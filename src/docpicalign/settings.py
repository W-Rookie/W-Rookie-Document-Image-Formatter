from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .paths import default_settings_dir


@dataclass(slots=True)
class AppSettings:
    align_mode: str = "smart"
    resize_enabled: bool = False
    resize_width: str = ""
    resize_height: str = ""
    resize_unit: str = "mm"
    lock_aspect_ratio: bool = True
    border_width: float = 1.0
    border_color: str = "000000"
    output_mode: str = "copy"
    output_dir: str = ""
    include_headers_footers: bool = True
    hwp_visible: bool = False
    security_scan: bool = True
    windows_defender_scan: bool = True
    last_folder: str = ""

    @classmethod
    def load(cls, path: Path | None = None) -> AppSettings:
        path = path or default_settings_dir() / "settings.json"
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            allowed = {field for field in cls.__dataclass_fields__}
            return cls(**{k: v for k, v in raw.items() if k in allowed})
        except (OSError, ValueError, TypeError):
            return cls()

    def save(self, path: Path | None = None) -> None:
        path = path or default_settings_dir() / "settings.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(asdict(self), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        temporary.replace(path)
