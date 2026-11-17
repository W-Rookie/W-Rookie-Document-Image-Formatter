from __future__ import annotations

import contextlib
import os
import re
import subprocess
import zipfile
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

import olefile
from defusedxml import ElementTree as SafeET
from defusedxml.common import DefusedXmlException


class RiskLevel(IntEnum):
    INFO = 0
    WARNING = 1
    BLOCKED = 2


@dataclass(frozen=True, slots=True)
class SecurityFinding:
    level: RiskLevel
    code: str
    message: str
    entry: str | None = None


@dataclass(slots=True)
class SecurityReport:
    path: Path
    findings: list[SecurityFinding] = field(default_factory=list)
    scanner_name: str = "W-Rookie 정적 검사"

    @property
    def blocked(self) -> bool:
        return any(item.level is RiskLevel.BLOCKED for item in self.findings)

    @property
    def warnings(self) -> list[SecurityFinding]:
        return [item for item in self.findings if item.level is RiskLevel.WARNING]

    @property
    def blocks(self) -> list[SecurityFinding]:
        return [item for item in self.findings if item.level is RiskLevel.BLOCKED]

    @property
    def status_text(self) -> str:
        if self.blocked:
            return "위험 요소 차단"
        if self.warnings:
            return "경고 있음"
        return "정상"


SecurityProgress = Callable[[float, str], None]


class SecurityScanner:
    """Conservative preflight scanner for untrusted office documents.

    This is defense in depth, not a replacement for a current operating-system
    antivirus or fully patched office applications.
    """

    MAX_ENTRIES = 100_000
    MAX_XML_BYTES = 512 * 1024 * 1024
    MAX_TOTAL_XML_BYTES = 1024 * 1024 * 1024
    MAX_TOTAL_UNCOMPRESSED = 64 * 1024 * 1024 * 1024
    ZIP_BOMB_ENTRY_MIN = 100 * 1024 * 1024
    ZIP_BOMB_ENTRY_RATIO = 1_000
    ZIP_BOMB_TOTAL_MIN = 2 * 1024 * 1024 * 1024
    ZIP_BOMB_TOTAL_RATIO = 500
    MAX_RELATIONSHIP_BYTES = 8 * 1024 * 1024

    DANGEROUS_EXTENSIONS = {
        ".ade",
        ".adp",
        ".app",
        ".bat",
        ".chm",
        ".cmd",
        ".com",
        ".cpl",
        ".dll",
        ".exe",
        ".hta",
        ".inf",
        ".ins",
        ".iso",
        ".jar",
        ".js",
        ".jse",
        ".lnk",
        ".mde",
        ".msc",
        ".msi",
        ".msp",
        ".mst",
        ".pif",
        ".ps1",
        ".reg",
        ".scr",
        ".sct",
        ".shb",
        ".sys",
        ".vbe",
        ".vbs",
        ".wsf",
        ".wsh",
    }
    DANGEROUS_SCHEMES = {
        "data",
        "file",
        "javascript",
        "mhtml",
        "ms-msdt",
        "powershell",
        "shell",
        "vbscript",
    }
    OLE_PREFIX = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"

    def scan(
        self,
        path: Path,
        *,
        use_windows_defender: bool = True,
        progress: SecurityProgress | None = None,
    ) -> SecurityReport:
        path = path.resolve()
        progress = progress or (lambda _value, _message: None)
        report = SecurityReport(path=path)
        progress(0.02, "파일 형식 확인")

        if not path.is_file():
            self._add(report, RiskLevel.BLOCKED, "file_missing", "파일을 찾을 수 없습니다.")
            return report
        try:
            if path.stat().st_size == 0:
                self._add(report, RiskLevel.BLOCKED, "empty_file", "빈 파일입니다.")
                return report
        except OSError as exc:
            self._add(report, RiskLevel.BLOCKED, "file_access", f"파일을 읽을 수 없습니다: {exc}")
            return report

        suffix = path.suffix.lower()
        if suffix == ".docx":
            self._scan_zip_document(path, report, document_kind="docx", progress=progress)
        elif suffix == ".hwpx":
            self._scan_zip_document(path, report, document_kind="hwpx", progress=progress)
        elif suffix == ".hwp":
            self._scan_hwp(path, report, progress)
        else:
            self._add(
                report,
                RiskLevel.BLOCKED,
                "unsupported_extension",
                "지원하지 않는 파일 확장자입니다.",
            )

        if not report.blocked and use_windows_defender:
            progress(0.75, "Windows Defender 검사")
            self._scan_with_windows_defender(path, report)
        progress(1.0, report.status_text)
        return report

    def _scan_zip_document(
        self,
        path: Path,
        report: SecurityReport,
        *,
        document_kind: str,
        progress: SecurityProgress,
    ) -> None:
        try:
            with zipfile.ZipFile(path, "r") as package:
                infos = package.infolist()
                names = [info.filename.replace("\\", "/") for info in infos]
                name_set = set(names)
                if document_kind == "docx" and not {
                    "[Content_Types].xml",
                    "word/document.xml",
                }.issubset(name_set):
                    self._add(
                        report,
                        RiskLevel.BLOCKED,
                        "invalid_docx",
                        "정상적인 DOCX 구조가 아닙니다.",
                    )
                if document_kind == "hwpx" and "mimetype" not in name_set:
                    self._add(
                        report,
                        RiskLevel.WARNING,
                        "hwpx_mimetype_missing",
                        "HWPX mimetype 항목이 없습니다. 한/글에서 다시 저장하는 것을 권장합니다.",
                    )

                if len(infos) > self.MAX_ENTRIES:
                    self._add(
                        report,
                        RiskLevel.BLOCKED,
                        "too_many_entries",
                        f"압축 내부 항목이 안전 한도({self.MAX_ENTRIES:,}개)를 초과합니다.",
                    )

                total_size = 0
                total_compressed = 0
                total_xml = 0
                seen: set[str] = set()
                xml_entries: list[zipfile.ZipInfo] = []
                relationship_entries: list[zipfile.ZipInfo] = []

                for index, (info, normalized) in enumerate(zip(infos, names, strict=True)):
                    if index % 250 == 0:
                        progress(0.05 + 0.5 * index / max(1, len(infos)), "압축 구조 검사")
                    total_size += max(0, info.file_size)
                    total_compressed += max(0, info.compress_size)
                    self._inspect_entry(info, normalized, report, seen)
                    lower = normalized.lower()
                    if lower.endswith((".xml", ".rels")):
                        total_xml += max(0, info.file_size)
                        xml_entries.append(info)
                    if lower.endswith(".rels"):
                        relationship_entries.append(info)

                if total_size > self.MAX_TOTAL_UNCOMPRESSED:
                    self._add(
                        report,
                        RiskLevel.BLOCKED,
                        "uncompressed_size_limit",
                        "압축 해제 예상 크기가 64GB 안전 한도를 초과합니다.",
                    )
                if total_xml > self.MAX_TOTAL_XML_BYTES:
                    self._add(
                        report,
                        RiskLevel.BLOCKED,
                        "xml_size_limit",
                        "문서 XML 총크기가 1GB 안전 한도를 초과합니다.",
                    )
                total_ratio = total_size / max(1, total_compressed)
                if (
                    total_size >= self.ZIP_BOMB_TOTAL_MIN
                    and total_ratio > self.ZIP_BOMB_TOTAL_RATIO
                ):
                    self._add(
                        report,
                        RiskLevel.BLOCKED,
                        "zip_bomb_ratio",
                        "압축률이 비정상적으로 높아 ZIP 폭탄 가능성이 있습니다.",
                    )

                self._inspect_special_entries(document_kind, names, report)
                if document_kind == "docx" and "[Content_Types].xml" in name_set:
                    try:
                        content_types = package.read("[Content_Types].xml").lower()
                        if b"macroenabled" in content_types or b"vbaproject" in content_types:
                            self._add(
                                report,
                                RiskLevel.BLOCKED,
                                "macro_content_type",
                                "매크로 사용 콘텐츠 형식이 선언되어 있습니다.",
                                "[Content_Types].xml",
                            )
                    except (OSError, RuntimeError, zipfile.BadZipFile):
                        pass
                self._inspect_xml(package, xml_entries, report, progress)
                self._inspect_relationships(package, relationship_entries, report)
        except zipfile.BadZipFile:
            self._add(
                report,
                RiskLevel.BLOCKED,
                "invalid_zip",
                "손상되었거나 정상적인 ZIP 기반 문서가 아닙니다.",
            )
        except (OSError, RuntimeError) as exc:
            self._add(report, RiskLevel.BLOCKED, "archive_error", f"압축 구조 검사 실패: {exc}")

    def _inspect_entry(
        self,
        info: zipfile.ZipInfo,
        normalized: str,
        report: SecurityReport,
        seen: set[str],
    ) -> None:
        path = PurePosixPath(normalized)
        parts = path.parts
        if (
            normalized.startswith("/")
            or "\x00" in normalized
            or any(part in {"", ".", ".."} for part in parts)
            or (parts and ":" in parts[0])
        ):
            self._add(
                report,
                RiskLevel.BLOCKED,
                "unsafe_path",
                "압축 내부에 안전하지 않은 경로가 있습니다.",
                normalized,
            )
        key = normalized.casefold()
        if key in seen:
            self._add(
                report,
                RiskLevel.BLOCKED,
                "duplicate_entry",
                "대소문자만 다른 중복 압축 항목이 있습니다.",
                normalized,
            )
        seen.add(key)
        if info.flag_bits & 0x1:
            self._add(
                report,
                RiskLevel.BLOCKED,
                "encrypted_entry",
                "암호화된 압축 항목은 안전하게 검사할 수 없습니다.",
                normalized,
            )
        suffix = path.suffix.lower()
        if suffix in self.DANGEROUS_EXTENSIONS:
            self._add(
                report,
                RiskLevel.BLOCKED,
                "executable_payload",
                f"실행 가능한 위험 확장자({suffix})가 포함되어 있습니다.",
                normalized,
            )
        if info.file_size > self.MAX_XML_BYTES and suffix in {".xml", ".rels"}:
            self._add(
                report,
                RiskLevel.BLOCKED,
                "oversized_xml",
                "단일 XML 항목이 512MB 안전 한도를 초과합니다.",
                normalized,
            )
        ratio = info.file_size / max(1, info.compress_size)
        if info.file_size >= self.ZIP_BOMB_ENTRY_MIN and ratio > self.ZIP_BOMB_ENTRY_RATIO:
            self._add(
                report,
                RiskLevel.BLOCKED,
                "entry_zip_bomb",
                "단일 압축 항목의 압축률이 비정상적으로 높습니다.",
                normalized,
            )

    def _inspect_special_entries(
        self, document_kind: str, names: list[str], report: SecurityReport
    ) -> None:
        lower_names = [name.lower() for name in names]
        for original, lower in zip(names, lower_names, strict=True):
            if lower.endswith("vbaproject.bin") or "macros/" in lower:
                self._add(
                    report,
                    RiskLevel.BLOCKED,
                    "macro_payload",
                    "매크로 코드가 포함된 문서는 처리하지 않습니다.",
                    original,
                )
            if document_kind == "docx" and (
                lower.startswith("word/activex/") or lower.startswith("word/embeddings/")
            ):
                self._add(
                    report,
                    RiskLevel.BLOCKED,
                    "active_content",
                    "ActiveX 또는 OLE 첨부 개체가 포함되어 있습니다.",
                    original,
                )
            if lower.startswith("customui/"):
                self._add(
                    report,
                    RiskLevel.WARNING,
                    "custom_ui",
                    "사용자 지정 Office 리본 구성이 포함되어 있습니다.",
                    original,
                )

    def _inspect_xml(
        self,
        package: zipfile.ZipFile,
        entries: list[zipfile.ZipInfo],
        report: SecurityReport,
        progress: SecurityProgress,
    ) -> None:
        for index, info in enumerate(entries):
            if info.file_size > self.MAX_XML_BYTES:
                continue
            if index % 100 == 0:
                progress(0.55 + 0.1 * index / max(1, len(entries)), "XML 안전 검사")
            try:
                data = package.read(info)
            except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
                self._add(
                    report,
                    RiskLevel.BLOCKED,
                    "xml_read_error",
                    f"XML 항목을 읽을 수 없습니다: {exc}",
                    info.filename,
                )
                continue
            upper = data.upper()
            if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
                self._add(
                    report,
                    RiskLevel.BLOCKED,
                    "xml_entity",
                    "DTD 또는 외부 엔터티가 포함된 XML은 처리하지 않습니다.",
                    info.filename,
                )
                continue
            try:
                SafeET.fromstring(data)
            except (SafeET.ParseError, DefusedXmlException) as exc:
                self._add(
                    report,
                    RiskLevel.BLOCKED,
                    "unsafe_xml",
                    f"손상되었거나 안전하지 않은 XML입니다: {exc}",
                    info.filename,
                )

    def _inspect_relationships(
        self,
        package: zipfile.ZipFile,
        entries: list[zipfile.ZipInfo],
        report: SecurityReport,
    ) -> None:
        for info in entries:
            if info.file_size > self.MAX_RELATIONSHIP_BYTES:
                self._add(
                    report,
                    RiskLevel.BLOCKED,
                    "oversized_relationships",
                    "관계 정보 파일이 비정상적으로 큽니다.",
                    info.filename,
                )
                continue
            try:
                root = SafeET.fromstring(package.read(info))
            except (OSError, RuntimeError, SafeET.ParseError, DefusedXmlException):
                continue
            for relationship in root.iter():
                if not relationship.tag.endswith("Relationship"):
                    continue
                if relationship.get("TargetMode", "").lower() != "external":
                    continue
                target = relationship.get("Target", "").strip()
                scheme = urlparse(target).scheme.lower()
                if scheme in self.DANGEROUS_SCHEMES or target.startswith(("\\\\", "//")):
                    self._add(
                        report,
                        RiskLevel.BLOCKED,
                        "dangerous_external_link",
                        "위험한 외부 링크 형식이 포함되어 있습니다.",
                        target[:200],
                    )
                else:
                    self._add(
                        report,
                        RiskLevel.WARNING,
                        "external_link",
                        "외부 링크가 포함되어 있습니다. 결과를 열 때 링크를 확인하세요.",
                        target[:200],
                    )

    def _scan_hwp(self, path: Path, report: SecurityReport, progress: SecurityProgress) -> None:
        progress(0.1, "HWP 바이너리 구조 검사")
        try:
            with path.open("rb") as stream:
                if stream.read(8) != self.OLE_PREFIX:
                    self._add(
                        report,
                        RiskLevel.BLOCKED,
                        "invalid_hwp",
                        "정상적인 OLE 기반 HWP 파일이 아닙니다.",
                    )
                    return
                stream.seek(0)
                indicators = {
                    b"DefaultJScript": False,
                    "DefaultJScript".encode("utf-16le"): False,
                    b"ScriptCode": False,
                    "ScriptCode".encode("utf-16le"): False,
                }
                overlap = b""
                while chunk := stream.read(1024 * 1024):
                    block = overlap + chunk
                    for pattern in indicators:
                        if pattern in block:
                            indicators[pattern] = True
                    overlap = block[-64:]
                if any(indicators.values()):
                    self._add(
                        report,
                        RiskLevel.BLOCKED,
                        "hwp_script",
                        "HWP 스크립트 지표가 발견되어 자동 열기를 차단했습니다.",
                    )
                    return

            with olefile.OleFileIO(str(path)) as compound:
                streams = ["/".join(parts) for parts in compound.listdir()]
                roots = {name.split("/", 1)[0].casefold() for name in streams}
                if not {"fileheader", "docinfo"}.issubset(roots):
                    self._add(
                        report,
                        RiskLevel.BLOCKED,
                        "invalid_hwp_structure",
                        "필수 HWP 스트림이 없어 정상 문서로 확인할 수 없습니다.",
                    )
                    return

                stream_keys = {name.casefold() for name in streams}
                if any(
                    name.startswith("scripts/") or name.endswith("/defaultjscript")
                    for name in stream_keys
                ):
                    self._add(
                        report,
                        RiskLevel.BLOCKED,
                        "hwp_script_storage",
                        "HWP Scripts 저장소가 포함되어 자동 열기를 차단했습니다.",
                    )

                for stream_name in streams:
                    if not stream_name.casefold().startswith("bindata/"):
                        continue
                    suffix = PurePosixPath(stream_name).suffix.lower()
                    if suffix in self.DANGEROUS_EXTENSIONS:
                        self._add(
                            report,
                            RiskLevel.BLOCKED,
                            "hwp_executable_bindata",
                            f"HWP BinData에 위험 확장자({suffix})가 포함되어 있습니다.",
                            stream_name,
                        )

                if not report.blocked:
                    self._add(
                        report,
                        RiskLevel.WARNING,
                        "hwp_static_limit",
                        "구형 HWP는 정적 검사 범위가 제한됩니다. 최신 한/글과 Windows Defender를 사용하세요.",
                    )
        except (OSError, ValueError, TypeError) as exc:
            self._add(report, RiskLevel.BLOCKED, "hwp_read_error", f"HWP 검사 실패: {exc}")

    def _scan_with_windows_defender(self, path: Path, report: SecurityReport) -> None:
        if os.name != "nt":
            return
        executable = self._defender_executable()
        if executable is None:
            self._add(
                report,
                RiskLevel.WARNING,
                "defender_unavailable",
                "Windows Defender 명령줄 검사를 사용할 수 없습니다.",
            )
            return
        command = [
            str(executable),
            "-Scan",
            "-ScanType",
            "3",
            "-File",
            str(path),
            "-DisableRemediation",
        ]
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            self._add(
                report,
                RiskLevel.WARNING,
                "defender_error",
                f"Windows Defender 검사를 완료하지 못했습니다: {exc}",
            )
            return
        output = f"{completed.stdout}\n{completed.stderr}".lower()
        clean_phrases = ("no threats", "no threat", "위협이 없습니다", "위협 없음")
        threat_words = re.search(r"\b(threat|infected|malware)\b", output)
        looks_clean = any(phrase in output for phrase in clean_phrases)
        if completed.returncode == 2 or (threat_words and not looks_clean):
            self._add(
                report,
                RiskLevel.BLOCKED,
                "defender_threat",
                "Windows Defender가 위협 가능성을 보고했습니다.",
            )
        elif completed.returncode != 0:
            self._add(
                report,
                RiskLevel.WARNING,
                "defender_nonzero",
                f"Windows Defender 검사 결과를 확인할 수 없습니다(코드 {completed.returncode}).",
            )

    @staticmethod
    def _defender_executable() -> Path | None:
        candidates: list[Path] = []
        program_files = os.environ.get("PROGRAMFILES")
        program_data = os.environ.get("PROGRAMDATA")
        if program_files:
            candidates.append(Path(program_files) / "Windows Defender" / "MpCmdRun.exe")
        if program_data:
            platform_dir = Path(program_data) / "Microsoft" / "Windows Defender" / "Platform"
            with contextlib.suppress(OSError):
                candidates.extend(sorted(platform_dir.glob("*/MpCmdRun.exe"), reverse=True))
        return next((candidate for candidate in candidates if candidate.is_file()), None)

    @staticmethod
    def _add(
        report: SecurityReport,
        level: RiskLevel,
        code: str,
        message: str,
        entry: str | None = None,
    ) -> None:
        finding = SecurityFinding(level=level, code=code, message=message, entry=entry)
        if finding not in report.findings:
            report.findings.append(finding)
