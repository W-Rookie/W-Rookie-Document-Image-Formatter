from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class AlignMode(str, Enum):
    """Picture positioning strategy."""

    SMART = "smart"
    PAGE = "page"


class OutputMode(str, Enum):
    """How processed documents are written."""

    COPY = "copy"
    OVERWRITE = "overwrite"


@dataclass(frozen=True, slots=True)
class BorderStyle:
    width_pt: float = 1.0
    color: str = "000000"

    def __post_init__(self) -> None:
        if not 0.1 <= self.width_pt <= 12.0:
            raise ValueError("border width must be between 0.1 and 12 pt")
        value = self.color.lstrip("#").upper()
        if len(value) != 6 or any(c not in "0123456789ABCDEF" for c in value):
            raise ValueError("border color must be a 6-digit RGB hex value")
        object.__setattr__(self, "color", value)


def fitted_dimensions(
    original_width: float,
    original_height: float,
    target_width: float | None,
    target_height: float | None,
    lock_aspect_ratio: bool,
) -> tuple[float, float]:
    """Return target dimensions, optionally fitting inside a size box."""
    if not lock_aspect_ratio:
        return target_width or original_width, target_height or original_height
    if target_width is not None and target_height is not None:
        scale = min(target_width / original_width, target_height / original_height)
    elif target_width is not None:
        scale = target_width / original_width
    elif target_height is not None:
        scale = target_height / original_height
    else:
        scale = 1.0
    return original_width * scale, original_height * scale


@dataclass(frozen=True, slots=True)
class JobOptions:
    align_mode: AlignMode = AlignMode.SMART
    resize_width_mm: float | None = None
    resize_height_mm: float | None = None
    lock_aspect_ratio: bool = True
    border: BorderStyle = field(default_factory=BorderStyle)
    output_mode: OutputMode = OutputMode.COPY
    output_dir: Path | None = None
    suffix: str = "_사진정렬"
    include_headers_footers: bool = True
    hwp_visible: bool = False
    security_scan: bool = True
    windows_defender_scan: bool = True

    def __post_init__(self) -> None:
        for label, value in (
            ("width", self.resize_width_mm),
            ("height", self.resize_height_mm),
        ):
            if value is not None and not 0 < value <= 1000:
                raise ValueError(f"resize {label} must be between 0 and 1000 mm")


@dataclass(slots=True)
class ProcessResult:
    source: Path
    output: Path | None
    pictures_found: int = 0
    pictures_changed: int = 0
    warnings: list[str] = field(default_factory=list)
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None


ProgressCallback = Callable[[float, str], None]
CancelCheck = Callable[[], bool]


class ProcessingCancelled(RuntimeError):
    pass


class DocumentError(RuntimeError):
    pass
