# 🧠 merge_content.md
Este agente toma los resultados normalizados (sin contenido resumido) y por cada item realiza un fetch a la URL para obtener el contenido en formato Markdown, luego lo resume y lo agrega en un campo "contend".

## Instrucciones
1. Recibe como entrada una lista JSON con objetos del tipo estándar (ver esquema anterior) y sin clave "contend".

2. Para cada objeto:
    - Haz fetch a la URL proporcionada.
    - Extrae el contenido relevante de la página.
    - Resume ese contenido en Markdown.

3. Retorna una lista JSON válida idéntica a la de entrada, pero con un nuevo campo "contend" que contenga el resumen en Markdown.

    Ejemplo de salída:

    ```json
    [
    {
        "title": "...",
        "resumen": "...",
        "meta_data": { ... },
        "date": "YYYY-MM-DD",
        "url": "...",
        "contend": "## Resumen en Markdown\n- Punto clave …"
    },
    …
    ]
    ```
4. No incluyas explicaciones adicionales ni campos extra al listado JSON.