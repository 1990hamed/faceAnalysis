"""Tests for config/feature_weights.py: FeatureWeightsStore CRUD and validation."""

from face_analysis.config.feature_weights import FeatureWeightsStore


def test_get_known_feature():
    store = FeatureWeightsStore()
    assert store.get("کمانی") == "1, 4"


def test_get_unknown_feature_returns_none():
    store = FeatureWeightsStore()
    assert store.get("nonexistent") is None


def test_all_returns_copy_of_defaults():
    store = FeatureWeightsStore()
    weights = store.all()
    assert "کمانی" in weights
    # Mutating the returned dict must not affect the store
    weights["کمانی"] = "99"
    assert store.get("کمانی") == "1, 4"


def test_update_valid_value(monkeypatch):
    store = FeatureWeightsStore()
    # Patch messagebox to prevent GUI calls
    monkeypatch.setattr(
        "face_analysis.config.feature_weights.messagebox.showerror",
        lambda *a, **kw: None,
    )
    result = store.update("کمانی", "2, 5")
    assert result is True
    assert store.get("کمانی") == "2,5"


def test_update_invalid_value_returns_false(monkeypatch):
    store = FeatureWeightsStore()
    monkeypatch.setattr(
        "face_analysis.config.feature_weights.messagebox.showerror",
        lambda *a, **kw: None,
    )
    result = store.update("کمانی", "0, 8")  # 0 and 8 are out of range 1–7
    assert result is False
    assert store.get("کمانی") == "1, 4"  # unchanged


def test_update_adds_new_feature(monkeypatch):
    store = FeatureWeightsStore()
    monkeypatch.setattr(
        "face_analysis.config.feature_weights.messagebox.showerror",
        lambda *a, **kw: None,
    )
    result = store.update("new_feature", "3")
    assert result is True
    assert store.get("new_feature") == "3"


def test_update_many_valid(monkeypatch):
    store = FeatureWeightsStore()
    monkeypatch.setattr(
        "face_analysis.config.feature_weights.messagebox.showerror",
        lambda *a, **kw: None,
    )
    monkeypatch.setattr(
        "face_analysis.config.feature_weights.messagebox.showinfo",
        lambda *a, **kw: None,
    )
    result = store.update_many({"کمانی": "1", "صاف": "2, 4"})
    assert result is True
    assert store.get("کمانی") == "1"
    assert store.get("صاف") == "2,4"


def test_update_many_invalid_rolls_back(monkeypatch):
    store = FeatureWeightsStore()
    monkeypatch.setattr(
        "face_analysis.config.feature_weights.messagebox.showerror",
        lambda *a, **kw: None,
    )
    monkeypatch.setattr(
        "face_analysis.config.feature_weights.messagebox.showinfo",
        lambda *a, **kw: None,
    )
    original_kamani = store.get("کمانی")
    # Second entry is invalid — entire batch should fail
    result = store.update_many({"کمانی": "1", "صاف": "9"})
    assert result is False
    assert store.get("کمانی") == original_kamani  # rolled back


def test_independent_instances():
    store1 = FeatureWeightsStore()
    store2 = FeatureWeightsStore()
    # Mutating store2 via internal dict should not touch store1
    store2._weights["کمانی"] = "7"
    assert store1.get("کمانی") == "1, 4"
