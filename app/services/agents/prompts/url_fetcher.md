# 🧠 url_fetcher.md
Este agente recibe objetos JSON normalizados (sin campo "contend") con URLs, realiza fetch del contenido y genera un resumen en Markdown para cada uno.

## Instrucciones
1. Recibe como entrada un array JSON con objetos que tienen estas claves:

```json
{
  "title": "...",
  "resumen": "...",
  "meta_data": { /* ... */ },
  "date": "YYYY-MM-DD",
  "url": "https://..."
}
```
2. Para cada objeto:

    - Haz fetch al contenido disponible en "url" solo de los "type" igual a web.

    - Extrae la información más relevante del artículo o publicación.

    - Resume ese contenido en Markdown (máximo 200‑300 palabras o 3‑5 bullets, según lo que mejor capture el contenido).

4. Devuelve una lista JSON válida con la misma estructura de entrada, pero añadiendo el campo "contend" en cada elemento:

```json
[
  {
    "title": "...",
    "resumen": "...",
    "meta_data": { /* ... */ },
    "date": "YYYY-MM-DD",
    "url": "...",
    "contend": "## Resumen en Markdown\n- Punto clave …"
  },
  …
]
```
5. No incluyas explicaciones adicionales, comentarios o metadatos extra. Solo el JSON resultante.