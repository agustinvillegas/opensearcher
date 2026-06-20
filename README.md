# OpenSearcher — Skill de opencode para prospección de negocios

Busca negocios que cumplan ciertos requisitos, evalúa su presencia web con PageSpeed Insights y genera un reporte `.md` con los mejores candidatos para venderles una página web.

## Requisitos

- Python 3.8+ con `pip install duckduckgo-search`
- Google Cloud API key con Places API + PageSpeed Insights habilitados

## Instalación

```bash
# En tu proyecto (o ~/.config/opencode/skills/)
mkdir -p .opencode/skills
cp -r skills/opensearcher .opencode/skills/

# Dependencias
pip install -r .opencode/skills/opensearcher/scripts/requirements.txt
```

## Config

Crea `.opencode/config.yaml`:

```yaml
opensearcher:
  google_places_key: "AIza..."
  pagespeed_key: "AIza..."
```

## Uso

1. Crea `requeriments.md` con los criterios de búsqueda
2. En opencode: invoca la skill (se activa con palabras como "prospección", "buscar leads", etc.)
3. Obtendrás `prospects.md` con los candidatos evaluados

## Estructura

```
.opencode/skills/opensearcher/
├── SKILL.md                    # Instrucciones para el LLM
└── scripts/
    ├── ddgs-search.py          # Búsqueda auxiliar DuckDuckGo
    └── requirements.txt
```
