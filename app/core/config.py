from pathlib import Path
import os


# Ruta base del proyecto 
BASE_DIR = Path(__file__).resolve().parent.parent
# Ruta al directorio de datos
DATA_DIR = BASE_DIR / "data"


PROPMTS_DIR = Path(__file__).resolve().parent.parent / "services" / "agents" / "prompts"



# llms disponibles 
LLMS = {
    "openai": {
        "api_key":""
    },
    "genai" : {
        "api_key":os.getenv('GEMINI_API_KEY')
    }
}

# selecionamos el proveedor
provider = 'genai'
provider_config = LLMS[provider]

# configuracion de modelos 
llm_config = {
    "provider": provider,
    "config": provider_config, 
}
