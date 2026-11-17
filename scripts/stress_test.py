from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from test_docx_processor import CONTENT_TYPES, DOCUMENT  # noqa: E402

from docpicalign.models import JobOptions  # noqa: E402
from docpicalign.processors.docx import DocxProcessor  # noqa: E402


def digest_member(path: Path, member: str) -> str:
    digest = hashlib.sha256()
    with zipfile.ZipFile(path) as package, package.open(member) as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a DOCX large-file streaming test")
    parser.add_argument("--size-mb", type=int, default=128)
    args = parser.parse_args()
    if args.size_mb < 1:
        parser.error("--size-mb must be positive")

    # Deterministic, incompressible-enough chunks. Media is ZIP_STORED so the
    # requested package size is preserved without holding it in memory.
    chunk = hashlib.shake_256(b"W-Rookie stress media").digest(1024 * 1024)
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        source = folder / "large.docx"
        output = folder / "large_formatted.docx"
        with zipfile.ZipFile(source, "w", allowZip64=True) as package:
            package.writestr("[Content_Types].xml", CONTENT_TYPES)
            package.writestr("word/document.xml", DOCUMENT)
            info = zipfile.ZipInfo("word/media/large.bin")
            info.compress_type = zipfile.ZIP_STORED
            with package.open(info, "w", force_zip64=True) as stream:
                for _ in range(args.size_mb):
                    stream.write(chunk)

        before = digest_member(source, "word/media/large.bin")
        started = time.perf_counter()
        result = DocxProcessor().process(source, JobOptions(), output=output)
        elapsed = time.perf_counter() - started
        if not result.success:
            print(f"FAIL: {result.error}")
            return 1
        after = digest_member(output, "word/media/large.bin")
        if before != after:
            print("FAIL: media SHA-256 mismatch")
            return 1
        print(
            f"PASS: {args.size_mb} MB media preserved, {result.pictures_changed} picture formatted "
            f"in {elapsed:.2f}s"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
