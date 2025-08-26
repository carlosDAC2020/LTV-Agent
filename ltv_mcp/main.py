from sentence_transformers import SentenceTransformer, util
from mcp.server.fastmcp import FastMCP
from typing import Dict, Any

# --- 1. Inicialización del Servidor MCP ---
mcp = FastMCP("LTV-mcp-toolkit", host="0.0.0.0")

# --- 2. Carga del Modelo de Lenguaje (una sola vez al iniciar) ---
print("Cargando modelo de lenguaje (puede tardar la primera vez)...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("Modelo cargado.")

@mcp.tool()
def get_context(prompt: str, noticias_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcula la similitud semántica entre un prompt y una lista de noticias.
    Enriquece cada objeto de noticia con una nueva clave 'similitud' y ordena
    la lista de noticias de mayor a menor similitud.

    Args:
        prompt: El texto con el que se compararán las noticias.
        noticias_data: Un diccionario que contiene una clave 'items' con la lista de noticias.

    Returns:
        El mismo diccionario 'noticias_data' de entrada, pero con cada item en la lista 'items'
        enriquecido con la clave 'similitud' y la lista ordenada por este valor.
    """
    # --- 3. EXTRACCIÓN DE DATOS DESDE EL DICCIONARIO ---
    items = noticias_data.get('items', [])
    if not items:
        print("El diccionario de entrada no contiene 'items' o la lista está vacía.")
        return noticias_data

    # --- 4. PREPARACIÓN DEL TEXTO ---
    textos_noticias = [f"{item.get('title', 'Sin título')}. {item.get('resumen', '')}" for item in items]

    # --- 5. CREACIÓN DE EMBEDDINGS ---
    print("Codificando textos a vectores semánticos...")
    embedding_prompt = model.encode(prompt, convert_to_tensor=True)
    embeddings_noticias = model.encode(textos_noticias, convert_to_tensor=True)
    print("Codificación completa.")

    # --- 6. CÁLCULO DE SIMILITUD DEL COSENO ---
    similitud_scores = util.cos_sim(embedding_prompt, embeddings_noticias).flatten()

    # --- 7. AÑADIR LA SIMILITUD A CADA ITEM ---
    for i, item in enumerate(items):
        # AÑADIMOS LA NUEVA CLAVE 'similitud' AL DICCIONARIO 'item' EXISTENTE
        item['context'] = similitud_scores[i].item()

    # --- 8. ORDENAR LA LISTA DE ITEMS POR SIMILITUD ---
    # Usamos el método sort() de la lista con una función lambda para ordenar in-place.
    items.sort(key=lambda x: x.get('context', 0), reverse=True)

    # --- 9. DEVOLVER EL OBJETO ORIGINAL MODIFICADO ---
    return noticias_data

@mcp.tool()
def get_veracity(noticias_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Obtiene tanto el puntaje de veracidad individual como general de
    los items de información.

    Args:
        noticias_data: Un diccionario que contiene una clave 'items' con la lista de noticias,
                       donde cada item ya tiene las claves 'context' e 'inference'.

    Returns:
        El mismo diccionario 'noticias_data' de entrada, pero con cada item en la lista 'items'
        enriquecido con la clave 'score' y 'confidence'. Además, se añaden métricas
        generales de veracidad al diccionario principal.
    """
    items = noticias_data.get('items', [])
    if not items:
        print("El diccionario de entrada no contiene 'items' o la lista está vacía.")
        return noticias_data

    # --- Pesos para el cálculo del puntaje ---
    ltv_w = {
        'w_C': 0.3, 'w_F': 0.5, 'w_I': 0.2,
    }

    # --- Funciones auxiliares para el cálculo ---
    pi = lambda c, w_c, f, w_f, i, w_i: c * w_c + f * w_f + i * w_i
    p_min = 0
    p_max = lambda n_items: (ltv_w['w_C'] * 1 + ltv_w['w_F'] * 1 + ltv_w['w_I'] * 1) * n_items

    pt = 0  # Puntaje total
    n_items = len(items)

    for item in items:
        # Extraemos los valores. Usamos .get() con un valor por defecto para evitar errores.
        c = item.get("context", 0)
        # Asumimos un valor fijo para 'f' (fact-checking) como en la lógica de ejemplo.
        f = item.get("confidence", 0.5)
        i = item.get("inference", 0)

        # Calculamos el puntaje individual del item
        pi_item = pi(c, ltv_w['w_C'], f, ltv_w['w_F'], i, ltv_w['w_I'])
        
        # Acumulamos el puntaje total
        pt += pi_item

        # Enriquecemos el item con su puntaje y confianza
        item["confidence"] = f
        item["score"] = pi_item

    # Calculamos la métrica general de veracidad 'v'
    p_max_val = p_max(n_items)
    # Evitamos la división por cero si p_max_val es igual a p_min
    if p_max_val == p_min:
        v = 0.0
    else:
        v = ((pt - p_min) / (p_max_val - p_min)) * 100

    # Añadimos las métricas generales al diccionario principal
    noticias_data["overall_veracity"] = v

    print(f"cantidad de items evaluados : {len(noticias_data['items'])}")

    return noticias_data

mcp.run(transport="streamable-http")


