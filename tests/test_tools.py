from tools import search_listings,suggest_outfit,create_fit_card
from utils.data_loader import get_example_wardrobe,get_empty_wardrobe


def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []


def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)


def test_search_size_filter():
    results = search_listings("vintage graphic tee", size="M", max_price=50)
    for item in results:
        assert "m" in item["size"].lower()


def test_search_sorted_by_relevance():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    # The top result should have "vintage" and "graphic tee" in its style_tags or title
    if results:
        top = results[0]
        blob = (top["title"] + " " + top["description"] + " " + " ".join(top["style_tags"])).lower()
        assert "vintage" in blob or "graphic" in blob

def test_suggest_outfit_with_wardrobe():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    outfit = suggest_outfit(results[0], get_example_wardrobe())
    assert isinstance(outfit, str)
    assert len(outfit) > 0


def test_suggest_outfit_empty_wardrobe():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    outfit = suggest_outfit(results[0], get_empty_wardrobe())
    assert isinstance(outfit, str)
    assert len(outfit) > 0


def test_create_fit_card_valid():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    outfit = suggest_outfit(results[0], get_example_wardrobe())
    fit_card = create_fit_card(outfit, results[0])
    assert isinstance(fit_card, str)
    assert len(fit_card) > 0


def test_create_fit_card_empty_outfit():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    fit_card = create_fit_card("", results[0])
    assert fit_card == "Cannot create fit card: outfit description is missing."