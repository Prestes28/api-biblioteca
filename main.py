from fastapi import FastAPI, HTTPException
import json 
from pydantic import BaseModel, Field
app = FastAPI()

class Libro(BaseModel):
    id: int = Field(..., gt=0)
    titulo: str = Field(..., min_length=3, max_length=100)
    autor: str = Field(..., min_length=3, max_length=100)
    anio: int = Field(..., ge=0)
    disponible: bool = Field(default=True)

def cargar_libros():
    try:
        with open("libros.json", "r", encoding="utf-8") as file:
            libros = json.load(file)
    except FileNotFoundError:
        libros = []
    return libros

def guardar_libros(libros: list[dict]) -> None:
    with open("libros.json", "w", encoding="utf-8") as file:
        json.dump(libros, file, indent=4)

@app.get("/")
def read_root():
    return {"message": "API de la biblioteca"}

@app.get("/libros")
def read_libros():
    return cargar_libros()

@app.get("/libros/buscar")
def buscar_libros(query: str):
    return {"message": f"Buscando libros con la consulta: {query}"} 

@app.post("/libros", response_model=Libro, status_code=201)
def crear_libro(datos: Libro):
    libros = cargar_libros()
    new_libro = datos.model_dump()
    if any(libro["id"] == new_libro["id"] for libro in libros):
        raise HTTPException(status_code=400, detail="El libro con este ID ya existe")
   
    libros.append(new_libro)
    guardar_libros(libros)
    return new_libro

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


