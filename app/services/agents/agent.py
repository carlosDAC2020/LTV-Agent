import asyncio
from mcp_agent.core.fastagent import FastAgent
from mcp_agent.core.request_params import RequestParams
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = CURRENT_DIR / "prompts"

# --- DEFINICIÓN DE AGENTES ---
# Crear la instancia del agente
LTV_agent = FastAgent("LTV Agent", parse_cli_args=False)

# 1. Extracción de palabras clave
@LTV_agent.agent(
    name="keywords_extraction",
    instruction=PROMPTS_DIR / "keywords_extraction.md",
)
@LTV_agent.agent(
    name="brave_search",
    instruction=PROMPTS_DIR/"brave_search.md",
    servers=["brave-search"],
)
#@LTV_agent.agent(
#    name="twitter_search",
#    instruction= PROMPTS_DIR/"twitter_search.md",
#    servers=["twitter-mcp"],
#)
@LTV_agent.parallel(
    name="parallel_search",
    fan_out=["brave_search"],
    instruction="Realiza búsqueda en todas las plataformas usando las palabras clave.",
)
@LTV_agent.agent(
    name="normalize_results",
    instruction=PROMPTS_DIR/"normalize_results.md",
)
@LTV_agent.agent(
    name="url_fetcher",
    instruction=PROMPTS_DIR/"url_fetcher.md",
    servers=["fetch"],
)
@LTV_agent.agent(
    name="merge_content",
    instruction=PROMPTS_DIR/"merge_content.md",
)
@LTV_agent.agent(
    name="inference_items",
    instruction=PROMPTS_DIR/"inference_items.md",
)
@LTV_agent.agent(
    name="confidence_items",
    instruction=PROMPTS_DIR/"confidence_items.md",
    request_params=RequestParams(temperature= 0.7)
)
@LTV_agent.agent(
    name="context_items",
    instruction=PROMPTS_DIR/"context_items.md",
    servers=["ltv_tools"],
    request_params=RequestParams(temperature= 0.5)
)
@LTV_agent.agent(
    name="veracity_score",
    instruction=PROMPTS_DIR/"veracity_score.md",
    servers=["ltv_tools"],
    request_params=RequestParams(temperature= 0.5)
)
@LTV_agent.chain(
    name="ltv_full_process",
    sequence=[
        "keywords_extraction",
        "brave_search",
        "normalize_results",
        "inference_items",
        "confidence_items"
    ],
)
async def setup_agent():
    pass
