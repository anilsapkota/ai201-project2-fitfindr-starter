# FitFindr 🛍️

FitFindr is an LLM-powered agent that finds secondhand clothing listings, suggests outfits built around your existing wardrobe, and writes a shareable "fit card" caption for your thrifted find.

Link for video in action:
https://www.loom.com/share/4c6fc02e261e4c68af47cdeb6b2ad834

Describe what you're looking for in natural language — including size and price if you want to filter — and FitFindr runs a three-tool planning loop to return a top listing, an outfit idea, and a social-media-ready caption.

## How It Works

FitFindr is built around a **planning loop** ([agent.py](agent.py)) that orchestrates three independent tools, passing state between them through a single `session` dict:

```
user query
    │
    ▼
_parse_query()        → extract description, size, max_price (regex)
    │
    ▼
search_listings()     → score & rank mock listings by keyword overlap
    │  (no results → return early with a helpful error)
    ▼
suggest_outfit()      → LLM suggests outfits using your wardrobe
    │
    ▼
create_fit_card()     → LLM writes a casual OOTD caption
    │
    ▼
session dict → UI panels
```

### The three tools ([tools.py](tools.py))

| Tool | Signature | What it does |
|------|-----------|--------------|
| `search_listings` | `(description, size, max_price) → list[dict]` | Filters the mock dataset by size/price, scores each listing by keyword overlap with the description, and returns matches ranked best-first. Returns `[]` (never raises) when nothing matches. |
| `suggest_outfit` | `(new_item, wardrobe) → str` | Asks the LLM to pair the found item with named pieces from your wardrobe. Falls back to general styling advice when the wardrobe is empty. |
| `create_fit_card` | `(outfit, new_item) → str` | Asks the LLM for a casual 1–3 sentence OOTD caption mentioning the item, price, and platform. Returns an error string (never raises) when the outfit is missing. |

The two LLM tools use Groq's `llama-3.3-70b-versatile` model.

### State & failure handling ([agent.py](agent.py))

`run_agent(query, wardrobe)` returns the completed `session` dict. Always check `session["error"]` first:

- **No search results** → `error` is set, the loop returns early, and the outfit/fit-card fields stay `None`.
- **Fit card fails** (e.g. empty outfit) → `error` is set but `outfit_suggestion` is preserved — a *partial success*. The UI surfaces the listing and outfit while showing the error in the fit-card panel.
- **Full success** → `error` is `None` and all three output fields are populated.

## Project Structure

```
ai201-project2-fitfindr-starter/
├── agent.py                   # Planning loop — orchestrates the three tools via a session dict
├── tools.py                   # The three tools: search_listings, suggest_outfit, create_fit_card
├── app.py                     # Gradio web interface
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example & empty wardrobes
├── utils/
│   └── data_loader.py         # Helpers for loading listings and wardrobes
├── tests/                     # Test suite
├── test_parse.py              # Tests for query parsing
├── test_failures.py           # Tests for failure-mode handling
├── conftest.py                # pytest configuration
├── planning.md                # Design notes for the planning loop
├── fitfindr_architecture.html # Architecture diagram
└── requirements.txt           # Python dependencies
```

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file in the project root (get a free key at [console.groq.com](https://console.groq.com)):

```
GROQ_API_KEY=your_key_here
```

## Running

### Web app

```bash
python app.py
```

Then open the localhost URL shown in your terminal (usually http://localhost:7860 — check the terminal, the port may differ). Type a query, pick a wardrobe (example or empty), and hit **Find it**.

### Command line

`agent.py` has a built-in demo covering the happy path and the no-results path:

```bash
python agent.py
```

You can also call the agent directly:

```python
from agent import run_agent
from utils.data_loader import get_example_wardrobe

result = run_agent(
    query="vintage graphic tee under $30, size M",
    wardrobe=get_example_wardrobe(),
)
print(result["fit_card"])
print(result["error"])   # None on success
```

## The Data

### Mock listings — `data/listings.json`

40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more). Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

```python
from utils.data_loader import load_listings
listings = load_listings()
```

### Wardrobe schema — `data/wardrobe_schema.json`

Defines the format the agent uses to represent a user's existing wardrobe:

- `schema` — field definitions for a wardrobe item
- `example_wardrobe` — a sample wardrobe with 10 items
- `empty_wardrobe` — a starting template for a new user

```python
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe
wardrobe = get_example_wardrobe()   # or get_empty_wardrobe()
```

## Testing

```bash
pytest
```

The suite includes query-parsing tests ([test_parse.py](test_parse.py)) and failure-mode tests ([test_failures.py](test_failures.py)) that verify the agent degrades gracefully on no results, empty wardrobes, and missing outfits.
