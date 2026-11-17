from __future__ import annotations

import os
import sys
from pathlib import Path

from .models import JobOptions, OutputMode

SUPPORTED_EXTENSIONS = {".docx", ".hwp", ".hwpx"}


def human_size(size: int) -> str:
    units = ("B", "KB", "MB", "GB", "TB")
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"


def is_supported(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS


def collect_documents(folder: Path, recursive: bool = True) -> list[Path]:
    iterator = folder.rglob("*") if recursive else folder.glob("*")
    return sorted((p.resolve() for p in iterator if is_supported(p)), key=str.lower)


def output_path_for(source: Path, options: JobOptions) -> Path:
    source = source.resolve()
    if options.output_mode is OutputMode.OVERWRITE:
        return source
    folder = options.output_dir.resolve() if options.output_dir else source.parent
    desired = folder / f"{source.stem}{options.suffix}{source.suffix}"
    if not desired.exists() and desired != source:
        return desired
    index = 2
    while True:
        candidate = folder / f"{source.stem}{options.suffix}_{index}{source.suffix}"
        if not candidate.exists() and candidate != source:
            return candidate
        index += 1


def default_settings_dir() -> Path:
    if os.name == "nt":
        root = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return root / "WRookie"
