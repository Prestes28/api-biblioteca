from fastapi import FastAPI, HTTPException, status, Query, Path, Response
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

class LibroUpdate(BaseModel):
    titulo: str | None = Field(default=None, min_length=3, max_length=100)
    autor: str | None = Field(default=None, min_length=3, max_length=60)
    anio: int | None = Field(default=None, ge=1000, le=2100)
    disponible: bool | None = None

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
    max_id =  max((libro["id"] for libro in libros), default=0)
    try:
        with open("./datos/contador.json", "r", encoding="utf-8") as file:
            contador = json.load(file)
            siguiente_id = contador.get("siguiente_id", max_id)
    except FileNotFoundError:
        siguiente_id = max_id
    return max(siguiente_id, max_id + 1)

def actualizar_contador(siguiente_id: int) -> None:
    with open("./datos/contador.json", "w", encoding="utf-8") as file:
        json.dump({"siguiente_id": siguiente_id}, file, indent=4)

@app.get("/")
def read_root():
    return {"message": "API de la biblioteca"}

@app.get("/libros", response_model=list[Libro], status_code=status.HTTP_200_OK)
def listar_libros( autor: str|None = Query(
    default=None, 
    min_length=1,
    description="Filtrar por autor"),
    disponible: bool|None = Query(
    default=None, description="Filtrar por disponibilidad(True/False)"),
    desde: int|None = Query(
        default=0,
          ge=0,
          description="Cantidad de libros a saltear desde el inicio (por defecto 0)"),
    limite: int|None = Query(
        default=100,
        ge=1,
        description="Cantidad máxima de libros a retornar (por defecto 100)")):
    libros = cargar_libros()
    if autor is not None:
        libros = [libro for libro in libros if libro["autor"].lower() == autor.lower()]
    if disponible is not None:
        libros = [libro for libro in libros if libro["disponible"] == disponible]
    if desde is not None:
        libros = libros[desde:]
    if limite is not None:
        libros = libros[:limite]
    return libros

@app.get("/libros/buscar", response_model=list[Libro], status_code=status.HTTP_200_OK)
def buscar_libros_por_texto(q: str = Query(..., min_length=1, description="Texto a buscar en título o autor")):
    libros = cargar_libros()
    return [libro for libro in libros if q.lower() in libro["titulo"].lower() or q.lower() in libro["autor"].lower()]

@app.post("/libros", response_model=Libro, status_code=201)
def crear_libro(datos: LibroCreate):
    libros = cargar_libros()
    new_id = obtener_siguiente_id(libros)
    actualizar_contador(new_id + 1)
    new_libro = Libro(id=new_id, **datos.model_dump()).model_dump()
    if any(libro["id"] == new_libro["id"] for libro in libros):
        raise HTTPException(status_code=400, detail="El libro con este ID ya existe")
   
    libros.append(new_libro)
    guardar_libros(libros)
    return new_libro

@app.get("/libros/{libro_id}",response_model=Libro, status_code=status.HTTP_200_OK)
def obtener_libro_por_id(libro_id: int = Path(..., gt=0, description="ID del libro a obtener")): 
    libros = cargar_libros()
    libro = next((libro for libro in libros if libro["id"] == libro_id), None)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return libro   

@app.put("/libros/{libro_id}", response_model=Libro, status_code=status.HTTP_200_OK)
def reemplazar_libro(datos: LibroCreate, libro_id: int = Path(..., gt=0, description="ID del libro a actualizar")):
    libros = cargar_libros()
    libro = next((libro for libro in libros if libro["id"] == libro_id), None)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    updated_libro = {**libro, **datos.model_dump()}
    libros = [libro if libro["id"] != libro_id else updated_libro for libro in libros]
    guardar_libros(libros)
    return updated_libro

@app.delete("/libros/{libro_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_libro(libro_id: int = Path(..., gt=0, description="ID del libro a eliminar")):
    libros = cargar_libros()
    libros_filtrados = [libro for libro in libros if libro["id"] != libro_id]
    if len(libros) == len(libros_filtrados):
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    guardar_libros(libros_filtrados)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.patch("/libros/{libro_id}", response_model=Libro, status_code=status.HTTP_200_OK)
def actualizar_libro(cambios: LibroUpdate, libro_id: int = Path(..., gt=0, description="ID del libro a actualizar")):
    libros = cargar_libros()
    libro = next((libro for libro in libros if libro["id"] == libro_id), None)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    updated_libro = {**libro, **cambios.model_dump(exclude_unset=True)}
    libros = [libro if libro["id"] != libro_id else updated_libro for libro in libros]
    guardar_libros(libros)
    return updated_libro


