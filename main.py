from fastapi import FastAPI, HTTPException, status, Query
import json 
from pydantic import BaseModel, Field
app = FastAPI()

class LibroCreate(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=100)
    autor: str = Field(..., min_length=3, max_length=60)
    anio: int = Field(..., minimum=1000, maximum=2100)
    disponible: bool = Field(default=True)

class Libro(LibroCreate):
    id: int = Field(..., gt=0)

def cargar_libros():
    try:
        with open("./datos/libros.json", "r", encoding="utf-8") as file:
            libros = json.load(file)
    except FileNotFoundError:
        libros = []
    return libros

def guardar_libros(libros: list[dict]) -> None:
    with open("./datos/libros.json", "w", encoding="utf-8") as file:
        json.dump(libros, file, indent=4)

def obtener_siguiente_id(libros: list[dict]) -> int:
    if not libros:
        return 1
    return max((libro["id"] for libro in libros), default=0) + 1
@app.get("/")
def read_root():
    return {"message": "API de la biblioteca"}

@app.get("/libros")
def read_libros():
    return cargar_libros()

@app.get("/libros/buscar", response_model=list[Libro], status_code=status.HTTP_200_OK)
def buscar_libros_por_texto(q: str = Query(..., min_length=1, description="Texto a buscar en título o autor")):
    libros = cargar_libros()
    return [libro for libro in libros if q.lower() in libro["titulo"].lower() or q.lower() in libro["autor"].lower()]

@app.post("/libros", response_model=Libro, status_code=201)
def crear_libro(datos: LibroCreate):
    libros = cargar_libros()
    new_id = obtener_siguiente_id(libros)
    new_libro = Libro(id=new_id, **datos.model_dump()).model_dump()
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


