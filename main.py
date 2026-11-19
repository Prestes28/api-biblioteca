from fastapi import FastAPI, HTTPException
import json 
from pydantic import BaseModel, Field
app = FastAPI()

class Libro(BaseModel):
    id: int = Field(..., gt=0)
    titulo: str = Field(..., min_length=3, max_length=100)
    autor: str = Field(..., min_length=3, max_length=100)
    anio: int = Field(..., ge=0)
    disponible: bool = True

def cargar_libros():
    try:
        with open("libros.json", "r") as file:
            libros = json.load(file)
    except FileNotFoundError:
        libros = []
    return libros

@app.get("/")
def read_root():
    return {"message": "API de la biblioteca"}

@app.get("/libros")
def read_libros():
    return cargar_libros()

@app.get("/libros/buscar")
def buscar_libros(query: str):
    return {"message": f"Buscando libros con la consulta: {query}"} 

@app.post("/libros")
def crear_libro(datos: dict):
    new_libro = {
        "id": len(datos) + 1,
        "titulo": datos.get("titulo"),
        "autor": datos.get("autor"),
        "anio": datos.get("anio"),
        'disponible': datos.get("disponible", True)
    }
    return {"message": "Libro creado", "libro": new_libro}

@app.get("/libros/{libro_id}")
def read_libro(libro_id: int): 
    return {"message": f"Detalles del libro con ID: {libro_id}"}    

@app.put("/libros/{libro_id}")
def actualizar_libro(libro_id: int, libro: dict):  
    return {"message": f"Libro con ID {libro_id} actualizado", "libro": libro}

@app.delete("/libros/{libro_id}")
def eliminar_libro(libro_id: int):
    return {"message": f"Libro con ID {libro_id} eliminado"}

@app.patch("/libros/{libro_id}")
def actualizar_parcial_libro(libro_id: int, libro: dict):
    return {"message": f"Libro con ID {libro_id} actualizado parcialmente", "libro": libro} 


