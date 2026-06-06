"""Tests for core/analyzer.py: analyze_archetypes, find_common_archetypes, build_result_texts."""

import pytest

from face_analysis.config.archetypes import ALL_ARCHETYPE_IDS
from face_analysis.config.feature_weights import FeatureWeightsStore
from face_analysis.core.analyzer import (
    analyze_archetypes,
    build_result_texts,
    find_common_archetypes,
)


@pytest.fixture()
def store():
    return FeatureWeightsStore()


# ---------------------------------------------------------------------------
# analyze_archetypes
# ---------------------------------------------------------------------------


def test_analyze_archetypes_known_features(store):
    # "کمانی" -> "1, 4",  "کوچک" -> "1",  "قلوه" -> "1, 2"
    result = analyze_archetypes("کمانی", "کوچک", "قلوه", store)
    assert sorted(result) == sorted([1, 4, 1, 1, 2])


def test_analyze_archetypes_unknown_feature_ignored(store):
    result = analyze_archetypes("کمانی", "nonexistent", "کوچک", store)
    # Only "کمانی" (1,4) and "کوچک" (1) contribute
    assert sorted(result) == sorted([1, 4, 1])


def test_analyze_archetypes_all_unknown_returns_empty(store):
    result = analyze_archetypes("x", "y", "z", store)
    assert result == []


# ---------------------------------------------------------------------------
# find_common_archetypes
# ---------------------------------------------------------------------------


def test_find_common_archetypes_single_common():
    result = find_common_archetypes([[1, 4], [1, 2], [1, 3]])
    common, missing = result
    assert 1 in common
    assert 1 not in missing


def test_find_common_archetypes_no_intersection_falls_back():
    # No element appears in all three sets, but 1 appears twice in first row
    result = find_common_archetypes([[1, 1, 2], [3, 4], [5, 6]])
    common, missing = result
    # Fallback: items with count > 1 in result_array[0] -> [1]
    assert common == [1]


def test_find_common_archetypes_empty_input():
    common, missing = find_common_archetypes([])
    assert common == []
    assert missing == sorted(ALL_ARCHETYPE_IDS)


def test_find_common_archetypes_empty_first_row():
    common, missing = find_common_archetypes([[]])
    assert common == []
    assert missing == sorted(ALL_ARCHETYPE_IDS)


def test_missing_archetypes_complement_common():
    common, missing = find_common_archetypes([[1, 2, 3], [1, 2, 3]])
    all_ids = sorted(ALL_ARCHETYPE_IDS)
    assert sorted(common + missing) == all_ids


# ---------------------------------------------------------------------------
# build_result_texts
# ---------------------------------------------------------------------------


def test_build_result_texts_with_archetypes():
    texts = build_result_texts([1, 3], [2, 4, 5, 6, 7])
    assert "آرکتایپ‌های مشترک:" in texts["common_text"]
    assert "آرکتایپ‌های اضافه شده:" in texts["missing_text"]
    assert "روش روانشناسی" in texts["method_text"]
    assert "شخصیت مردانه" in texts["man_feature_text"]
    assert "شخصیت زنانه" in texts["woman_feature_text"]


def test_build_result_texts_no_common_archetypes():
    texts = build_result_texts([], list(ALL_ARCHETYPE_IDS))
    assert texts["common_text"] == "هیچ آرکتایپی یافت نشد"
    assert texts["method_text"] == "روشی وجود ندارد"
    assert texts["man_feature_text"] == "خصوصیت مردانه نمیتوان تشخیص داد"
    assert texts["woman_feature_text"] == "خصوصیت زنانه نمیتوان تشخیص داد"


def test_build_result_texts_no_missing_archetypes():
    texts = build_result_texts(list(ALL_ARCHETYPE_IDS), [])
    assert texts["missing_text"] == "هیچ آرکتایپی اضافه‌ای ندارد"


def test_build_result_texts_unknown_archetype_id_uses_fallback():
    texts = build_result_texts([99], [])
    assert "99" in texts["common_text"]
