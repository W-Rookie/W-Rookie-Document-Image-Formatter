from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from .models import AlignMode, BorderStyle, JobOptions, OutputMode
from .paths import collect_documents, is_supported
from .service import ProcessingService, diagnose_environment


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="w-rookie-cli",
        description="DOCX/HWP/HWPX 그림의 크기·정렬·테두리를 일괄 편집합니다.",
    )
    parser.add_argument("files", nargs="*", type=Path, help="처리할 파일 또는 폴더")
    parser.add_argument("--mode", choices=("smart", "page"), default="smart")
    parser.add_argument("--width", type=float, metavar="SIZE")
    parser.add_argument("--height", type=float, metavar="SIZE")
    parser.add_argument("--unit", choices=("mm", "cm"), default="mm")
    parser.add_argument("--stretch", action="store_true", help="크기 변경 시 원본 비율 해제")
    parser.add_argument("--border", type=float, default=1.0, metavar="PT")
    parser.add_argument("--color", default="000000", metavar="RRGGBB")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--no-recursive", action="store_true")
    parser.add_argument("--body-only", action="store_true")
    parser.add_argument("--hwp-visible", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--diagnose", action="store_true")
    return parser


def _documents(inputs: list[Path], recursive: bool) -> list[Path]:
    found: list[Path] = []
    for item in inputs:
        if item.is_dir():
            found.extend(collect_documents(item, recursive=recursive))
        elif is_supported(item):
            found.append(item.resolve())
    return list(dict.fromkeys(found))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.diagnose:
        rows = diagnose_environment()
        if args.as_json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            for name, ok, message in rows:
                print(f"[{'OK' if ok else '!!'}] {name}: {message}")
        return 0 if all(ok for _, ok, _ in rows[:2]) else 1

    documents = _documents(args.files, recursive=not args.no_recursive)
    if not documents:
        print("처리할 DOCX/HWP/HWPX 파일이 없습니다.", file=sys.stderr)
        return 2
    try:
        size_factor = 10.0 if args.unit == "cm" else 1.0
        options = JobOptions(
            align_mode=AlignMode(args.mode),
            resize_width_mm=args.width * size_factor if args.width is not None else None,
            resize_height_mm=args.height * size_factor if args.height is not None else None,
            lock_aspect_ratio=not args.stretch,
            border=BorderStyle(args.border, args.color),
            output_mode=OutputMode.OVERWRITE if args.overwrite else OutputMode.COPY,
            output_dir=args.output_dir,
            include_headers_footers=not args.body_only,
            hwp_visible=args.hwp_visible,
        )
    except ValueError as exc:
        print(f"옵션 오류: {exc}", file=sys.stderr)
        return 2

    service = ProcessingService()
    results = []
    for index, path in enumerate(documents, 1):
        if not args.as_json:
            print(f"[{index}/{len(documents)}] {path.name}")

        def report(value: float, message: str) -> None:
            if not args.as_json:
                print(f"  {value * 100:5.1f}% {message}", end="\r", flush=True)

        result = service.process_one(path, options, progress=report)
        results.append(result)
        if not args.as_json:
            print(" " * 100, end="\r")
            state = "완료" if result.success else "실패"
            detail = (
                f"그림 {result.pictures_changed}개 · {result.output}"
                if result.success
                else result.error
            )
            print(f"  {state}: {detail}")
            for warning in result.warnings:
                print(f"  주의: {warning}")

    if args.as_json:
        payload = []
        for result in results:
            item = asdict(result)
            item["source"] = str(result.source)
            item["output"] = str(result.output) if result.output else None
            item["success"] = result.success
            payload.append(item)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if all(result.success for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
