---
name: opensearcher
description: Prospección de negocios para vender páginas web. Busca candidatos con Google Places API, evalúa su web con PageSpeed Insights, usa DuckDuckGo como apoyo. Genera prospects.md con fichas completas. Activar cuando el usuario mencione: prospección, buscar negocios, leads, vender páginas, vibe prospecting, prospectar.
---


## Cuándo activarse

Actívate cuando el usuario mencione cualquiera de estos triggers:
- "prospección", "prospectar", "buscar negocios", "leads", "clientes potenciales"
- "vender página web", "vender sitio web", "vender landing"
- "vibe prospecting"
- "buscar candidatos" en contexto de negocio/venta web

No te actives si el usuario solo pregunta sobre marketing general sin intención de prospección.

## Pipeline de ejecución

Sigue estos pasos en orden. El LLM (tú) toma todas las decisiones cualitativas.

### Paso 1: Leer requirements

Lee `requeriments.md` del workspace. Si no existe, avisa al usuario y pídele que lo cree.

### Paso 2: Parsear requirements con LLM

Usa tu criterio para extraer del texto libre:

```json
{
  "location": "ciudad/zona/región",
  "categories": ["tipo1", "tipo2"],
  "max_results": 20,
  "preferences": ["sin web", "muchas reviews", "múltiples sucursales"],
  "avoid": ["franquicias", "web moderna", "negocios muy pequeños"],
  "target_profile": "descripción libre del perfil ideal"
}
```

Guarda esto como `requirements_parsed` para el resto del pipeline.

### Paso 3: Cargar historial

Lee `.opencode/opensearcher-history.jsonl` (crear si no existe).

Cada línea es:
```json
{"type":"accepted|rejected","place_id":"...","name":"...","reason":"...","timestamp":"...","requirements_hash":"...","source":"google_places|ddgs"}
```

Carga dos listas:
- `rejected` → place_ids que no deben reaparecer (salvo que el reasoning haya cambiado, ver Paso 6)
- `accepted` → place_ids ya considerados buenos (para referencia, no se excluyen automáticamente pero se priorizan negocios similares)

Calcula un `requirements_hash` simple del contenido de `requeriments.md` para trackear cambios.

### Paso 4: Buscar en Google Places

Usa `webfetch` para llamar a la API de Google Places Text Search:

```
GET https://maps.googleapis.com/maps/api/place/textsearch/json
  ?query={categories} en {location}
  &key={api_key}
  &language=es
  &region=ES
```

La API key se lee de `.opencode/skills/opensearcher/config.yaml` → `opensearcher.google_places_key`.

Para cada resultado, llama a Place Details para obtener `website` y `formatted_phone_number`:

```
GET https://maps.googleapis.com/maps/api/place/details/json
  ?place_id={place_id}
  &fields=name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,opening_hours,types,price_level,business_status,url
  &key={api_key}
  &language=es
```

Construye un array `raw_places[]` con los campos relevantes.

### Paso 5: Filtrar candidatos ya rechazados

Para cada `raw_place`, si su `place_id` está en `rejected`:
- Revisa si el `reasoning` del rechazo sigue aplicando con los nuevos requirements
- Si el motivo ya no aplica (ej: antes se rechazó por "rating muy bajo" y ahora requirements no menciona rating), **inclúyelo** y anótalo como reconsiderado
- Si el motivo sigue vigente, **exclúyelo** silenciosamente

### Paso 6: Evaluar webs con PageSpeed Insights

Para cada candidato filtrado que tenga `website`:

```
GET https://www.googleapis.com/pagespeedonline/v5/runPagespeed
  ?url={website}
  &key={api_key}
  &strategy=mobile
```

Y también con `strategy=desktop`.

Campos relevantes del response:
- `lighthouseResult.categories.performance.score` (0-1)
- `lighthouseResult.categories.seo.score` (0-1)
- `loadingExperience.metrics` (opcional)

Si la API responde error (sitio caído, URL inválida, timeout), registra `pagespeed: null` con `pagespeed_error: "razón"`.

### Paso 7: DDGS auxiliar (opcional, decide el LLM)

Usa tu criterio para decidir si DuckDuckGo aporta valor adicional:
- ¿Faltan datos de contacto?
- ¿Quieres verificar reseñas en otras fuentes?
- ¿El negocio parece tener presencia online no reflejada en Google Places?
- ¿Quieres buscar competidores en la zona?

Si decides usarlo, ejecuta:

```bash
pip install duckduckgo-search 2>$null; python .opencode/skills/opensearcher/scripts/ddgs-search.py "{query}" --max 5
```

Procesa los resultados e intégralos al candidato como `ddgs_results`.

### Paso 8: Evaluar candidatos (decisión cualitativa del LLM)

Con toda la información reunida, usa tu criterio para seleccionar los mejores candidatos.

Considera:
- **Alineación con requirements** (categoría, ubicación, perfil)
- **Calidad de la web actual** (PageSpeed bajo → oportunidad de mejora; sin web → oportunidad directa)
- **Señales de reviews** (muchas reviews con rating medio-bajo → negocio popular pero con margen de mejora)
- **Preferencias/avoid del usuario**
- **Historial**: ¿el usuario aceptó negocios similares antes? ¿rechazó por razones que aplican aquí?
- **Potencial de venta**: ¿este negocio se beneficiaría visiblemente de una web mejor?

Para cada candidato seleccionado, genera:

```json
{
  "place_id": "...",
  "name": "...",
  "address": "...",
  "phone": "...",
  "website": "...",
  "rating": 4.2,
  "reviews": 87,
  "price_level": 2,
  "business_status": "OPERATIONAL",
  "types": ["restaurant", "food"],
  "google_maps_url": "...",
  "pagespeed": { "mobile": 0.45, "desktop": 0.62 } | null,
  "pagespeed_error": "..." | null,
  "ddgs_insights": "..." | null,
  "llm_reasoning": "Explicación cualitativa de por qué este negocio es un buen candidato",
  "llm_score": "A/B/C (A=excelente lead, B=bueno, C=posible)",
  "reconsiderado": false
}
```

### Paso 9: Persistir en historial

Anexa al archivo `.opencode/opensearcher-history.jsonl`:
- Una línea por cada candidato **seleccionado** con `type: "accepted"`
- Una línea por cada candidato evaluado y **rechazado** con `type: "rejected"` + `reason`

No dupliques entradas para el mismo `place_id` dentro de la misma ejecución.

Formato de cada línea:

```json
{"type":"accepted","place_id":"ChIJ...","name":"Restaurante X","reason":"Sin web, 120 reviews, rating 3.9, PageSpeed N/A → oportunidad clara","timestamp":"2026-06-20T12:00:00Z","requirements_hash":"abc123","source":"google_places"}
```

### Paso 10: Generar prospects.md

Escribe `prospects.md` con la siguiente estructura:

```markdown
# Prospects — {fecha}

> Basado en: {requirements original}

## Resumen

| # | Nombre | Tipo | Rating | Reviews | Web | PageSpeed | Score LLM |
|---|--------|------|--------|---------|-----|-----------|-----------|
| 1 | Restaurante X | Restaurante | 3.9 | 120 | ❌ | N/A | A |

---

## Fichas detalle

### 1. Restaurante X

- **Dirección:** Calle Ejemplo 123, Madrid
- **Teléfono:** +34 912 345 678
- **Web:** No tiene
- **Google Maps:** [Ver en Maps](url)
- **Rating:** ⭐ 3.9 (120 reviews)
- **Rango precio:** €€
- **Estado:** Operando

**PageSpeed Insights:** N/A (no tiene web)

**Análisis LLM:**
{razonamiento cualitativo}

**Por qué es buen lead:**
- No tiene página web
- Volumen alto de reviews → negocio con clientela
- Rating medio-bajo → margen de mejora
- {otros factores}

---

[Repetir para cada candidato]
```

## Config (.opencode/skills/opensearcher/config.yaml)

```yaml
opensearcher:
  google_places_key: "tu-api-key"
  pagespeed_key: "tu-api-key"  # Misma key de Google Cloud
  defaults:
    radius_meters: 5000
    language: "es"
    region: "ES"
```

Si no encuentra el config o las keys, avisa al usuario con el mensaje exacto:
> "Necesito que configures tu API key en `.opencode/skills/opensearcher/config.yaml`. Si no tienes una, créala en https://console.cloud.google.com/apis/credentials"

## Reglas importantes

1. **No inventes datos.** Si una API falla o un campo no está disponible, regístralo como `null`.
2. **No repitas candidatos.** Usa el historial para evitar proposiciones duplicadas.
3. **El LLM decide.** Eres tú quien evalúa cualitativamente. No hay fórmulas rígidas de scoring.
4. **Sé honesto con el usuario.** Si los resultados son pobres, dilo. No fuerces candidatos malos.
5. **No modifiques `requeriments.md`.** Es del usuario.
6. **No comitees nada.** El workspace tiene `/.opencode` en `.gitignore`.
