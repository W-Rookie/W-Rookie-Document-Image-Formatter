from __future__ import annotations

import contextlib
import os
import queue
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox, ttk
from tkinter import font as tkfont

from .models import AlignMode, BorderStyle, JobOptions, OutputMode
from .paths import collect_documents, human_size, is_supported
from .service import ProcessingService, diagnose_environment
from .settings import AppSettings

IS_WINDOWS = os.name == "nt"


class WRookieApp(tk.Tk):
    BG = "#08090C"
    CARD = "#111318"
    SURFACE = "#191C22"
    TEXT = "#F7F7F8"
    MUTED = "#979CA7"
    ACCENT = "#E50914"
    ACCENT_HOVER = "#FF2633"
    BORDER = "#2A2E36"
    SUCCESS = "#38D979"
    DANGER = "#FF4D57"

    def __init__(self) -> None:
        super().__init__()
        self.title("W-Rookie · 문서 사진 자동 편집")
        self.geometry("1180x780")
        self.minsize(1020, 700)
        self.configure(bg=self.BG)
        self.ui_font = self._select_ui_font()
        self.option_add("*Font", (self.ui_font, 10))
        self._background_image: tk.PhotoImage | None = None
        background_path = Path(__file__).with_name("assets") / "background.png"
        with contextlib.suppress(OSError, tk.TclError):
            self._background_image = tk.PhotoImage(file=background_path)

        self.settings = AppSettings.load()
        self.service = ProcessingService()
        self.documents: list[Path] = []
        self.events: queue.Queue[tuple] = queue.Queue()
        self.cancel_event = threading.Event()
        self.worker: threading.Thread | None = None
        self.inputs_enabled = True
        self.row_by_path: dict[Path, str] = {}

        self.align_var = tk.StringVar(value=self.settings.align_mode)
        self.resize_enabled_var = tk.BooleanVar(value=self.settings.resize_enabled)
        self.resize_width_var = tk.StringVar(value=self.settings.resize_width)
        self.resize_height_var = tk.StringVar(value=self.settings.resize_height)
        self.resize_unit_var = tk.StringVar(value=self.settings.resize_unit)
        self.lock_aspect_var = tk.BooleanVar(value=self.settings.lock_aspect_ratio)
        self.border_var = tk.StringVar(value=str(self.settings.border_width))
        self.color_var = tk.StringVar(value=self.settings.border_color)
        self.output_mode_var = tk.StringVar(value=self.settings.output_mode)
        self.output_dir_var = tk.StringVar(value=self.settings.output_dir)
        self.parts_var = tk.BooleanVar(value=self.settings.include_headers_footers)
        self.hwp_visible_var = tk.BooleanVar(value=self.settings.hwp_visible)
        self.defender_var = tk.BooleanVar(value=self.settings.windows_defender_scan)
        self.status_var = tk.StringVar(value="파일을 추가해 주세요")
        self.progress_var = tk.DoubleVar(value=0)

        self._configure_styles()
        self._build_ui()
        self.align_var.trace_add("write", self._update_mode_hint)
        self.resize_enabled_var.trace_add("write", self._update_resize_controls)
        self.output_mode_var.trace_add("write", self._update_output_controls)
        self._update_mode_hint()
        self._update_resize_controls()
        self._update_output_controls()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(100, self._drain_events)

    def _select_ui_font(self) -> str:
        available = set(tkfont.families(self))
        if IS_WINDOWS:
            candidates = ("Malgun Gothic", "맑은 고딕", "Arial")
        elif sys.platform == "darwin":
            candidates = ("Apple SD Gothic Neo", "AppleGothic", "Arial")
        else:
            candidates = ("Noto Sans CJK KR", "NanumGothic", "DejaVu Sans")
        return next((name for name in candidates if name in available), "TkDefaultFont")

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        with contextlib.suppress(tk.TclError):
            style.theme_use("clam")
        style.configure("TFrame", background=self.BG)
        style.configure("Card.TFrame", background=self.CARD)
        style.configure("TLabel", background=self.BG, foreground=self.TEXT)
        style.configure("Card.TLabel", background=self.CARD, foreground=self.TEXT)
        style.configure("Muted.TLabel", background=self.CARD, foreground=self.MUTED)
        style.configure(
            "Title.TLabel",
            foreground=self.TEXT,
            font=(self.ui_font, 24, "bold"),
        )
        style.configure(
            "Eyebrow.TLabel",
            foreground=self.ACCENT,
            font=(self.ui_font, 8, "bold"),
        )
        style.configure("Subtitle.TLabel", foreground=self.MUTED, font=(self.ui_font, 10))
        style.configure(
            "Section.TLabel",
            background=self.CARD,
            foreground=self.ACCENT_HOVER,
            font=(self.ui_font, 10, "bold"),
        )
        style.configure(
            "Badge.TLabel",
            background="#2A1013",
            foreground="#FF6B73",
            padding=(8, 3),
            font=(self.ui_font, 8, "bold"),
        )
        style.configure(
            "TButton",
            background=self.SURFACE,
            foreground=self.TEXT,
            bordercolor=self.BORDER,
            lightcolor=self.SURFACE,
            darkcolor=self.SURFACE,
            borderwidth=1,
            padding=(11, 8),
        )
        style.map(
            "TButton",
            background=[("active", "#252932"), ("pressed", "#303540")],
            foreground=[("disabled", "#5F646E")],
        )
        style.configure(
            "Accent.TButton",
            background=self.ACCENT,
            foreground="white",
            bordercolor=self.ACCENT,
            lightcolor=self.ACCENT,
            darkcolor=self.ACCENT,
            borderwidth=1,
            padding=(22, 12),
            font=(self.ui_font, 11, "bold"),
        )
        style.map(
            "Accent.TButton",
            background=[("active", self.ACCENT_HOVER), ("pressed", "#B70710")],
        )
        style.configure("Soft.TButton", padding=(12, 8), background="#14171C")
        style.configure(
            "Treeview",
            rowheight=32,
            background="#0D0F13",
            fieldbackground="#0D0F13",
            foreground="#E8E9EC",
            bordercolor=self.BORDER,
            lightcolor=self.BORDER,
            darkcolor=self.BORDER,
        )
        style.map(
            "Treeview",
            background=[("selected", "#611016")],
            foreground=[("selected", "#FFFFFF")],
        )
        style.configure(
            "Treeview.Heading",
            background="#1B1E24",
            foreground="#D7D9DE",
            bordercolor=self.BORDER,
            font=(self.ui_font, 9, "bold"),
            padding=(8, 9),
        )
        style.map("Treeview.Heading", background=[("active", "#252932")])
        style.configure(
            "Horizontal.TProgressbar",
            troughcolor="#20232A",
            background=self.ACCENT,
            bordercolor="#20232A",
            lightcolor=self.ACCENT,
            darkcolor=self.ACCENT,
        )
        style.configure(
            "Card.TRadiobutton",
            background=self.CARD,
            foreground=self.TEXT,
            indicatorcolor="#0D0F13",
        )
        style.map(
            "Card.TRadiobutton",
            indicatorcolor=[("selected", self.ACCENT), ("active", self.ACCENT_HOVER)],
            foreground=[("disabled", "#5F646E")],
        )
        style.configure(
            "Card.TCheckbutton",
            background=self.CARD,
            foreground=self.TEXT,
            indicatorcolor="#0D0F13",
        )
        style.map(
            "Card.TCheckbutton",
            indicatorcolor=[("selected", self.ACCENT), ("active", self.ACCENT_HOVER)],
            foreground=[("disabled", "#5F646E")],
        )
        style.configure(
            "Axis.TCheckbutton",
            background=self.SURFACE,
            foreground=self.TEXT,
            indicatorcolor="#08090C",
            padding=(12, 7),
            font=(self.ui_font, 9, "bold"),
        )
        style.map(
            "Axis.TCheckbutton",
            background=[("active", "#242832"), ("selected", "#2A1013")],
            indicatorcolor=[("selected", self.ACCENT), ("active", self.ACCENT_HOVER)],
        )
        style.configure(
            "TEntry",
            fieldbackground="#0D0F13",
            foreground=self.TEXT,
            bordercolor=self.BORDER,
            insertcolor=self.TEXT,
        )
        style.configure(
            "TSpinbox",
            fieldbackground="#0D0F13",
            foreground=self.TEXT,
            bordercolor=self.BORDER,
            arrowcolor=self.TEXT,
        )
        style.configure(
            "TCombobox",
            fieldbackground="#0D0F13",
            background=self.SURFACE,
            foreground=self.TEXT,
            bordercolor=self.BORDER,
            arrowcolor=self.TEXT,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", "#0D0F13")],
            foreground=[("readonly", self.TEXT), ("disabled", "#5F646E")],
        )
        style.configure("TSeparator", background=self.BORDER)
        style.configure("TPanedwindow", background=self.BG)

    def _build_ui(self) -> None:
        shell = tk.Frame(self, background=self.BG)
        shell.pack(fill="both", expand=True)
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_rowconfigure(2, weight=1)
        if self._background_image is not None:
            tk.Label(
                shell,
                image=self._background_image,
                borderwidth=0,
                highlightthickness=0,
                background=self.BG,
            ).place(relx=0.5, rely=0.5, anchor="center")

        header = tk.Canvas(shell, height=92, background=self.BG, highlightthickness=0)
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(16, 8))
        image_id = None
        if self._background_image is not None:
            image_id = header.create_image(0, 0, image=self._background_image, anchor="n")
        header.create_text(
            18,
            13,
            anchor="nw",
            text="DOCUMENT AUTOMATION  /  LOCAL ENGINE",
            fill=self.ACCENT_HOVER,
            font=(self.ui_font, 8, "bold"),
        )
        header.create_text(
            18,
            31,
            anchor="nw",
            text="W-Rookie",
            fill=self.TEXT,
            font=(self.ui_font, 24, "bold"),
        )
        header.create_text(
            18,
            67,
            anchor="nw",
            text=(
                "DOCX · HWP · HWPX 사진을 한 번에 깔끔하게"
                if IS_WINDOWS
                else "DOCX 사진을 한 번에 깔끔하게"
            ),
            fill="#C2C5CC",
            font=(self.ui_font, 9),
        )
        header_buttons = ttk.Frame(header)
        ttk.Button(
            header_buttons, text="사용법", style="Soft.TButton", command=self._show_help
        ).pack(side="left")
        ttk.Button(
            header_buttons, text="보안 안내", style="Soft.TButton", command=self._show_security_help
        ).pack(side="left", padx=(8, 0))
        ttk.Button(
            header_buttons, text="환경 진단", style="Soft.TButton", command=self._diagnose
        ).pack(side="left", padx=(8, 0))
        buttons_id = header.create_window(0, 22, window=header_buttons, anchor="ne")

        def resize_header(event: tk.Event) -> None:
            if image_id is not None:
                header.coords(image_id, event.width / 2, 0)
            header.coords(buttons_id, event.width - 14, 22)

        header.bind("<Configure>", resize_header)

        divider = tk.Frame(shell, height=2, background=self.ACCENT)
        divider.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 12))

        body = ttk.Panedwindow(shell, orient="horizontal")
        body.grid(row=2, column=0, sticky="nsew", padx=30)
        left = ttk.Frame(body, style="Card.TFrame", padding=16)
        right_host = ttk.Frame(body, style="Card.TFrame")
        right_canvas = tk.Canvas(
            right_host,
            background=self.CARD,
            borderwidth=0,
            highlightthickness=0,
            yscrollincrement=20,
        )
        right_scrollbar = ttk.Scrollbar(right_host, orient="vertical", command=right_canvas.yview)
        right_canvas.configure(yscrollcommand=right_scrollbar.set)
        right_scrollbar.pack(side="right", fill="y")
        right_canvas.pack(side="left", fill="both", expand=True)
        right = ttk.Frame(right_canvas, style="Card.TFrame", padding=16)
        right_window = right_canvas.create_window(0, 0, anchor="nw", window=right)

        def update_options_scrollregion(_event: tk.Event) -> None:
            right_canvas.configure(scrollregion=right_canvas.bbox("all"))

        def fit_options_width(event: tk.Event) -> None:
            right_canvas.itemconfigure(right_window, width=event.width)

        right.bind("<Configure>", update_options_scrollregion)
        right_canvas.bind("<Configure>", fit_options_width)
        body.add(left, weight=3)
        body.add(right_host, weight=2)

        file_header = ttk.Frame(left, style="Card.TFrame")
        file_header.pack(fill="x", pady=(0, 10))
        ttk.Label(file_header, text="처리할 문서", style="Section.TLabel").pack(side="left")
        self.count_label = ttk.Label(file_header, text="0개", style="Badge.TLabel")
        self.count_label.pack(side="left", padx=(8, 0))
        ttk.Button(file_header, text="파일 추가", command=self._add_files).pack(side="right")
        ttk.Button(file_header, text="폴더 추가", command=self._add_folder).pack(
            side="right", padx=(0, 7)
        )

        tree_frame = ttk.Frame(left, style="Card.TFrame")
        tree_frame.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("type", "size", "status"),
            show="tree headings",
            selectmode="extended",
        )
        self.tree.heading("#0", text="파일명", anchor="w")
        self.tree.heading("type", text="형식", anchor="center")
        self.tree.heading("size", text="크기", anchor="e")
        self.tree.heading("status", text="상태", anchor="center")
        self.tree.column("#0", width=275, minwidth=180)
        self.tree.column("type", width=65, stretch=False, anchor="center")
        self.tree.column("size", width=86, stretch=False, anchor="e")
        self.tree.column("status", width=95, stretch=False, anchor="center")
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.tag_configure("success", foreground=self.SUCCESS)
        self.tree.tag_configure("error", foreground=self.DANGER)
        self.tree.tag_configure("working", foreground=self.ACCENT)
        self.tree.bind("<Delete>", lambda _event: self._remove_selected())

        file_footer = ttk.Frame(left, style="Card.TFrame")
        file_footer.pack(fill="x", pady=(10, 0))
        ttk.Button(file_footer, text="선택 제거", command=self._remove_selected).pack(side="left")
        ttk.Button(file_footer, text="전체 비우기", command=self._clear_files).pack(
            side="left", padx=(7, 0)
        )
        ttk.Label(
            file_footer,
            text="대용량 파일 지원 · 원본 보존이 기본값",
            style="Muted.TLabel",
        ).pack(side="right")

        ttk.Label(right, text="01  정렬 기준", style="Section.TLabel").pack(anchor="w")
        self.smart_radio = ttk.Radiobutton(
            right,
            text="스마트 중앙 정렬  (권장)",
            value="smart",
            variable=self.align_var,
            style="Card.TRadiobutton",
        )
        self.smart_radio.pack(anchor="w", pady=(9, 2))
        self.page_radio = ttk.Radiobutton(
            right,
            text="페이지 가로·세로 중앙",
            value="page",
            variable=self.align_var,
            style="Card.TRadiobutton",
        )
        self.page_radio.pack(anchor="w", pady=(2, 4))
        self.mode_hint = ttk.Label(
            right, text="", style="Muted.TLabel", wraplength=350, justify="left"
        )
        self.mode_hint.pack(anchor="w", fill="x", pady=(2, 9))

        ttk.Label(right, text="02  사진 크기", style="Section.TLabel").pack(anchor="w")
        self.resize_enabled_check = ttk.Checkbutton(
            right,
            text="크기 조절 사용",
            variable=self.resize_enabled_var,
            style="Card.TCheckbutton",
        )
        self.resize_enabled_check.pack(anchor="w", pady=(6, 4))
        size_row = ttk.Frame(right, style="Card.TFrame")
        size_row.pack(fill="x", pady=(1, 4))
        ttk.Label(size_row, text="가로", style="Card.TLabel").pack(side="left")
        self.resize_width_entry = ttk.Entry(size_row, width=7, textvariable=self.resize_width_var)
        self.resize_width_entry.pack(side="left", padx=(6, 10))
        ttk.Label(size_row, text="세로", style="Card.TLabel").pack(side="left")
        self.resize_height_entry = ttk.Entry(size_row, width=7, textvariable=self.resize_height_var)
        self.resize_height_entry.pack(side="left", padx=(6, 10))
        self.resize_unit_combo = ttk.Combobox(
            size_row,
            width=5,
            values=("mm", "cm"),
            state="readonly",
            textvariable=self.resize_unit_var,
        )
        self.resize_unit_combo.pack(side="left")
        self.lock_aspect_check = ttk.Checkbutton(
            right,
            text="원본 비율 유지",
            variable=self.lock_aspect_var,
            style="Card.TCheckbutton",
        )
        self.lock_aspect_check.pack(anchor="w", pady=(2, 1))
        self.resize_hint = ttk.Label(
            right,
            text="비율 유지: 한쪽만 입력하거나 가로·세로 박스 안에 맞춤",
            style="Muted.TLabel",
            wraplength=360,
        )
        self.resize_hint.pack(anchor="w", pady=(1, 8))

        separator = ttk.Separator(right)
        separator.pack(fill="x", pady=(0, 10))
        ttk.Label(right, text="03  사진 테두리", style="Section.TLabel").pack(anchor="w")
        border_row = ttk.Frame(right, style="Card.TFrame")
        border_row.pack(fill="x", pady=(6, 10))
        ttk.Label(border_row, text="두께", style="Card.TLabel").pack(side="left")
        self.border_spin = ttk.Spinbox(
            border_row, from_=0.1, to=12, increment=0.1, width=6, textvariable=self.border_var
        )
        self.border_spin.pack(side="left", padx=(9, 4))
        ttk.Label(border_row, text="pt", style="Card.TLabel").pack(side="left")
        self.color_button = tk.Button(
            border_row,
            text="  선 색상  ",
            command=self._choose_color,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.BORDER,
            highlightcolor=self.ACCENT,
            cursor="hand2",
            background=f"#{self.color_var.get()}",
            foreground="white" if self._is_dark(self.color_var.get()) else "black",
            activebackground=self.ACCENT,
            activeforeground="white",
            font=(self.ui_font, 9),
        )
        self.color_button.pack(side="right")

        ttk.Separator(right).pack(fill="x", pady=(0, 10))
        ttk.Label(right, text="04  결과 저장", style="Section.TLabel").pack(anchor="w")
        ttk.Radiobutton(
            right,
            text="새 파일로 저장 (원본 보존)",
            value="copy",
            variable=self.output_mode_var,
            style="Card.TRadiobutton",
        ).pack(anchor="w", pady=(9, 2))
        ttk.Radiobutton(
            right,
            text="원본 덮어쓰기",
            value="overwrite",
            variable=self.output_mode_var,
            style="Card.TRadiobutton",
        ).pack(anchor="w", pady=(2, 7))
        output_row = ttk.Frame(right, style="Card.TFrame")
        output_row.pack(fill="x", pady=(3, 10))
        self.output_entry = ttk.Entry(output_row, textvariable=self.output_dir_var)
        self.output_entry.pack(side="left", fill="x", expand=True)
        self.output_button = ttk.Button(output_row, text="폴더", command=self._choose_output_dir)
        self.output_button.pack(side="right", padx=(7, 0))
        ttk.Label(
            right,
            text="비워 두면 원본과 같은 폴더에 '_사진정렬'로 저장",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(0, 9))

        ttk.Checkbutton(
            right,
            text="머리글·바닥글의 사진도 처리",
            variable=self.parts_var,
            style="Card.TCheckbutton",
        ).pack(anchor="w", pady=2)
        self.hwp_visible_checkbox = ttk.Checkbutton(
            right,
            text=(
                "HWP 처리 화면 표시 (문제 해결용)"
                if IS_WINDOWS
                else "HWP/HWPX는 Windows에서만 지원"
            ),
            variable=self.hwp_visible_var,
            style="Card.TCheckbutton",
        )
        self.hwp_visible_checkbox.pack(anchor="w", pady=2)
        if not IS_WINDOWS:
            self.hwp_visible_var.set(False)
            self.hwp_visible_checkbox.state(["disabled"])
        ttk.Checkbutton(
            right,
            text="Windows Defender 추가 검사 (권장)",
            variable=self.defender_var,
            style="Card.TCheckbutton",
        ).pack(anchor="w", pady=2)
        security_note = tk.Frame(right, background="#241013", padx=10, pady=7)
        security_note.pack(fill="x", pady=(7, 0))
        tk.Label(
            security_note,
            text="SECURITY GATE  ·  처리 전 검사 항상 실행",
            background="#241013",
            foreground="#FF6B73",
            font=(self.ui_font, 9, "bold"),
        ).pack(anchor="w")
        tk.Label(
            security_note,
            text="매크로·ActiveX·OLE·실행 파일·위험 링크·ZIP 폭탄 차단",
            background="#241013",
            foreground="#B8A3A6",
            font=(self.ui_font, 8),
        ).pack(anchor="w", pady=(2, 0))

        bottom = ttk.Frame(shell)
        bottom.grid(row=3, column=0, sticky="ew", padx=30, pady=(12, 16))
        status_box = ttk.Frame(bottom)
        status_box.pack(side="left", fill="x", expand=True)
        ttk.Label(status_box, textvariable=self.status_var).pack(anchor="w")
        ttk.Progressbar(
            status_box, maximum=100, variable=self.progress_var, style="Horizontal.TProgressbar"
        ).pack(fill="x", pady=(6, 0))
        self.start_button = ttk.Button(
            bottom, text="작업 시작", style="Accent.TButton", command=self._start
        )
        self.start_button.pack(side="right", padx=(18, 0))

    def _add_files(self) -> None:
        filetypes = (
            [
                ("지원 문서", "*.docx *.hwp *.hwpx"),
                ("Word 문서", "*.docx"),
                ("한글 문서", "*.hwp *.hwpx"),
            ]
            if IS_WINDOWS
            else [("Word 문서", "*.docx")]
        )
        names = filedialog.askopenfilenames(
            title="처리할 문서 선택",
            initialdir=self.settings.last_folder or None,
            filetypes=filetypes,
        )
        if names:
            self.settings.last_folder = str(Path(names[0]).parent)
            self._append_documents(Path(name) for name in names)

    def _add_folder(self) -> None:
        name = filedialog.askdirectory(
            title="문서 폴더 선택", initialdir=self.settings.last_folder or None
        )
        if not name:
            return
        self.settings.last_folder = name
        paths = collect_documents(Path(name), recursive=True)
        self._append_documents(paths)
        if not paths:
            messagebox.showinfo("W-Rookie", "선택한 폴더에 지원 문서가 없습니다.")

    def _append_documents(self, paths) -> None:
        known = set(self.documents)
        for path in paths:
            path = path.resolve()
            if not IS_WINDOWS and path.suffix.lower() in {".hwp", ".hwpx"}:
                continue
            if path in known or not is_supported(path):
                continue
            self.documents.append(path)
            known.add(path)
            item = self.tree.insert(
                "",
                "end",
                text=path.name,
                values=(path.suffix[1:].upper(), human_size(path.stat().st_size), "대기"),
            )
            self.row_by_path[path] = item
        self._refresh_count()

    def _remove_selected(self) -> None:
        if self.worker and self.worker.is_alive():
            return
        items = set(self.tree.selection())
        if not items:
            return
        self.documents = [p for p in self.documents if self.row_by_path.get(p) not in items]
        for path, item in list(self.row_by_path.items()):
            if item in items:
                self.tree.delete(item)
                del self.row_by_path[path]
        self._refresh_count()

    def _clear_files(self) -> None:
        if self.worker and self.worker.is_alive():
            return
        self.documents.clear()
        self.row_by_path.clear()
        self.tree.delete(*self.tree.get_children())
        self._refresh_count()

    def _refresh_count(self) -> None:
        total_size = sum(path.stat().st_size for path in self.documents if path.exists())
        self.count_label.configure(text=f"{len(self.documents)}개 · {human_size(total_size)}")
        if not self.documents:
            self.status_var.set("파일을 추가해 주세요")

    def _choose_color(self) -> None:
        color = colorchooser.askcolor(color=f"#{self.color_var.get()}", title="테두리 색상")
        if color[1]:
            value = color[1].lstrip("#").upper()
            self.color_var.set(value)
            self.color_button.configure(
                background=f"#{value}",
                foreground="white" if self._is_dark(value) else "black",
            )

    @staticmethod
    def _is_dark(color: str) -> bool:
        r, g, b = (int(color[i : i + 2], 16) for i in (0, 2, 4))
        return 0.299 * r + 0.587 * g + 0.114 * b < 145

    def _choose_output_dir(self) -> None:
        name = filedialog.askdirectory(title="결과 저장 폴더 선택")
        if name:
            self.output_dir_var.set(name)

    def _update_mode_hint(self, *_args) -> None:
        if self.align_var.get() == "smart":
            text = (
                "문단을 가로 중앙으로, 표 안 사진은 셀 세로 중앙으로 맞추며 문서 흐름을 유지합니다."
            )
        else:
            text = "사진을 페이지 가로·세로 정중앙으로 이동합니다. 같은 페이지의 여러 사진은 겹칠 수 있습니다."
        self.mode_hint.configure(text=text)

    def _update_resize_controls(self, *_args) -> None:
        enabled = self.resize_enabled_var.get() and self.inputs_enabled
        entry_state = "normal" if enabled else "disabled"
        combo_state = "readonly" if enabled else "disabled"
        self.resize_width_entry.configure(state=entry_state)
        self.resize_height_entry.configure(state=entry_state)
        self.resize_unit_combo.configure(state=combo_state)
        self.lock_aspect_check.state(["!disabled"] if enabled else ["disabled"])

    def _update_output_controls(self, *_args) -> None:
        state = "normal" if self.output_mode_var.get() == "copy" else "disabled"
        self.output_entry.configure(state=state)
        self.output_button.configure(state=state)

    def _build_job_options(self) -> JobOptions:
        output_dir = (
            Path(self.output_dir_var.get()).expanduser() if self.output_dir_var.get() else None
        )
        width_mm = None
        height_mm = None
        if self.resize_enabled_var.get():
            width = self._optional_size(self.resize_width_var.get(), "가로")
            height = self._optional_size(self.resize_height_var.get(), "세로")
            if width is None and height is None:
                raise ValueError("크기 조절을 사용하려면 가로 또는 세로 값을 입력하세요.")
            factor = 10.0 if self.resize_unit_var.get() == "cm" else 1.0
            width_mm = width * factor if width is not None else None
            height_mm = height * factor if height is not None else None
        return JobOptions(
            align_mode=AlignMode(self.align_var.get()),
            resize_width_mm=width_mm,
            resize_height_mm=height_mm,
            lock_aspect_ratio=self.lock_aspect_var.get(),
            border=BorderStyle(float(self.border_var.get()), self.color_var.get()),
            output_mode=OutputMode(self.output_mode_var.get()),
            output_dir=output_dir,
            include_headers_footers=self.parts_var.get(),
            hwp_visible=self.hwp_visible_var.get(),
            security_scan=True,
            windows_defender_scan=self.defender_var.get(),
        )

    @staticmethod
    def _optional_size(raw: str, label: str) -> float | None:
        value = raw.strip().replace(",", ".")
        if not value:
            return None
        try:
            number = float(value)
        except ValueError as exc:
            raise ValueError(f"{label} 크기는 숫자로 입력하세요.") from exc
        if number <= 0:
            raise ValueError(f"{label} 크기는 0보다 커야 합니다.")
        return number

    def _start(self) -> None:
        if self.worker and self.worker.is_alive():
            self.cancel_event.set()
            self.start_button.configure(text="취소 중…", state="disabled")
            return
        if not self.documents:
            messagebox.showinfo("W-Rookie", "먼저 처리할 문서를 추가해 주세요.")
            return
        try:
            options = self._build_job_options()
        except (ValueError, OSError) as exc:
            messagebox.showerror("설정 확인", f"설정을 확인해 주세요.\n\n{exc}")
            return
        if options.output_mode is OutputMode.OVERWRITE and not messagebox.askyesno(
            "원본 덮어쓰기",
            "원본 파일을 새 결과로 교체합니다. 계속할까요?\n\n중요 문서는 먼저 백업하는 것을 권장합니다.",
            icon="warning",
        ):
            return
        if options.align_mode is AlignMode.PAGE and not messagebox.askyesno(
            "페이지 기준 배치",
            "같은 페이지에 사진이 여러 개면 중앙에서 겹칠 수 있습니다. 계속할까요?",
            icon="warning",
        ):
            return
        self._save_settings()
        self.cancel_event.clear()
        self.progress_var.set(0)
        self.start_button.configure(text="작업 취소")
        self._set_inputs_enabled(False)
        paths = list(self.documents)
        self.worker = threading.Thread(
            target=self._run_batch, args=(paths, options), name="document-worker", daemon=True
        )
        self.worker.start()

    def _run_batch(self, paths: list[Path], options: JobOptions) -> None:
        succeeded = 0
        for index, path in enumerate(paths):
            if self.cancel_event.is_set():
                break
            self.events.put(("status", path, "처리 중", "working"))

            def report(value: float, message: str, i=index, p=path) -> None:
                overall = (i + value) / len(paths) * 100
                self.events.put(("progress", overall, f"{p.name} · {message}"))

            result = self.service.process_one(
                path,
                options,
                progress=report,
                cancelled=self.cancel_event.is_set,
            )
            if result.success:
                succeeded += 1
                warning_mark = " ⚠" if result.warnings else ""
                label = f"완료 ({result.pictures_changed}){warning_mark}"
                self.events.put(("status", path, label, "success"))
            else:
                if self.cancel_event.is_set():
                    label = "취소"
                elif result.error and result.error.startswith("보안 검사에서 차단"):
                    label = "보안 차단"
                else:
                    label = "실패"
                self.events.put(("status", path, label, "error"))
            self.events.put(("result", result))
        self.events.put(("done", succeeded, len(paths), self.cancel_event.is_set()))

    def _drain_events(self) -> None:
        try:
            while True:
                event = self.events.get_nowait()
                kind = event[0]
                if kind == "progress":
                    self.progress_var.set(event[1])
                    self.status_var.set(event[2])
                elif kind == "status":
                    _, path, label, tag = event
                    item = self.row_by_path.get(path)
                    if item:
                        values = list(self.tree.item(item, "values"))
                        values[2] = label
                        self.tree.item(item, values=values, tags=(tag,))
                        self.tree.see(item)
                elif kind == "result":
                    result = event[1]
                    if result.success:
                        warning = f" · ⚠ {result.warnings[0]}" if result.warnings else ""
                        self.status_var.set(
                            f"{result.source.name} 완료 · 사진 {result.pictures_changed}개{warning}"
                        )
                    else:
                        self.status_var.set(f"{result.source.name} · {result.error}")
                elif kind == "done":
                    _, succeeded, total, cancelled = event
                    self._set_inputs_enabled(True)
                    self.start_button.configure(text="작업 시작", state="normal")
                    if cancelled:
                        self.status_var.set(f"작업 취소 · {succeeded}/{total}개 완료")
                    else:
                        self.progress_var.set(100)
                        self.status_var.set(f"전체 완료 · {succeeded}/{total}개 성공")
                        if succeeded == total:
                            messagebox.showinfo("W-Rookie", f"문서 {total}개 처리를 완료했습니다.")
        except queue.Empty:
            pass
        self.after(100, self._drain_events)

    def _set_inputs_enabled(self, enabled: bool) -> None:
        self.inputs_enabled = enabled
        self.tree.configure(selectmode="extended" if enabled else "none")
        self.border_spin.configure(state="normal" if enabled else "disabled")
        self.color_button.configure(state="normal" if enabled else "disabled")
        state = ["!disabled"] if enabled else ["disabled"]
        self.smart_radio.state(state)
        self.page_radio.state(state)
        self.resize_enabled_check.state(state)
        self._update_resize_controls()

    def _diagnose(self) -> None:
        rows = diagnose_environment()
        text = "\n".join(
            f"{'✓' if ok else '!'}  {name}\n    {message}" for name, ok, message in rows
        )
        messagebox.showinfo("환경 진단", text)

    def _show_help(self) -> None:
        format_note = (
            "HWP/HWPX는 Windows와 설치된 한/글, pywin32가 필요합니다."
            if IS_WINDOWS
            else "macOS/Linux에서는 DOCX를 지원합니다. HWP/HWPX는 Windows 전용입니다."
        )
        messagebox.showinfo(
            "빠른 사용법",
            "1. 파일 추가 또는 폴더 추가\n"
            "2. 필요하면 사진 가로·세로 크기를 mm/cm로 입력\n"
            "3. 스마트 중앙 정렬과 1pt를 그대로 사용\n"
            "4. 작업 시작\n\n"
            "DOCX는 별도 프로그램 없이 처리됩니다.\n"
            f"{format_note}\n"
            "첫 테스트는 반드시 새 파일로 저장을 권장합니다.",
        )

    def _show_security_help(self) -> None:
        messagebox.showinfo(
            "보안 검사",
            "모든 파일은 문서 처리 전에 정적 보안 검사를 통과해야 합니다.\n\n"
            "자동 차단:\n"
            "• 매크로, ActiveX, OLE 첨부 개체\n"
            "• EXE, DLL, 스크립트 등 실행 가능한 payload\n"
            "• 경로 조작, 중복 항목, 암호화 항목\n"
            "• 비정상 압축률과 ZIP 폭탄\n"
            "• DTD/XML 외부 엔터티와 위험한 외부 링크\n\n"
            "Windows Defender 옵션을 켜면 운영체제 백신 검사도 추가합니다. "
            "보안 검사는 완벽한 백신을 대체하지 않으므로 Windows와 Office를 최신 상태로 유지하세요.",
        )

    def _save_settings(self) -> None:
        try:
            width = float(self.border_var.get())
        except ValueError:
            width = 1.0
        self.settings.align_mode = self.align_var.get()
        self.settings.resize_enabled = self.resize_enabled_var.get()
        self.settings.resize_width = self.resize_width_var.get()
        self.settings.resize_height = self.resize_height_var.get()
        self.settings.resize_unit = self.resize_unit_var.get()
        self.settings.lock_aspect_ratio = self.lock_aspect_var.get()
        self.settings.border_width = width
        self.settings.border_color = self.color_var.get()
        self.settings.output_mode = self.output_mode_var.get()
        self.settings.output_dir = self.output_dir_var.get()
        self.settings.include_headers_footers = self.parts_var.get()
        self.settings.hwp_visible = self.hwp_visible_var.get()
        self.settings.security_scan = True
        self.settings.windows_defender_scan = self.defender_var.get()
        with contextlib.suppress(OSError):
            self.settings.save()

    def _on_close(self) -> None:
        if self.worker and self.worker.is_alive():
            if not messagebox.askyesno("작업 중", "진행 중인 작업을 취소하고 종료할까요?"):
                return
            self.cancel_event.set()
        self._save_settings()
        self.destroy()


def main() -> int:
    app = WRookieApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
