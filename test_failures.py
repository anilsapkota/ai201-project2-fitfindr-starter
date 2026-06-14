from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

print("=== Failure 1: search_listings returns zero results ===")
results = search_listings("designer ballgown", size="XXS", max_price=5)
print(f"Result: {results}")
print(f"Is empty list: {results == []}")

print("\n=== Failure 2: suggest_outfit with empty wardrobe ===")
results = search_listings("vintage graphic tee", size=None, max_price=50)
outfit = suggest_outfit(results[0], get_empty_wardrobe())
print(f"Result: {outfit}")

print("\n=== Failure 3: create_fit_card with empty outfit ===")
results = search_listings("vintage graphic tee", size=None, max_price=50)
fit_card = create_fit_card("", results[0])
print(f"Result: {fit_card}")