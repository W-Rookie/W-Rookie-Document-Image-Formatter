from __future__ import annotations

from pathlib import Path

from .models import CancelCheck, JobOptions, ProcessResult, ProgressCallback
from .paths import output_path_for
from .processors import DocxProcessor, HwpProcessor
from .security import RiskLevel, SecurityReport, SecurityScanner


class ProcessingService:
    def __init__(self) -> None:
        self.docx = DocxProcessor()
        self.hwp = HwpProcessor()
        self.security = SecurityScanner()

    def process_one(
        self,
        source: Path,
        options: JobOptions,
        *,
        progress: ProgressCallback | None = None,
        cancelled: CancelCheck | None = None,
    ) -> ProcessResult:
        suffix = source.suffix.lower()
        output = output_path_for(source, options)
        security_report: SecurityReport | None = None
        processor_progress = progress
        if options.security_scan:
            if progress:
                progress(0.0, "보안 검사 시작")

            def security_progress(value: float, message: str) -> None:
                if progress:
                    progress(value * 0.15, message)

            security_report = self.security.scan(
                source,
                use_windows_defender=options.windows_defender_scan,
                progress=security_progress,
            )
            if security_report.blocked:
                messages = [item.message for item in security_report.blocks[:3]]
                if len(security_report.blocks) > 3:
                    messages.append(f"외 {len(security_report.blocks) - 3}건")
                return ProcessResult(
                    source=source,
                    output=None,
                    error="보안 검사에서 차단했습니다: " + " / ".join(messages),
                )

            def mapped_progress(value: float, message: str) -> None:
                if progress:
                    progress(0.15 + value * 0.85, message)

            processor_progress = mapped_progress

        if suffix == ".docx":
            result = self.docx.process(
                source,
                options,
                output=output,
                progress=processor_progress,
                cancelled=cancelled,
            )
        elif suffix in {".hwp", ".hwpx"}:
            result = self.hwp.process(
                source,
                options,
                output=output,
                progress=processor_progress,
                cancelled=cancelled,
            )
        else:
            result = ProcessResult(
                source=source, output=None, error="지원하지 않는 파일 형식입니다."
            )
        if security_report:
            result.warnings[:0] = [
                f"보안 경고: {item.message}"
                for item in security_report.findings
                if item.level is RiskLevel.WARNING
            ]
        return result


def diagnose_environment() -> list[tuple[str, bool, str]]:
    import platform
    import sys

    rows: list[tuple[str, bool, str]] = [
        (
            "Python",
            sys.version_info >= (3, 10),
            f"{platform.python_version()} ({platform.architecture()[0]})",
        ),
        ("DOCX 엔진", True, "내장 OOXML 스트리밍 엔진 사용 가능"),
    ]
    available, message = HwpProcessor.diagnostic()
    rows.append(("HWP/HWPX 엔진", available, message))
    return rows
