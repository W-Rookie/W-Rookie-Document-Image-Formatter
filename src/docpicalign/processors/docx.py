from __future__ import annotations

import contextlib
import io
import os
import re
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

from ..models import (
    AlignMode,
    CancelCheck,
    DocumentError,
    JobOptions,
    ProcessingCancelled,
    ProcessResult,
    ProgressCallback,
    fitted_dimensions,
)
from ..paths import output_path_for

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "v": "urn:schemas-microsoft-com:vml",
    "o": "urn:schemas-microsoft-com:office:office",
    "w10": "urn:schemas-microsoft-com:office:word",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    "wp14": "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
    "a14": "http://schemas.microsoft.com/office/drawing/2010/main",
}

for _prefix, _uri in NS.items():
    ET.register_namespace(_prefix, _uri)

W = f"{{{NS['w']}}}"
WP = f"{{{NS['wp']}}}"
A = f"{{{NS['a']}}}"
PIC = f"{{{NS['pic']}}}"
V = f"{{{NS['v']}}}"

MAX_XML_PART_BYTES = 512 * 1024 * 1024
MAX_ZIP_ENTRIES = 100_000


@dataclass(slots=True)
class _PartStats:
    found: int = 0
    changed: int = 0
    page_anchors: int = 0


class DocxProcessor:
    """Low-memory OOXML processor that never decodes embedded image binaries."""

    def process(
        self,
        source: Path,
        options: JobOptions,
        *,
        output: Path | None = None,
        progress: ProgressCallback | None = None,
        cancelled: CancelCheck | None = None,
    ) -> ProcessResult:
        source = source.resolve()
        output = (output or output_path_for(source, options)).resolve()
        result = ProcessResult(source=source, output=output)
        progress = progress or (lambda _value, _message: None)
        cancelled = cancelled or (lambda: False)

        if source.suffix.lower() != ".docx":
            result.error = "DOCX 파일이 아닙니다."
            return result
        if not source.is_file():
            result.error = "파일을 찾을 수 없습니다."
            return result

        output.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{output.stem}.", suffix=".tmp", dir=output.parent
        )
        os.close(fd)
        temporary = Path(temporary_name)
        try:
            stats = self._rewrite(source, temporary, options, progress, cancelled)
            if cancelled():
                raise ProcessingCancelled("사용자가 작업을 취소했습니다.")
            os.replace(temporary, output)
            result.pictures_found = stats.found
            result.pictures_changed = stats.changed
            if stats.found == 0:
                result.warnings.append("문서에서 그림 개체를 찾지 못했습니다.")
            if options.align_mode is AlignMode.PAGE and stats.page_anchors > 1:
                result.warnings.append(
                    "페이지 기준 배치는 같은 페이지의 여러 그림을 중앙에서 겹치게 할 수 있습니다."
                )
            progress(1.0, "저장 완료")
        except ProcessingCancelled as exc:
            result.error = str(exc)
        except (zipfile.BadZipFile, ET.ParseError) as exc:
            result.error = f"손상되었거나 지원하지 않는 DOCX입니다: {exc}"
        except DocumentError as exc:
            result.error = str(exc)
        except (OSError, ValueError) as exc:
            result.error = f"파일 처리 중 오류가 발생했습니다: {exc}"
        finally:
            with contextlib.suppress(OSError):
                temporary.unlink(missing_ok=True)
        return result

    def _rewrite(
        self,
        source: Path,
        temporary: Path,
        options: JobOptions,
        progress: ProgressCallback,
        cancelled: CancelCheck,
    ) -> _PartStats:
        total = _PartStats()
        with zipfile.ZipFile(source, "r") as src:
            names = set(src.namelist())
            if "[Content_Types].xml" not in names or "word/document.xml" not in names:
                raise DocumentError("유효한 Word DOCX 구조가 아닙니다.")
            infos = src.infolist()
            if len(infos) > MAX_ZIP_ENTRIES:
                raise DocumentError("DOCX 내부 항목 수가 안전 한도를 초과했습니다.")
            byte_total = max(1, sum(max(0, item.file_size) for item in infos))
            processed = 0
            with zipfile.ZipFile(
                temporary, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True
            ) as dst:
                dst.comment = src.comment
                for info in infos:
                    if cancelled():
                        raise ProcessingCancelled("사용자가 작업을 취소했습니다.")
                    self._validate_entry(info)
                    if self._should_format(info.filename, options):
                        if info.file_size > MAX_XML_PART_BYTES:
                            raise DocumentError(f"문서 XML이 비정상적으로 큽니다: {info.filename}")
                        data = src.read(info)
                        data, part = self._format_xml(data, options)
                        total.found += part.found
                        total.changed += part.changed
                        total.page_anchors += part.page_anchors
                        dst.writestr(info, data)
                        processed += max(0, info.file_size)
                    else:
                        # Streaming copy keeps large word/media entries out of RAM.
                        with (
                            src.open(info, "r") as read_handle,
                            dst.open(info, "w") as write_handle,
                        ):
                            since_update = 0
                            while chunk := read_handle.read(1024 * 1024):
                                if cancelled():
                                    raise ProcessingCancelled("사용자가 작업을 취소했습니다.")
                                write_handle.write(chunk)
                                processed += len(chunk)
                                since_update += len(chunk)
                                if since_update >= 8 * 1024 * 1024:
                                    progress(
                                        min(0.98, processed / byte_total),
                                        f"처리 중 · {info.filename}",
                                    )
                                    since_update = 0
                    progress(min(0.98, processed / byte_total), f"처리 중 · {info.filename}")
        return total

    @staticmethod
    def _validate_entry(info: zipfile.ZipInfo) -> None:
        normalized = info.filename.replace("\\", "/")
        if normalized.startswith("/") or any(part == ".." for part in normalized.split("/")):
            raise DocumentError("안전하지 않은 DOCX 내부 경로를 발견했습니다.")

    @staticmethod
    def _should_format(name: str, options: JobOptions) -> bool:
        if name == "word/document.xml":
            return True
        if not options.include_headers_footers:
            return False
        if not name.startswith("word/") or not name.endswith(".xml"):
            return False
        leaf = name.rsplit("/", 1)[-1]
        return leaf.startswith(("header", "footer")) or leaf in {
            "footnotes.xml",
            "endnotes.xml",
            "comments.xml",
        }

    def _format_xml(self, data: bytes, options: JobOptions) -> tuple[bytes, _PartStats]:
        upper = data.upper()
        if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
            raise DocumentError("DTD 또는 외부 엔터티가 포함된 XML은 처리하지 않습니다.")
        source_namespaces = self._source_namespaces(data)
        for prefix, uri in source_namespaces.items():
            if prefix != "xml" and not re.fullmatch(r"ns\d+", prefix):
                with contextlib.suppress(ValueError):
                    ET.register_namespace(prefix, uri)
        root = ET.fromstring(data)
        parents = {child: parent for parent in root.iter() for child in parent}
        stats = _PartStats()
        positioned: set[int] = set()

        for picture in list(root.iter(f"{PIC}pic")):
            stats.found += 1
            changed = self._set_drawingml_border(
                picture, options.border.width_pt, options.border.color
            )
            paragraph = self._ancestor(picture, parents, f"{W}p")
            cell = self._ancestor(picture, parents, f"{W}tc")
            if paragraph is not None:
                changed |= self._center_paragraph(paragraph)
            if cell is not None and options.align_mode is AlignMode.SMART:
                changed |= self._center_cell(cell)
            frame = self._frame_ancestor(picture, parents)
            if frame is not None:
                changed |= self._resize_drawingml(picture, frame, options)
            if (
                options.align_mode is AlignMode.PAGE
                and frame is not None
                and id(frame) not in positioned
            ):
                changed |= self._center_frame_on_page(frame, parents)
                positioned.add(id(frame))
                stats.page_anchors += 1
            if changed:
                stats.changed += 1

        for image_data in list(root.iter(f"{V}imagedata")):
            stats.found += 1
            changed = False
            shape = self._ancestor(image_data, parents, f"{V}shape")
            if shape is not None:
                changed |= self._set_vml_border(
                    shape, options.border.width_pt, options.border.color
                )
                changed |= self._resize_vml(shape, options)
                if options.align_mode is AlignMode.PAGE:
                    changed |= self._center_vml_on_page(shape)
                    stats.page_anchors += 1
            paragraph = self._ancestor(image_data, parents, f"{W}p")
            cell = self._ancestor(image_data, parents, f"{W}tc")
            if paragraph is not None:
                changed |= self._center_paragraph(paragraph)
            if cell is not None and options.align_mode is AlignMode.SMART:
                changed |= self._center_cell(cell)
            if changed:
                stats.changed += 1

        if stats.found == 0:
            return data, stats
        self._preserve_ignorable_prefixes(root, source_namespaces)
        declaration = b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        return declaration + ET.tostring(root, encoding="utf-8"), stats

    @staticmethod
    def _source_namespaces(data: bytes) -> dict[str, str]:
        namespaces: dict[str, str] = {}
        try:
            for _event, (prefix, uri) in ET.iterparse(io.BytesIO(data), events=("start-ns",)):
                namespaces[prefix or ""] = uri
        except ET.ParseError:
            return namespaces
        return namespaces

    @staticmethod
    def _preserve_ignorable_prefixes(root: ET.Element, source_namespaces: dict[str, str]) -> None:
        ignorable = root.get(f"{{{NS['mc']}}}Ignorable", "").split()
        if not ignorable:
            return
        used_uris: set[str] = set()
        for element in root.iter():
            for name in (element.tag, *element.attrib):
                if isinstance(name, str) and name.startswith("{"):
                    used_uris.add(name[1:].split("}", 1)[0])
        for prefix in ignorable:
            uri = source_namespaces.get(prefix)
            if uri and uri not in used_uris:
                root.set(f"xmlns:{prefix}", uri)

    @staticmethod
    def _ancestor(
        element: ET.Element, parents: dict[ET.Element, ET.Element], tag: str
    ) -> ET.Element | None:
        current = element
        while current in parents:
            current = parents[current]
            if current.tag == tag:
                return current
        return None

    @staticmethod
    def _frame_ancestor(
        element: ET.Element, parents: dict[ET.Element, ET.Element]
    ) -> ET.Element | None:
        current = element
        while current in parents:
            current = parents[current]
            if current.tag in {f"{WP}inline", f"{WP}anchor"}:
                return current
        return None

    @staticmethod
    def _center_paragraph(paragraph: ET.Element) -> bool:
        ppr = paragraph.find(f"{W}pPr")
        if ppr is None:
            ppr = ET.Element(f"{W}pPr")
            paragraph.insert(0, ppr)
        jc = ppr.find(f"{W}jc")
        if jc is None:
            jc = ET.SubElement(ppr, f"{W}jc")
        key = f"{W}val"
        changed = jc.get(key) != "center"
        jc.set(key, "center")
        return changed

    @staticmethod
    def _center_cell(cell: ET.Element) -> bool:
        tcpr = cell.find(f"{W}tcPr")
        if tcpr is None:
            tcpr = ET.Element(f"{W}tcPr")
            cell.insert(0, tcpr)
        valign = tcpr.find(f"{W}vAlign")
        if valign is None:
            valign = ET.SubElement(tcpr, f"{W}vAlign")
        key = f"{W}val"
        changed = valign.get(key) != "center"
        valign.set(key, "center")
        return changed

    @staticmethod
    def _set_drawingml_border(picture: ET.Element, width_pt: float, color: str) -> bool:
        sppr = picture.find(f"{PIC}spPr")
        if sppr is None:
            sppr = ET.SubElement(picture, f"{PIC}spPr")
            geometry = ET.SubElement(sppr, f"{A}prstGeom", {"prst": "rect"})
            ET.SubElement(geometry, f"{A}avLst")
        line = sppr.find(f"{A}ln")
        if line is None:
            line = ET.SubElement(sppr, f"{A}ln")
        width_emu = str(round(width_pt * 12700))
        signature_before = ET.tostring(line, encoding="unicode")
        line.set("w", width_emu)
        for child in list(line):
            if child.tag in {
                f"{A}noFill",
                f"{A}solidFill",
                f"{A}gradFill",
                f"{A}pattFill",
                f"{A}prstDash",
                f"{A}custDash",
            }:
                line.remove(child)
        solid = ET.Element(f"{A}solidFill")
        ET.SubElement(solid, f"{A}srgbClr", {"val": color})
        dash = ET.Element(f"{A}prstDash", {"val": "solid"})
        line.insert(0, solid)
        line.insert(1, dash)
        return signature_before != ET.tostring(line, encoding="unicode")

    @staticmethod
    def _set_vml_border(shape: ET.Element, width_pt: float, color: str) -> bool:
        before = (shape.get("stroked"), shape.get("strokecolor"), shape.get("strokeweight"))
        shape.set("stroked", "t")
        shape.set("strokecolor", f"#{color}")
        shape.set("strokeweight", f"{width_pt:g}pt")
        return before != ("t", f"#{color}", f"{width_pt:g}pt")

    def _resize_drawingml(
        self, picture: ET.Element, frame: ET.Element, options: JobOptions
    ) -> bool:
        if options.resize_width_mm is None and options.resize_height_mm is None:
            return False
        extent = frame.find(f"{WP}extent")
        shape_extent = picture.find(f"{PIC}spPr/{A}xfrm/{A}ext")
        source = extent if extent is not None else shape_extent
        if source is None:
            return False
        try:
            original_width = float(source.get("cx", "0"))
            original_height = float(source.get("cy", "0"))
        except ValueError:
            return False
        if original_width <= 0 or original_height <= 0:
            return False
        width, height = fitted_dimensions(
            original_width,
            original_height,
            options.resize_width_mm * 36000 if options.resize_width_mm is not None else None,
            options.resize_height_mm * 36000 if options.resize_height_mm is not None else None,
            options.lock_aspect_ratio,
        )
        new_width = str(round(width))
        new_height = str(round(height))
        before = (
            extent.get("cx") if extent is not None else None,
            extent.get("cy") if extent is not None else None,
            shape_extent.get("cx") if shape_extent is not None else None,
            shape_extent.get("cy") if shape_extent is not None else None,
        )
        if extent is not None:
            extent.set("cx", new_width)
            extent.set("cy", new_height)
        if shape_extent is None:
            sppr = picture.find(f"{PIC}spPr")
            if sppr is not None:
                xfrm = sppr.find(f"{A}xfrm")
                if xfrm is None:
                    xfrm = ET.Element(f"{A}xfrm")
                    sppr.insert(0, xfrm)
                    ET.SubElement(xfrm, f"{A}off", {"x": "0", "y": "0"})
                shape_extent = ET.SubElement(xfrm, f"{A}ext")
        if shape_extent is not None:
            shape_extent.set("cx", new_width)
            shape_extent.set("cy", new_height)
        after = (
            extent.get("cx") if extent is not None else None,
            extent.get("cy") if extent is not None else None,
            shape_extent.get("cx") if shape_extent is not None else None,
            shape_extent.get("cy") if shape_extent is not None else None,
        )
        return before != after

    def _resize_vml(self, shape: ET.Element, options: JobOptions) -> bool:
        if options.resize_width_mm is None and options.resize_height_mm is None:
            return False
        parts = self._vml_style_parts(shape)
        original_width = self._css_length_points(parts.get("width"))
        original_height = self._css_length_points(parts.get("height"))
        target_width = (
            options.resize_width_mm * 72 / 25.4 if options.resize_width_mm is not None else None
        )
        target_height = (
            options.resize_height_mm * 72 / 25.4 if options.resize_height_mm is not None else None
        )
        if original_width is not None and original_height is not None:
            width, height = fitted_dimensions(
                original_width,
                original_height,
                target_width,
                target_height,
                options.lock_aspect_ratio,
            )
            parts["width"] = f"{width:.6g}pt"
            parts["height"] = f"{height:.6g}pt"
        else:
            if target_width is not None:
                parts["width"] = f"{target_width:.6g}pt"
            if target_height is not None:
                parts["height"] = f"{target_height:.6g}pt"
        before = shape.get("style", "")
        shape.set("style", self._serialize_vml_style(parts))
        return before != shape.get("style", "")

    @staticmethod
    def _css_length_points(value: str | None) -> float | None:
        if not value:
            return None
        match = re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)\s*(pt|px|in|cm|mm)?\s*", value)
        if not match:
            return None
        number = float(match.group(1))
        unit = match.group(2) or "pt"
        factors = {"pt": 1.0, "px": 0.75, "in": 72.0, "cm": 72 / 2.54, "mm": 72 / 25.4}
        return number * factors[unit]

    @staticmethod
    def _vml_style_parts(shape: ET.Element) -> dict[str, str]:
        parts: dict[str, str] = {}
        for declaration in shape.get("style", "").split(";"):
            if ":" in declaration:
                key, value = declaration.split(":", 1)
                parts[key.strip()] = value.strip()
        return parts

    @staticmethod
    def _serialize_vml_style(parts: dict[str, str]) -> str:
        return ";".join(f"{key}:{value}" for key, value in parts.items())

    def _center_frame_on_page(
        self, frame: ET.Element, parents: dict[ET.Element, ET.Element]
    ) -> bool:
        if frame.tag == f"{WP}inline":
            parent = parents.get(frame)
            if parent is None:
                return False
            index = list(parent).index(frame)
            anchor = ET.Element(
                f"{WP}anchor",
                {
                    "distT": frame.get("distT", "0"),
                    "distB": frame.get("distB", "0"),
                    "distL": frame.get("distL", "0"),
                    "distR": frame.get("distR", "0"),
                    "simplePos": "0",
                    "relativeHeight": "0",
                    "behindDoc": "0",
                    "locked": "0",
                    "layoutInCell": "1",
                    "allowOverlap": "1",
                },
            )
            ET.SubElement(anchor, f"{WP}simplePos", {"x": "0", "y": "0"})
            self._append_page_positions(anchor)
            extent = frame.find(f"{WP}extent")
            effect = frame.find(f"{WP}effectExtent")
            if extent is not None:
                anchor.append(extent)
            if effect is not None:
                anchor.append(effect)
            ET.SubElement(anchor, f"{WP}wrapNone")
            for child in list(frame):
                if child.tag not in {f"{WP}extent", f"{WP}effectExtent"}:
                    anchor.append(child)
            parent.remove(frame)
            parent.insert(index, anchor)
            return True

        for tag in (f"{WP}positionH", f"{WP}positionV"):
            old = frame.find(tag)
            if old is not None:
                frame.remove(old)
        insert_at = 1 if frame.find(f"{WP}simplePos") is not None else 0
        horizontal, vertical = self._new_page_positions()
        frame.insert(insert_at, horizontal)
        frame.insert(insert_at + 1, vertical)
        return True

    @staticmethod
    def _new_page_positions() -> tuple[ET.Element, ET.Element]:
        horizontal = ET.Element(f"{WP}positionH", {"relativeFrom": "page"})
        ET.SubElement(horizontal, f"{WP}align").text = "center"
        vertical = ET.Element(f"{WP}positionV", {"relativeFrom": "page"})
        ET.SubElement(vertical, f"{WP}align").text = "center"
        return horizontal, vertical

    def _append_page_positions(self, anchor: ET.Element) -> None:
        horizontal, vertical = self._new_page_positions()
        anchor.append(horizontal)
        anchor.append(vertical)

    @staticmethod
    def _center_vml_on_page(shape: ET.Element) -> bool:
        updates = {
            "position": "absolute",
            "mso-position-horizontal": "center",
            "mso-position-horizontal-relative": "page",
            "mso-position-vertical": "center",
            "mso-position-vertical-relative": "page",
        }
        parts = DocxProcessor._vml_style_parts(shape)
        before = dict(parts)
        parts.update(updates)
        shape.set("style", DocxProcessor._serialize_vml_style(parts))
        return before != parts
