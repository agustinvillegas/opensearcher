# OpenSearcher — opencode skill for business prospecting

Search for businesses matching your criteria, evaluate their web presence with PageSpeed Insights, and get a `.md` report with the best leads to sell them a website.

## Requirements

- Python 3.8+ with `pip install duckduckgo-search`
- Google Cloud API key with Places API + PageSpeed Insights enabled

## Installation

```bash
# In your project
cp -r skills/opensearcher .opencode/skills/

# Or globally (~/.config/opencode/skills/)
cp -r skills/opensearcher ~/.config/opencode/skills/

# Dependencies
pip install -r .opencode/skills/opensearcher/scripts/requirements.txt
```

## Config

Edit `.opencode/skills/opensearcher/config.yaml`:

```yaml
opensearcher:
  google_places_key: "AIza..."
  pagespeed_key: "AIza..."
```

## Usage

1. Create `requeriments.md` in your project root with your search criteria
2. In opencode: invoke the skill (triggers on "prospecting", "find leads", etc.)
3. Get `prospects.md` with evaluated candidates

## Structure

```
.opencode/skills/opensearcher/
├── SKILL.md                    # LLM instructions
├── config.yaml                 # API keys (edit this)
├── requeriments.md.example     # Template for your search criteria
└── scripts/
    ├── ddgs-search.py          # DuckDuckGo auxiliary search
    └── requirements.txt
```
