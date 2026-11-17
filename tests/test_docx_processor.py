from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from docpicalign.models import AlignMode, BorderStyle, JobOptions
from docpicalign.processors.docx import PIC, WP, A, DocxProcessor, V, W

DOCUMENT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
 xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
 xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
 <w:body><w:tbl><w:tr><w:tc><w:tcPr/><w:p><w:r><w:drawing>
  <wp:inline distT="0" distB="0" distL="0" distR="0">
   <wp:extent cx="914400" cy="914400"/><wp:docPr id="1" name="Picture 1"/>
   <a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
    <pic:pic><pic:nvPicPr/><pic:blipFill><a:blip r:embed="rId1"/></pic:blipFill>
     <pic:spPr><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
    </pic:pic>
   </a:graphicData></a:graphic>
  </wp:inline>
 </w:drawing></w:r></w:p></w:tc></w:tr></w:tbl><w:sectPr/></w:body>
</w:document>"""

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="xml" ContentType="application/xml"/>
 <Default Extension="png" ContentType="image/png"/>
 <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

VML_DOCUMENT = """<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
 xmlns:v="urn:schemas-microsoft-com:vml" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
 <w:body><w:p><w:r><w:pict><v:shape id="v1" style="width:10pt;height:10pt"><v:imagedata r:id="rId2"/></v:shape></w:pict></w:r></w:p></w:body>
</w:document>"""

IGNORABLE_DOCUMENT = DOCUMENT.replace(
    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"',
    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
    ' xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"'
    ' xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" mc:Ignorable="w14"',
)


def make_docx(path: Path, document: str = DOCUMENT, media: bytes = b"fake-png") -> None:
    with zipfile.ZipFile(path, "w", allowZip64=True) as package:
        package.writestr("[Content_Types].xml", CONTENT_TYPES)
        package.writestr(
            "_rels/.rels",
            "<Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'/>",
        )
        package.writestr("word/document.xml", document)
        package.writestr("word/media/image1.png", media)


def read_part(path: Path, name: str = "word/document.xml") -> ET.Element:
    with zipfile.ZipFile(path) as package:
        return ET.fromstring(package.read(name))


class DocxProcessorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.source = self.folder / "source.docx"
        make_docx(self.source)
        self.processor = DocxProcessor()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_smart_mode_centers_paragraph_and_table_cell_and_adds_one_pt_border(self) -> None:
        output = self.folder / "smart.docx"
        result = self.processor.process(self.source, JobOptions(), output=output)
        self.assertTrue(result.success, result.error)
        self.assertEqual(result.pictures_found, 1)
        self.assertEqual(result.pictures_changed, 1)
        root = read_part(output)
        self.assertEqual(root.find(f".//{W}jc").get(f"{W}val"), "center")
        self.assertEqual(root.find(f".//{W}vAlign").get(f"{W}val"), "center")
        line = root.find(f".//{PIC}spPr/{A}ln")
        self.assertIsNotNone(line)
        self.assertEqual(line.get("w"), "12700")
        self.assertEqual(line.find(f"{A}solidFill/{A}srgbClr").get("val"), "000000")
        self.assertEqual(line.find(f"{A}prstDash").get("val"), "solid")

    def test_media_bytes_are_copied_without_changes(self) -> None:
        media = bytes(range(256)) * 16384
        make_docx(self.source, media=media)
        output = self.folder / "copied.docx"
        result = self.processor.process(self.source, JobOptions(), output=output)
        self.assertTrue(result.success, result.error)
        with zipfile.ZipFile(output) as package:
            self.assertEqual(package.read("word/media/image1.png"), media)

    def test_page_mode_converts_inline_picture_to_centered_anchor(self) -> None:
        output = self.folder / "page.docx"
        options = JobOptions(align_mode=AlignMode.PAGE)
        result = self.processor.process(self.source, options, output=output)
        self.assertTrue(result.success, result.error)
        root = read_part(output)
        self.assertIsNone(root.find(f".//{WP}inline"))
        anchor = root.find(f".//{WP}anchor")
        self.assertIsNotNone(anchor)
        self.assertEqual(anchor.find(f"{WP}positionH").get("relativeFrom"), "page")
        self.assertEqual(anchor.find(f"{WP}positionH/{WP}align").text, "center")
        self.assertEqual(anchor.find(f"{WP}positionV").get("relativeFrom"), "page")
        self.assertEqual(anchor.find(f"{WP}positionV/{WP}align").text, "center")

    def test_exact_width_and_height_resize_without_aspect_lock(self) -> None:
        output = self.folder / "exact-size.docx"
        result = self.processor.process(
            self.source,
            JobOptions(
                resize_width_mm=50,
                resize_height_mm=20,
                lock_aspect_ratio=False,
            ),
            output=output,
        )
        self.assertTrue(result.success, result.error)
        root = read_part(output)
        extent = root.find(f".//{WP}extent")
        shape_extent = root.find(f".//{PIC}spPr/{A}xfrm/{A}ext")
        self.assertEqual((extent.get("cx"), extent.get("cy")), ("1800000", "720000"))
        self.assertEqual(
            (shape_extent.get("cx"), shape_extent.get("cy")),
            ("1800000", "720000"),
        )

    def test_single_dimension_resize_preserves_aspect_ratio(self) -> None:
        output = self.folder / "ratio-size.docx"
        result = self.processor.process(
            self.source,
            JobOptions(resize_width_mm=50, lock_aspect_ratio=True),
            output=output,
        )
        self.assertTrue(result.success, result.error)
        extent = read_part(output).find(f".//{WP}extent")
        self.assertEqual((extent.get("cx"), extent.get("cy")), ("1800000", "1800000"))

    def test_aspect_locked_resize_fits_inside_width_and_height_box(self) -> None:
        output = self.folder / "fitted-size.docx"
        result = self.processor.process(
            self.source,
            JobOptions(
                resize_width_mm=40,
                resize_height_mm=20,
                lock_aspect_ratio=True,
            ),
            output=output,
        )
        self.assertTrue(result.success, result.error)
        extent = read_part(output).find(f".//{WP}extent")
        self.assertEqual((extent.get("cx"), extent.get("cy")), ("720000", "720000"))

    def test_custom_border_color_and_width(self) -> None:
        output = self.folder / "custom.docx"
        options = JobOptions(border=BorderStyle(2.5, "#1A2B3C"))
        result = self.processor.process(self.source, options, output=output)
        self.assertTrue(result.success, result.error)
        line = read_part(output).find(f".//{PIC}spPr/{A}ln")
        self.assertEqual(line.get("w"), str(round(2.5 * 12700)))
        self.assertEqual(line.find(f"{A}solidFill/{A}srgbClr").get("val"), "1A2B3C")

    def test_processing_twice_is_structurally_idempotent(self) -> None:
        first = self.folder / "first.docx"
        second = self.folder / "second.docx"
        self.assertTrue(self.processor.process(self.source, JobOptions(), output=first).success)
        self.assertTrue(self.processor.process(first, JobOptions(), output=second).success)
        root = read_part(second)
        self.assertEqual(len(root.findall(f".//{PIC}spPr/{A}ln")), 1)
        self.assertEqual(len(root.findall(f".//{W}pPr/{W}jc")), 1)
        self.assertEqual(len(root.findall(f".//{W}tcPr/{W}vAlign")), 1)

    def test_vml_picture_gets_border_and_page_position(self) -> None:
        make_docx(self.source, VML_DOCUMENT)
        output = self.folder / "vml.docx"
        result = self.processor.process(
            self.source, JobOptions(align_mode=AlignMode.PAGE), output=output
        )
        self.assertTrue(result.success, result.error)
        shape = read_part(output).find(f".//{V}shape")
        self.assertEqual(shape.get("strokeweight"), "1pt")
        self.assertEqual(shape.get("strokecolor"), "#000000")
        self.assertIn("mso-position-horizontal:center", shape.get("style"))
        self.assertIn("mso-position-vertical:center", shape.get("style"))

    def test_vml_picture_gets_exact_physical_size(self) -> None:
        make_docx(self.source, VML_DOCUMENT)
        output = self.folder / "vml-size.docx"
        result = self.processor.process(
            self.source,
            JobOptions(
                resize_width_mm=25.4,
                resize_height_mm=12.7,
                lock_aspect_ratio=False,
            ),
            output=output,
        )
        self.assertTrue(result.success, result.error)
        style = read_part(output).find(f".//{V}shape").get("style")
        self.assertIn("width:72pt", style)
        self.assertIn("height:36pt", style)

    def test_mc_ignorable_namespace_is_preserved(self) -> None:
        make_docx(self.source, IGNORABLE_DOCUMENT)
        output = self.folder / "ignorable.docx"
        result = self.processor.process(self.source, JobOptions(), output=output)
        self.assertTrue(result.success, result.error)
        with zipfile.ZipFile(output) as package:
            xml = package.read("word/document.xml")
        self.assertIn(b'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"', xml)
        ET.fromstring(xml)

    def test_invalid_package_returns_clear_error_and_no_output(self) -> None:
        broken = self.folder / "broken.docx"
        broken.write_bytes(b"not a zip")
        output = self.folder / "out.docx"
        result = self.processor.process(broken, JobOptions(), output=output)
        self.assertFalse(result.success)
        self.assertIn("손상", result.error)
        self.assertFalse(output.exists())

    def test_cancel_is_non_destructive(self) -> None:
        output = self.folder / "cancelled.docx"
        result = self.processor.process(
            self.source, JobOptions(), output=output, cancelled=lambda: True
        )
        self.assertFalse(result.success)
        self.assertIn("취소", result.error)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
