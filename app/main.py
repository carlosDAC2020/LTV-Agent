from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles  
from pathlib import Path
import os
from app.routers import agents_router

from dotenv import load_dotenv

# cargaando variables de entorno
load_dotenv()

app = FastAPI(
    title="LTV-api",
    description="LTV-Agent API.",
    version="0.1.0"
)


# Definimos la ruta base del proyecto para encontrar el directorio 'templates'
BASE_DIR = Path(__file__).resolve().parent.parent
# Montar el directorio estático
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
# Configuramos Jinja2 para que busque plantillas en el directorio 'templates'
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# Incluir los routers
app.include_router(agents_router.router)


@app.get("/", response_class=HTMLResponse)
async def trueshield(request: Request):
    ws_host = os.getenv("VM_IP", "127.0.0.1")
    ws_port = os.getenv("WS_PORT", "80")
    ws_url = f"ws://{ws_host}:{ws_port}/agent/ltv/ws"
    print(f"url de coneccion: {ws_url}")
    return templates.TemplateResponse("index.html", 
                                      {"request": request,
                                        "ws_url": ws_url})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=80, reload=True)