from __future__ import annotations

import contextlib
import os
import tempfile
from pathlib import Path
from typing import Any

from ..models import (
    AlignMode,
    CancelCheck,
    JobOptions,
    ProcessingCancelled,
    ProcessResult,
    ProgressCallback,
    fitted_dimensions,
)
from ..paths import output_path_for


class HwpProcessor:
    """HWP/HWPX processor using Hancom's official Windows automation object."""

    PICTURE_LABELS = {"그림", "사진", "picture", "image"}
    HWP_WIDTHS_MM = (
        0.1,
        0.12,
        0.15,
        0.2,
        0.25,
        0.3,
        0.4,
        0.5,
        0.6,
        0.7,
        1.0,
        1.5,
        2.0,
        3.0,
        4.0,
        5.0,
    )

    @staticmethod
    def diagnostic() -> tuple[bool, str]:
        if os.name != "nt":
            return False, "HWP 자동화는 Windows에서만 사용할 수 있습니다."
        try:
            import pythoncom
            import win32com.client
        except ImportError:
            return False, "pywin32가 없습니다. 'pip install pywin32'를 실행하세요."
        hwp = None
        try:
            pythoncom.CoInitialize()
            hwp = win32com.client.DispatchEx("HWPFrame.HwpObject")
            hwp.Quit()
            hwp = None
        except Exception as exc:
            return False, f"한/글 자동화 개체를 열 수 없습니다: {exc}"
        finally:
            if hwp is not None:
                with contextlib.suppress(Exception):
                    hwp.Quit()
            with contextlib.suppress(Exception):
                pythoncom.CoUninitialize()
        return True, "한/글 자동화 연결 정상"

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

        if source.suffix.lower() not in {".hwp", ".hwpx"}:
            result.error = "HWP 또는 HWPX 파일이 아닙니다."
            return result
        if not source.is_file():
            result.error = "파일을 찾을 수 없습니다."
            return result
        if os.name != "nt":
            result.error = "HWP 자동화는 Windows에서만 사용할 수 있습니다."
            return result

        output.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary_name = tempfile.mkstemp(
            prefix=f".{output.stem}.", suffix=source.suffix.lower(), dir=output.parent
        )
        os.close(fd)
        temporary = Path(temporary_name)
        temporary.unlink(missing_ok=True)

        hwp: Any | None = None
        pythoncom: Any | None = None
        document_open = False
        try:
            import pythoncom as _pythoncom
            import win32com.client

            pythoncom = _pythoncom
            pythoncom.CoInitialize()
            hwp = win32com.client.DispatchEx("HWPFrame.HwpObject")
            with contextlib.suppress(Exception):
                hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
                # The optional Hancom security module is not installed everywhere.
            with contextlib.suppress(Exception):
                hwp.XHwpWindows.Item(0).Visible = bool(options.hwp_visible)

            progress(0.02, "한/글에서 문서 여는 중")
            opened = hwp.Open(str(source), "", "forceopen:true;suspendpassword:true")
            if opened is False:
                raise RuntimeError("한/글이 문서를 열지 못했습니다.")
            document_open = True
            controls = self._picture_controls(hwp)
            result.pictures_found = len(controls)

            actual_width = self._nearest_hwp_width(options.border.width_pt)
            requested_mm = options.border.width_pt * 25.4 / 72.0
            if abs(actual_width - requested_mm) > 0.015:
                result.warnings.append(
                    f"한/글의 지원 두께에 맞춰 {actual_width:g}mm로 적용했습니다."
                )
            total = max(1, len(controls))
            for index, ctrl in enumerate(controls, 1):
                if cancelled():
                    raise ProcessingCancelled("사용자가 작업을 취소했습니다.")
                self._format_picture(hwp, ctrl, options, actual_width)
                result.pictures_changed += 1
                progress(0.05 + 0.85 * index / total, f"그림 {index}/{len(controls)} 처리")

            if cancelled():
                raise ProcessingCancelled("사용자가 작업을 취소했습니다.")
            format_name = "HWPX" if source.suffix.lower() == ".hwpx" else "HWP"
            progress(0.92, "한/글 문서 저장 중")
            saved = hwp.SaveAs(str(temporary), format_name, "lock:false")
            if saved is False or not temporary.is_file():
                raise RuntimeError("한/글이 결과 파일을 저장하지 못했습니다.")
            hwp.Clear(1)
            document_open = False
            hwp.Quit()
            hwp = None
            os.replace(temporary, output)
            if result.pictures_found == 0:
                result.warnings.append("문서에서 그림 개체를 찾지 못했습니다.")
            if options.align_mode is AlignMode.PAGE and result.pictures_found > 1:
                result.warnings.append(
                    "페이지 기준 배치는 같은 페이지의 여러 그림을 중앙에서 겹치게 할 수 있습니다."
                )
            progress(1.0, "저장 완료")
        except ProcessingCancelled as exc:
            result.error = str(exc)
        except Exception as exc:
            result.error = f"한/글 처리 중 오류가 발생했습니다: {exc}"
        finally:
            if hwp is not None:
                with contextlib.suppress(Exception):
                    if document_open:
                        hwp.Clear(1)
                    hwp.Quit()
            if pythoncom is not None:
                with contextlib.suppress(Exception):
                    pythoncom.CoUninitialize()
            with contextlib.suppress(OSError):
                temporary.unlink(missing_ok=True)
        return result

    def _picture_controls(self, hwp: Any) -> list[Any]:
        pictures: list[Any] = []
        ctrl = hwp.HeadCtrl
        while ctrl is not None:
            try:
                ctrl_id = str(ctrl.CtrlID).strip().lower()
                description = str(getattr(ctrl, "UserDesc", "")).strip().lower()
                if ctrl_id == "gso" and any(label in description for label in self.PICTURE_LABELS):
                    pictures.append(ctrl)
            except Exception:
                pass
            ctrl = ctrl.Next
        return pictures

    def _format_picture(self, hwp: Any, ctrl: Any, options: JobOptions, width_mm: float) -> None:
        anchor = ctrl.GetAnchorPos(0)
        hwp.SetPosBySet(anchor)

        # For inline pictures this centers the containing paragraph. Outside a
        # table TableVAlignCenter simply returns false and is safe to ignore.
        hwp.HAction.Run("ParagraphShapeAlignCenter")
        if options.align_mode is AlignMode.SMART:
            with contextlib.suppress(Exception):
                hwp.HAction.Run("TableVAlignCenter")

        hwp.SetPosBySet(anchor)
        if hwp.FindCtrl() is False:
            raise RuntimeError("그림 개체를 선택하지 못했습니다.")
        shape = hwp.HParameterSet.HShapeObject
        hwp.HAction.GetDefault("ShapeObjDialog", shape.HSet)

        if options.align_mode is AlignMode.PAGE:
            self._set_item(shape.HSet, "TreatAsChar", 0)
            self._set_item(shape.HSet, "HorzRelTo", 1)  # page
            self._set_item(shape.HSet, "VertRelTo", 1)  # page
            self._set_item(shape.HSet, "HorzAlign", 1)  # center
            self._set_item(shape.HSet, "VertAlign", 1)  # center
            self._set_item(shape.HSet, "HorzOffset", 0)
            self._set_item(shape.HSet, "VertOffset", 0)
            self._set_item(shape.HSet, "AllowOverlap", 1)

        self._apply_picture_size(hwp, shape.HSet, options)

        line = shape.HSet.CreateItemSet("ShapeDrawLineAttr", "DrawLineAttr")
        self._set_item(line, "Style", self._enum(hwp, "HwpLineType", "Solid", 1))
        red = int(options.border.color[0:2], 16)
        green = int(options.border.color[2:4], 16)
        blue = int(options.border.color[4:6], 16)
        try:
            color_value = hwp.RGBColor(red, green, blue)
        except Exception:
            color_value = red | (green << 8) | (blue << 16)
        self._set_item(line, "Color", color_value)
        label = f"{width_mm:g}mm"
        fallback = self.HWP_WIDTHS_MM.index(width_mm)
        self._set_item(line, "Width", self._enum(hwp, "HwpLineWidth", label, fallback))

        if hwp.HAction.Execute("ShapeObjDialog", shape.HSet) is False:
            raise RuntimeError("그림 속성을 적용하지 못했습니다.")
        with contextlib.suppress(Exception):
            hwp.HAction.Run("Cancel")

    @staticmethod
    def _set_item(target: Any, name: str, value: Any) -> None:
        try:
            target.SetItem(name, value)
        except Exception:
            setattr(target, name, value)

    def _apply_picture_size(self, hwp: Any, target: Any, options: JobOptions) -> None:
        if options.resize_width_mm is None and options.resize_height_mm is None:
            return
        width = self._mm_to_hwp_unit(hwp, options.resize_width_mm)
        height = self._mm_to_hwp_unit(hwp, options.resize_height_mm)
        original_width = self._get_item(target, "Width")
        original_height = self._get_item(target, "Height")
        if (
            options.lock_aspect_ratio
            and original_width is not None
            and original_height is not None
            and original_width > 0
            and original_height > 0
        ):
            width, height = fitted_dimensions(
                float(original_width),
                float(original_height),
                width,
                height,
                True,
            )
        self._set_item(target, "KeepAspectRatio", 1 if options.lock_aspect_ratio else 0)
        if width is not None:
            self._set_item(target, "Width", round(width))
        if height is not None:
            self._set_item(target, "Height", round(height))

    @staticmethod
    def _mm_to_hwp_unit(hwp: Any, value_mm: float | None) -> float | None:
        if value_mm is None:
            return None
        try:
            return float(hwp.MiliToHwpUnit(value_mm))
        except Exception:
            return value_mm * 7200 / 25.4

    @staticmethod
    def _get_item(target: Any, name: str) -> float | None:
        try:
            return float(target.Item(name))
        except Exception:
            pass
        try:
            return float(getattr(target, name))
        except Exception:
            pass
        try:
            return float(target.values[name])
        except Exception:
            return None

    @staticmethod
    def _enum(hwp: Any, method: str, label: str, fallback: int) -> int:
        try:
            return int(getattr(hwp, method)(label))
        except Exception:
            return fallback

    def _nearest_hwp_width(self, width_pt: float) -> float:
        requested = width_pt * 25.4 / 72.0
        return min(self.HWP_WIDTHS_MM, key=lambda value: abs(value - requested))
