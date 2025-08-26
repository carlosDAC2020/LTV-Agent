from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles  
from pathlib import Path

from app.routers import agents_router


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
    return templates.TemplateResponse("index.html", {"request": request})


# Si quieres ejecutar directamente con `python app/main.py` (para depuración rápida, no para producción)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)