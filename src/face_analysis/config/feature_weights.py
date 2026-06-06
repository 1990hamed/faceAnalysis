"""Feature-to-archetype weight store with runtime validation.

:data:`_DEFAULT_WEIGHTS` maps each facial-feature label (in Farsi) to a
comma-separated string of archetype IDs (1–7).  :class:`FeatureWeightsStore`
wraps this mapping and is the single mutable state object passed through the app;
every page that needs to read or update weights holds a reference to the same
instance.
"""

from tkinter import messagebox

_DEFAULT_WEIGHTS: dict[str, str] = {
    "کمانی": "1, 4",
    "کوچک": "1",
    "قلوه": "1, 2",
    "صاف": "3, 7",
    "بزرگ": "2, 3, 4, 7",
    "نازک": "1, 6",
    "باریک": "1",
    "تیز": "3, 6, 7",
    "هر دو": "3, 5, 7",
    "پیوسته": "3, 7",
    "عقابی": "7",
}


class FeatureWeightsStore:
    """Single mutable store for feature-to-archetype weight mappings."""

    def __init__(self) -> None:
        self._weights: dict[str, str] = dict(_DEFAULT_WEIGHTS)

    def get(self, feature: str) -> str | None:
        return self._weights.get(feature)

    def all(self) -> dict[str, str]:
        return dict(self._weights)

    def update(self, feature: str, raw_value: str) -> bool:
        """Validate and apply a new mapping for *feature*.

        Returns True on success, False (and shows an error dialog) on invalid input.
        """
        cleaned = raw_value.replace(" ", "")
        numbers = cleaned.split(",")
        if all(n.isdigit() and 1 <= int(n) <= 7 for n in numbers if n):
            self._weights[feature] = cleaned
            return True
        messagebox.showerror(
            "خطا",
            f"مقدار وارد شده برای {feature} باید شامل اعداد بین ۱ تا ۷ باشد و با کاما جدا شود.",
        )
        return False

    def update_many(self, entries: dict[str, str]) -> bool:
        """Validate all entries first, then apply. Shows success dialog."""
        validated: dict[str, str] = {}
        for feature, raw in entries.items():
            cleaned = raw.replace(" ", "")
            numbers = cleaned.split(",")
            if not all(n.isdigit() and 1 <= int(n) <= 7 for n in numbers if n):
                messagebox.showerror(
                    "خطا",
                    f"مقدار وارد شده برای {feature} باید شامل اعداد بین ۱ تا ۷ باشد و با کاما جدا شود.",
                )
                return False
            validated[feature] = cleaned
        self._weights.update(validated)
        messagebox.showinfo("موفقیت", "خصوصیات با موفقیت به‌روزرسانی شدند.")
        return True
