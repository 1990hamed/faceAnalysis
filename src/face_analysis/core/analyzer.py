"""Core analysis logic: map facial features to archetypes and build result strings.

The pipeline is intentionally pure (no I/O, no GUI imports):

1. :func:`analyze_archetypes` — look up each selected feature in the weight store
   and collect the associated archetype IDs into a flat list.
2. :func:`find_common_archetypes` — intersect per-feature ID lists to find which
   archetypes appear across all features; falls back to high-frequency IDs when
   there is no intersection.
3. :func:`build_result_texts` — format the common/missing archetypes plus their
   personality traits and therapeutic methods into display-ready Farsi strings.
"""

from collections import Counter

from face_analysis.config.archetypes import (
    ALL_ARCHETYPE_IDS,
    ARCHETYPE_FEATURES_MAN,
    ARCHETYPE_FEATURES_WOMAN,
    ARCHETYPE_METHODS,
    ARCHETYPE_NAMES,
)
from face_analysis.config.feature_weights import FeatureWeightsStore


def analyze_archetypes(
    eyebrow_type: str,
    lips_type: str,
    nose_type: str,
    store: FeatureWeightsStore,
) -> list[int]:
    """Return archetype IDs associated with the three selected feature types."""
    result: list[int] = []
    for feature in (eyebrow_type, lips_type, nose_type):
        raw = store.get(feature)
        if raw:
            result.extend(int(n.strip()) for n in raw.split(",") if n.strip().isdigit())
    return result


def find_common_archetypes(
    result_array: list[list[int]],
) -> tuple[list[int], list[int]]:
    """Return (common_archetypes, missing_archetypes) from a per-feature result array."""
    if not result_array or not result_array[0]:
        return [], sorted(ALL_ARCHETYPE_IDS)

    common = list(set.intersection(*map(set, result_array)))
    if not common:
        # fall back to archetypes that appear more than once in the first row
        common = [item for item, count in Counter(result_array[0]).items() if count > 1]

    missing = [i for i in sorted(ALL_ARCHETYPE_IDS) if i not in common]
    return common, missing


def build_result_texts(
    common_archetypes: list[int],
    missing_archetypes: list[int],
) -> dict[str, str]:
    """Build display/PDF strings for the analysis result."""
    common_names = [
        ARCHETYPE_NAMES.get(a, f"آرکتایپ مشترک {a}") for a in common_archetypes
    ]
    missing_names = [
        ARCHETYPE_NAMES.get(a, f"آرکتایپ گم‌شده {a}") for a in missing_archetypes
    ]
    method_names = [
        ARCHETYPE_METHODS.get(a, f"متد روانشناسی {a}") for a in common_archetypes
    ]
    man_features = [
        ARCHETYPE_FEATURES_MAN.get(a, f"خصوصیت مردانه {a}") for a in common_archetypes
    ]
    woman_features = [
        ARCHETYPE_FEATURES_WOMAN.get(a, f"خصوصیت زنانه {a}") for a in common_archetypes
    ]

    return {
        "common_text": "آرکتایپ‌های مشترک: " + ", ".join(common_names)
        if common_names
        else "هیچ آرکتایپی یافت نشد",
        "missing_text": "آرکتایپ‌های اضافه شده: " + ", ".join(missing_names)
        if missing_names
        else "هیچ آرکتایپی اضافه‌ای ندارد",
        "method_text": "روش روانشناسی برای شخص: " + ", ".join(method_names)
        if method_names
        else "روشی وجود ندارد",
        "man_feature_text": "شخصیت مردانه شخص: " + ", ".join(man_features)
        if man_features
        else "خصوصیت مردانه نمیتوان تشخیص داد",
        "woman_feature_text": "شخصیت زنانه شخص: " + ", ".join(woman_features)
        if woman_features
        else "خصوصیت زنانه نمیتوان تشخیص داد",
    }
