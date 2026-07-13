"""
test_recommendations.py
Tests the label -> recommendation mapping logic in recommendations.py.
"""
from recommendations import get_recommendation, RECOMMENDATIONS, DEFAULT_RECOMMENDATION


def test_known_disease_label_returns_full_data():
    result = get_recommendation("corn_gray_leaf_spot")
    assert result["category"] == "disease"
    assert result["risk"] == "high"
    assert result["disease_type"] == "Fungal disease"
    assert "Cercospora" in result["cause"]
    assert "advice" in result


def test_known_healthy_label_returns_none_type_and_cause():
    result = get_recommendation("apple_leaf")
    assert result["category"] == "healthy"
    assert result["risk"] == "none"
    assert result["disease_type"] is None
    assert result["cause"] is None


def test_label_is_case_insensitive():
    result_lower = get_recommendation("apple_scab_leaf")
    result_upper = get_recommendation("APPLE_SCAB_LEAF")
    assert result_lower == result_upper


def test_label_with_spaces_is_normalized():
    result_underscore = get_recommendation("corn_rust_leaf")
    result_spaces = get_recommendation("corn rust leaf")
    assert result_underscore == result_spaces


def test_unknown_label_falls_back_to_default():
    result = get_recommendation("some_totally_unknown_label_xyz")
    assert result == DEFAULT_RECOMMENDATION
    assert result["category"] == "unknown"


def test_pest_label_returns_pest_category():
    result = get_recommendation("tomato_two_spotted_spider_mites_leaf")
    assert result["category"] == "pest"
    assert "mite" in result["disease_type"].lower()


def test_all_recommendations_have_required_keys():
    required_keys = {"category", "risk", "disease_type", "cause", "advice"}
    for label, data in RECOMMENDATIONS.items():
        missing = required_keys - data.keys()
        assert not missing, f"Label '{label}' is missing keys: {missing}"


def test_all_disease_entries_have_non_null_cause():
    for label, data in RECOMMENDATIONS.items():
        if data["category"] in ("disease", "pest"):
            assert data["cause"] is not None, f"'{label}' should have a cause but has None"
            assert data["disease_type"] is not None, f"'{label}' should have a disease_type but has None"