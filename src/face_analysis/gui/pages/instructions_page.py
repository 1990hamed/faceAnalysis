"""Instructions page shown between the landing screen and the analysis page.

Displays a welcome message and a numbered list of usage steps so the operator
knows how to select features, run the analysis, and navigate between clients.
"""

import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from face_analysis.gui.theme import SPACE

_WELCOME = "به نرم‌افزار تحلیل چهره خوش آمدید!"

_STEPS = (
    "برای تغییر ضرایب، اعداد را ویرایش کرده و دکمه «به‌روزرسانی ضرایب» را بزنید.",
    "ویژگی‌های چهرهٔ مراجعه‌کننده را انتخاب و سپس «تأیید و تحلیل» را بزنید تا گزارش "
    "آرکیتایپ ساخته شود.",
    "برای تحلیل مراجعه‌کنندهٔ جدید، دکمه «بازگشت» را بزنید.",
    "برای بستن برنامه، دکمه «خروج» را بزنید.",
)


class InstructionsPage(ttk.Frame):
    """Informational page shown after the username is confirmed."""

    def __init__(
        self,
        parent: tk.Widget,
        on_continue: Callable[[], None],
        **kwargs: object,
    ) -> None:
        super().__init__(parent, style="TFrame", **kwargs)
        self._on_continue = on_continue
        self._build()

    def _build(self) -> None:
        card = ttk.Frame(self, style="Card.TFrame")
        card.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(
            card,
            text=_WELCOME,
            style="Heading.TLabel",
            anchor="e",
        ).pack(fill="x", padx=SPACE["xl"], pady=(SPACE["xl"], SPACE["lg"]))

        steps_frame = ttk.Frame(card, style="Card.TFrame")
        steps_frame.pack(fill="x", padx=SPACE["xl"], pady=(0, SPACE["lg"]))

        for step in _STEPS:
            row = ttk.Frame(steps_frame, style="Card.TFrame")
            row.pack(fill="x", pady=SPACE["xs"])
            # Bullet on the right for RTL reading order.
            ttk.Label(
                row,
                text=step,
                style="Surface.TLabel",
                anchor="e",
                justify="right",
                wraplength=560,
            ).pack(side="right", fill="x", expand=True)
            ttk.Label(
                row,
                text="◆",
                style="Result.TLabel",
            ).pack(side="right", padx=SPACE["sm"])

        ttk.Button(
            card,
            text="ادامه",
            style="Accent.TButton",
            command=self._on_continue,
        ).pack(padx=SPACE["xl"], pady=(0, SPACE["xl"]))
