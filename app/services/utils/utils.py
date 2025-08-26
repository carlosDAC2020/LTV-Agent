import re
import json

def json_extraction(text: str) -> dict:
    """Extrae un bloque de código JSON de una cadena de texto y lo parsea."""
    if not isinstance(text, str):
        # Si la entrada ya es un dict (de una herramienta, por ejemplo), devuélvelo.
        if isinstance(text, dict):
            return text
        return {"error": "Input text is not a string.", "raw_output": str(text)}

    match = re.search(r"```json(.*?)```", text, re.DOTALL)
    if not match:
        return {"error": "JSON block not found in the text.", "raw_output": text}
    
    json_text = match.group(1).strip()
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        return {"error": f"JSON Decode Error: {e}", "raw_output": json_text}