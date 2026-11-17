from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from test_docx_processor import DOCUMENT, make_docx

from docpicalign.models import JobOptions
from docpicalign.security import RiskLevel, SecurityScanner
from docpicalign.service import ProcessingService

RELATIONSHIPS = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId9" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" TargetMode="External" Target="{target}"/>
</Relationships>"""


class SecurityScannerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.scanner = SecurityScanner()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_clean_docx_passes(self) -> None:
        path = self.folder / "clean.docx"
        make_docx(path)
        report = self.scanner.scan(path, use_windows_defender=False)
        self.assertFalse(report.blocked, report.findings)
        self.assertEqual(report.status_text, "정상")

    def test_macro_payload_is_blocked(self) -> None:
        path = self.folder / "macro.docx"
        make_docx(path)
        with zipfile.ZipFile(path, "a") as package:
            package.writestr("word/vbaProject.bin", b"macro")
        report = self.scanner.scan(path, use_windows_defender=False)
        self.assertTrue(report.blocked)
        self.assertIn("macro_payload", {item.code for item in report.blocks})

    def test_path_traversal_is_blocked(self) -> None:
        path = self.folder / "traversal.docx"
        make_docx(path)
        with zipfile.ZipFile(path, "a") as package:
            package.writestr("word/../../evil.exe", b"MZ")
        report = self.scanner.scan(path, use_windows_defender=False)
        codes = {item.code for item in report.blocks}
        self.assertIn("unsafe_path", codes)
        self.assertIn("executable_payload", codes)

    def test_activex_and_ole_are_blocked(self) -> None:
        path = self.folder / "active.docx"
        make_docx(path)
        with zipfile.ZipFile(path, "a") as package:
            package.writestr("word/activeX/activeX1.bin", b"payload")
            package.writestr("word/embeddings/oleObject1.bin", b"payload")
        report = self.scanner.scan(path, use_windows_defender=False)
        self.assertTrue(report.blocked)
        self.assertIn("active_content", {item.code for item in report.blocks})

    def test_normal_external_link_warns_but_does_not_block(self) -> None:
        path = self.folder / "link.docx"
        make_docx(path)
        with zipfile.ZipFile(path, "a") as package:
            package.writestr(
                "word/_rels/document.xml.rels",
                RELATIONSHIPS.format(target="https://example.com"),
            )
        report = self.scanner.scan(path, use_windows_defender=False)
        self.assertFalse(report.blocked, report.findings)
        self.assertIn("external_link", {item.code for item in report.warnings})

    def test_file_scheme_external_link_is_blocked(self) -> None:
        path = self.folder / "dangerous-link.docx"
        make_docx(path)
        with zipfile.ZipFile(path, "a") as package:
            package.writestr(
                "word/_rels/document.xml.rels",
                RELATIONSHIPS.format(target="file:///C:/Windows/System32/calc.exe"),
            )
        report = self.scanner.scan(path, use_windows_defender=False)
        self.assertTrue(report.blocked)
        self.assertIn("dangerous_external_link", {item.code for item in report.blocks})

    def test_dtd_and_entity_xml_is_blocked(self) -> None:
        path = self.folder / "entity.docx"
        unsafe = DOCUMENT.replace(
            "<w:document xmlns:w=",
            '<!DOCTYPE x [<!ENTITY payload "boom">]><w:document xmlns:w=',
        )
        make_docx(path, unsafe)
        report = self.scanner.scan(path, use_windows_defender=False)
        self.assertTrue(report.blocked)
        self.assertIn("xml_entity", {item.code for item in report.blocks})

    def test_hwp_script_indicator_is_blocked(self) -> None:
        path = self.folder / "script.hwp"
        path.write_bytes(
            SecurityScanner.OLE_PREFIX + b"\x00" * 512 + "DefaultJScript".encode("utf-16le")
        )
        report = self.scanner.scan(path, use_windows_defender=False)
        self.assertTrue(report.blocked)
        self.assertIn("hwp_script", {item.code for item in report.blocks})

    def test_service_does_not_process_blocked_document(self) -> None:
        path = self.folder / "blocked.docx"
        make_docx(path)
        with zipfile.ZipFile(path, "a") as package:
            package.writestr("word/vbaProject.bin", b"macro")
        result = ProcessingService().process_one(path, JobOptions())
        self.assertFalse(result.success)
        self.assertIn("보안 검사에서 차단", result.error)
        self.assertIsNone(result.output)

    def test_report_levels_are_orderable(self) -> None:
        self.assertGreater(RiskLevel.BLOCKED, RiskLevel.WARNING)


if __name__ == "__main__":
    unittest.main()
