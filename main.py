import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FILE_PATH = "/data/stats.json"

def cargar_stats():
    """Lee el archivo JSON. Si no existe, devuelve valores en cero."""
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as f:
            return json.load(f)
    return {"main": 0, "estadisticas": 0}

def guardar_stats(stats):
    """Guarda el diccionario en el archivo JSON asegurando que el directorio exista."""
    directorio = os.path.dirname(FILE_PATH)
    if directorio:
        os.makedirs(directorio, exist_ok=True)

    with open(FILE_PATH, "w") as f:
        json.dump(stats, f)

@app.post("/visit/{page}")
def registrar_visita(page: str):
    stats = cargar_stats()
    if page in stats:
        stats[page] += 1
        guardar_stats(stats)
        return {"mensaje": f"Visita a {page} registrada con éxito"}
    return {"error": "Página no encontrada"}

@app.get("/stats")
def obtener_estadisticas():
    stats = cargar_stats()
    total = stats["main"] + stats["estadisticas"]
    return {
        "main": stats["main"],
        "estadisticas": stats["estadisticas"],
        "total": total
    }
