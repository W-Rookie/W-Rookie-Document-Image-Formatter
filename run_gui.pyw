"""W-Rookie no-console Windows launcher with a visible crash report."""

from __future__ import annotations

import contextlib
import os
import tempfile
import traceback
from pathlib import Path


def show_fatal_error(details: str, log_path: Path) -> None:
    summary = details.strip().splitlines()[-1] if details.strip() else "알 수 없는 오류"
    summary = summary[:500]
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "W-Rookie 실행 오류",
            "GUI를 시작하지 못했습니다.\n\n"
            f"원인: {summary}\n\n"
            f"오류 기록: {log_path}\n\n"
            "setup.bat을 다시 실행한 뒤 시도하세요.",
            parent=root,
        )
        root.destroy()
    except Exception:
        # pythonw has no console; the log remains the final recovery channel.
        _ = details


def main() -> int:
    project_dir = Path(__file__).resolve().parent
    log_path = project_dir / "w-rookie-error.log"
    try:
        from docpicalign.app import main as app_main

        with contextlib.suppress(OSError):
            log_path.unlink(missing_ok=True)
        return app_main()
    except Exception:
        details = traceback.format_exc()
        try:
            log_path.write_text(details, encoding="utf-8")
        except OSError:
            fallback_root = Path(os.environ.get("TEMP", tempfile.gettempdir())) / "WRookie"
            with contextlib.suppress(OSError):
                fallback_root.mkdir(parents=True, exist_ok=True)
            log_path = fallback_root / "w-rookie-error.log"
            with contextlib.suppress(OSError):
                log_path.write_text(details, encoding="utf-8")
        show_fatal_error(details, log_path)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
