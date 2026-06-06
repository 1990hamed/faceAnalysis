"""Static archetype data: names, personality features, and therapeutic methods.

All text is in Farsi. There are seven archetypes (IDs 1–7) based on Greek myth
pairs. Each archetype carries three lookup tables:

- :data:`ARCHETYPE_NAMES` — display name shown in the UI and PDF.
- :data:`ARCHETYPE_FEATURES_MAN` / :data:`ARCHETYPE_FEATURES_WOMAN` — personality
  traits by gender.
- :data:`ARCHETYPE_METHODS` — recommended therapeutic approach.
- :data:`ALL_ARCHETYPE_IDS` — frozen set of valid IDs; used for validation and
  computing the complement ("missing archetypes").
"""

ARCHETYPE_NAMES: dict[int, str] = {
    1: "پرسفون و هفائستوس و دیونیسوس 1",
    2: "2 دیمیتر و پوزیدون",
    3: "3 آتنا و آپولو",
    4: "4 آفرودیت و آرسا",
    5: "5 هستیا و هرمس",
    6: "6 آرتمیس و هادس",
    7: "7 هرا و زئوس",
}

ARCHETYPE_FEATURES_MAN: dict[int, str] = {
    1: "یاری رسان، پرتلاش، زحمت کش،  آسان گیر، راحت، بی خیال، هر چیزی را جدی نمیگیرد",
    2: "دنبال گرفتن حق خود، حساس",
    3: "برنامه ریز، آینده نگر، باهوش",
    4: "زندگی در لحظه، به دنبال شادی و صفا، با معرفت",
    5: "توانایی استفاده از فرصت ها، سخن ور",
    6: "پر از علامت سؤال، پیچیده و ناشناخته",
    7: "دنبال پول و قدرت، مدیر، سردسته",
}

ARCHETYPE_FEATURES_WOMAN: dict[int, str] = {
    1: "جوان، بی خیال، دل نشین، افسرده",
    2: "بچه، مادر، دلسوز",
    3: "عاقل، همکار، بیمار کار",
    4: "باحال، عاشق، پرستو",
    5: "ساکت، غیر اجتماعی",
    6: "حیوان دوست، نقش خواهر، شاد",
    7: "اهل ازدواج، سوار بر شوهر، ناپایدار",
}

ARCHETYPE_METHODS: dict[int, str] = {
    1: "روانکاوی",
    2: "آدلری",
    3: "وجودی شناختی رفتاری",
    4: "گشتالتی",
    5: "فرد مدار پست مدرن",
    6: "واقعیت درمانی رفتار درمانی",
    7: "فمینیستی",
}

ALL_ARCHETYPE_IDS: frozenset[int] = frozenset(ARCHETYPE_NAMES)
