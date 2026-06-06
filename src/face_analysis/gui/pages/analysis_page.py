"""Main analysis page: image display, feature selectors, and result output.

Layout (top to bottom):
- Fixed header bar with Back / Exit buttons and the client's name.
- Scrollable body containing:
    - :class:`~face_analysis.gui.widgets.feature_input.FeatureInputGrid` —
      live weight editor.
    - Two-column middle row: image canvases (original + landmark) on the left,
      :class:`~face_analysis.gui.widgets.radio_selector.RadioSelectorPanel` on
      the right.
    - Results card showing common/missing archetype labels.

Submitting the form runs the full pipeline: archetype analysis → PDF generation
→ session logging.
"""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from face_analysis.config.feature_weights import FeatureWeightsStore
from face_analysis.core.analyzer import (
    analyze_archetypes,
    build_result_texts,
    find_common_archetypes,
)
from face_analysis.core.logger import get_session, init_session
from face_analysis.core.pdf_generator import generate_pdf
from face_analysis.gui.theme import COLORS, FONTS, SPACE
from face_analysis.gui.widgets.feature_input import FeatureInputGrid
from face_analysis.gui.widgets.radio_selector import RadioSelectorPanel
from face_analysis.vision.face_mesh import draw_face_mesh
from face_analysis.vision.image_utils import open_image_dialog

_CANVAS_W = 300
_CANVAS_H = 200


class AnalysisPage(ttk.Frame):
    """Main analysis page: weight editor, image display, radio selectors, result labels."""

    def __init__(
        self,
        parent: tk.Widget,
        store: FeatureWeightsStore,
        username: str,
        on_back: Callable[[], None],
        on_exit: Callable[[], None],
        **kwargs: object,
    ) -> None:
        super().__init__(parent, style="TFrame", **kwargs)
        self._store = store
        self._username = username
        self._on_back = on_back
        self._on_exit = on_exit

        self._eyebrow_var = tk.StringVar()
        self._nose_var = tk.StringVar()
        self._lips_var = tk.StringVar()
        self._common_var = tk.StringVar(value="نتیجه‌ای هنوز ساخته نشده است.")
        self._missing_var = tk.StringVar()

        self._image_file_path: str | None = None
        self._landmark_file_path: str | None = None

        self._build()

    # ------------------------------------------------------------------
    def _build(self) -> None:
        self._build_header()

        # Scrollable viewport.
        viewport = tk.Frame(self, bg=COLORS["bg"])
        viewport.pack(expand=True, fill="both")

        scrollbar = ttk.Scrollbar(viewport, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self._scroll_canvas = tk.Canvas(
            viewport,
            bg=COLORS["bg"],
            highlightthickness=0,
            yscrollcommand=scrollbar.set,
        )
        self._scroll_canvas.pack(side="left", expand=True, fill="both")
        scrollbar.config(command=self._scroll_canvas.yview)

        body = ttk.Frame(self._scroll_canvas, style="TFrame")
        self._scroll_window = self._scroll_canvas.create_window(
            (0, 0), window=body, anchor="nw"
        )

        body.bind("<Configure>", self._on_body_configure)
        self._scroll_canvas.bind("<Configure>", self._on_canvas_configure)
        self._scroll_canvas.bind("<MouseWheel>", self._on_mousewheel)
        body.bind("<MouseWheel>", self._on_mousewheel)

        body.columnconfigure(0, weight=1)

        inner = ttk.Frame(body, style="TFrame")
        inner.pack(expand=True, fill="both", padx=SPACE["lg"], pady=SPACE["md"])

        # Weight editor card.
        FeatureInputGrid(inner, self._store).pack(fill="x", pady=(0, SPACE["md"]))

        # Middle section: radio selectors (right) + image card (left).
        middle = ttk.Frame(inner, style="TFrame")
        middle.pack(expand=True, fill="both")
        middle.columnconfigure(0, weight=1, uniform="cols")
        middle.columnconfigure(1, weight=1, uniform="cols")
        middle.rowconfigure(0, weight=1)

        # Image card on the left column.
        self._build_image_card(middle).grid(
            row=0, column=0, padx=(0, SPACE["sm"]), sticky="nsew"
        )

        # Radio selectors on the right column (primary RTL focus).
        RadioSelectorPanel(
            middle,
            eyebrow_var=self._eyebrow_var,
            nose_var=self._nose_var,
            lips_var=self._lips_var,
            on_submit=self._on_submit,
        ).grid(row=0, column=1, padx=(SPACE["sm"], 0), sticky="nsew")

        # Results card.
        self._build_results_card(inner).pack(fill="x", pady=(SPACE["md"], 0))

    # ------------------------------------------------------------------
    def _on_body_configure(self, _: tk.Event) -> None:  # type: ignore[type-arg]
        self._scroll_canvas.configure(scrollregion=self._scroll_canvas.bbox("all"))

    def _on_canvas_configure(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        self._scroll_canvas.itemconfig(self._scroll_window, width=event.width)

    def _on_mousewheel(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        self._scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ------------------------------------------------------------------
    def _build_header(self) -> None:
        """Render the top bar with navigation buttons and client name."""
        header = ttk.Frame(self, style="Header.TFrame")
        header.pack(fill="x")
        inner = ttk.Frame(header, style="Header.TFrame")
        inner.pack(fill="x", padx=SPACE["lg"], pady=SPACE["md"])

        # Navigation buttons on the left.
        ttk.Button(
            inner,
            text="خروج",
            style="Danger.TButton",
            command=self._on_exit,
        ).pack(side="left")
        ttk.Button(
            inner,
            text="بازگشت",
            style="Secondary.TButton",
            command=self._on_back,
        ).pack(side="left", padx=SPACE["sm"])

        # Title / user on the right.
        title_box = ttk.Frame(inner, style="Header.TFrame")
        title_box.pack(side="right")
        ttk.Label(
            title_box,
            text="تحلیل چهره",
            style="Heading.TLabel",
            anchor="e",
        ).pack(anchor="e")
        user = self._username.strip() or "کاربر مهمان"
        ttk.Label(
            title_box,
            text=f"مراجعه‌کننده: {user}",
            style="Muted.TLabel",
            anchor="e",
        ).pack(anchor="e")

        ttk.Separator(self, orient="horizontal").pack(fill="x")

    # ------------------------------------------------------------------
    def _build_image_card(self, parent: tk.Widget) -> ttk.Frame:
        """Build and return the card containing the two image canvases and the open-file button."""
        card = ttk.Frame(parent, style="Card.TFrame")

        ttk.Label(
            card,
            text="تصویر چهره",
            style="Subheading.TLabel",
            anchor="e",
        ).pack(fill="x", padx=SPACE["md"], pady=(SPACE["md"], SPACE["sm"]))

        canvases = ttk.Frame(card, style="Card.TFrame")
        canvases.pack(padx=SPACE["md"])

        self._image_canvas = self._make_canvas(canvases, "تصویر اصلی")
        self._image_canvas.grid(row=0, column=1, padx=SPACE["xs"], pady=SPACE["xs"])

        self._landmark_canvas = self._make_canvas(canvases, "نقاط چهره")
        self._landmark_canvas.grid(row=0, column=0, padx=SPACE["xs"], pady=SPACE["xs"])

        ttk.Button(
            card,
            text="انتخاب تصویر",
            style="Secondary.TButton",
            command=self._insert_image,
        ).pack(padx=SPACE["md"], pady=SPACE["md"])

        return card

    def _make_canvas(self, parent: tk.Widget, placeholder: str) -> tk.Canvas:
        """Create a fixed-size canvas with a centred placeholder text label."""
        canvas = tk.Canvas(
            parent,
            width=_CANVAS_W,
            height=_CANVAS_H,
            bg=COLORS["field"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            bd=0,
        )
        canvas.create_text(
            _CANVAS_W / 2,
            _CANVAS_H / 2,
            text=placeholder,
            fill=COLORS["text_muted"],
            font=FONTS["body"],
            tags="placeholder",
        )
        return canvas

    # ------------------------------------------------------------------
    def _build_results_card(self, parent: tk.Widget) -> ttk.Frame:
        """Build and return the card that displays the common and missing archetype labels."""
        card = ttk.Frame(parent, style="Card.TFrame")

        ttk.Label(
            card,
            text="نتیجهٔ تحلیل",
            style="Subheading.TLabel",
            anchor="e",
        ).pack(fill="x", padx=SPACE["md"], pady=(SPACE["md"], SPACE["sm"]))

        ttk.Label(
            card,
            textvariable=self._common_var,
            style="Result.TLabel",
            anchor="e",
            justify="right",
            wraplength=900,
        ).pack(fill="x", padx=SPACE["md"], pady=SPACE["xs"])
        ttk.Label(
            card,
            textvariable=self._missing_var,
            style="Muted.TLabel",
            anchor="e",
            justify="right",
            wraplength=900,
        ).pack(fill="x", padx=SPACE["md"], pady=(SPACE["xs"], SPACE["md"]))

        return card

    # ------------------------------------------------------------------
    def _insert_image(self) -> None:
        """Open the file picker, display the chosen image, and run face-mesh detection."""
        if get_session() is None:
            init_session(self._username)

        file_path, img = open_image_dialog()
        if file_path is None:
            return
        self._image_file_path = file_path
        self._show_on_canvas(self._image_canvas, img)

        result = draw_face_mesh(file_path)
        if result:
            landmark_path, landmark_img = result
            self._landmark_file_path = landmark_path
            self._show_on_canvas(self._landmark_canvas, landmark_img)

    @staticmethod
    def _show_on_canvas(canvas: tk.Canvas, img: object) -> None:
        canvas.delete("placeholder")
        canvas.create_image(0, 0, anchor="nw", image=img)
        canvas.image = img  # type: ignore[attr-defined]

    def _on_submit(self) -> None:
        """Run the full analysis pipeline and update result labels + PDF on submit."""
        session = get_session() or init_session(self._username)

        eyebrow = self._eyebrow_var.get()
        lips = self._lips_var.get()
        nose = self._nose_var.get()
        session.log(
            "info",
            "Analysis submitted — eyebrow=%s  lips=%s  nose=%s",
            eyebrow,
            lips,
            nose,
        )

        archetype_ids = analyze_archetypes(eyebrow, lips, nose, self._store)
        session.log("debug", "Archetype IDs from features: %s", archetype_ids)

        common, missing = find_common_archetypes([archetype_ids])
        session.log("info", "Common archetypes: %s  |  Missing: %s", common, missing)

        texts = build_result_texts(common, missing)

        self._common_var.set(texts["common_text"])
        self._missing_var.set(texts["missing_text"])

        # Images already stored in session dirs by image_utils / face_mesh.
        generate_pdf(
            texts, self._username, self._image_file_path, self._landmark_file_path
        )
        session.log("info", "Analysis complete")
