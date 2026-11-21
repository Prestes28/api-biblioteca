import json
import logging

from fastapi import FastAPI, HTTPException, Path, Query, Response, status
from pydantic import BaseModel, Field

app = FastAPI()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
logger = logging.getLogger(__name__)
class LibroCreate(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=100)
    autor: str = Field(..., min_length=3, max_length=60)
    anio: int = Field(..., ge=1000, le=2100)
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

@app.get("/", summary="Raíz de la API", status_code=status.HTTP_200_OK)
def read_root():
    ''' Raíz de la API de la biblioteca.'''
    return {"message": "API de la biblioteca"}

@app.get("/libros", response_model=list[Libro], status_code=status.HTTP_200_OK, summary="Listar libros")
def listar_libros(
    autor: str | None = Query(
        default=None,
        min_length=1,
        description="Filtrar por autor"
    ),
    disponible: bool | None = Query(
        default=None,
        description="Filtrar por disponibilidad"
    ),
    desde: int = Query(
        default=0,
        ge=0,
        description="Cantidad de libros a saltear"
    ),
    limite: int = Query(
        default=100,
        ge=1,
        description="Cantidad máxima de libros"
    )
):
    """Lista libros con filtros opcionales y paginación."""

    libros = cargar_libros()

    if autor is not None:
        autor_busqueda = autor.strip().casefold()

        libros = [
            libro for libro in libros
            if libro["autor"].strip().casefold() == autor_busqueda
        ]

    if disponible is not None:
        libros = [
            libro for libro in libros
            if libro["disponible"] == disponible
        ]

    libros = libros[desde:desde + limite]

    return libros

@app.get("/libros/estadisticas", status_code=status.HTTP_200_OK, summary="Obtener estadísticas de libros")
def obtener_estadisticas():
    ''' Obtener estadísticas de libros: total, disponibles y prestados.'''
    libros = cargar_libros()
    total_libros = len(libros)
    libros_disponibles = sum(1 for libro in libros if libro["disponible"] == True)
    libros_prestados = sum(1 for libro in libros if libro["disponible"] == False)
    return {
        "total_libros": total_libros,
        "libros_disponibles": libros_disponibles,
        "libros_prestados": libros_prestados
    }

@app.get("/libros/buscar", response_model=list[Libro], status_code=status.HTTP_200_OK, summary="Buscar libros por texto en título o autor")
def buscar_libros_por_texto(texto: str = Query(..., min_length=1, description="Texto a buscar en título o autor")):
    ''' Buscar libros por texto en título o autor.'''
    libros = cargar_libros()
    return [libro for libro in libros if texto.lower() in libro["titulo"].lower() or texto.lower() in libro["autor"].lower()]

@app.post("/libros", response_model=Libro, status_code=status.HTTP_201_CREATED, summary="Crear un nuevo libro")
def crear_libro(datos: LibroCreate):
    ''' Crear un nuevo libro.'''
    libros = cargar_libros()
    existe = any(libro["titulo"].lower() == datos.titulo.lower() and libro["autor"].lower() == datos.autor.lower() for libro in libros)
    if existe:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El libro ya existe")
    new_id = obtener_siguiente_id(libros)
    actualizar_contador(new_id + 1)
    new_libro = Libro(id=new_id, **datos.model_dump()).model_dump()
    if any(libro["id"] == new_libro["id"] for libro in libros):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El libro con este ID ya existe")
   
    libros.append(new_libro)
    guardar_libros(libros)
    logger.info(f"Libro creado:ID {new_libro['id']} - {new_libro['titulo']}")
    return new_libro

@app.get("/libros/{libro_id}",response_model=Libro, status_code=status.HTTP_200_OK, summary="Obtener un libro por ID")
def obtener_libro_por_id(libro_id: int = Path(..., gt=0, description="ID del libro a obtener")): 
    ''' Obtener un libro por su ID.'''
    libros = cargar_libros()
    libro = next((libro for libro in libros if libro["id"] == libro_id), None)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    logger.info(f"Libro obtenido:ID {libro['id']} - {libro['titulo']}")
    return libro   

@app.put("/libros/{libro_id}", response_model=Libro, status_code=status.HTTP_200_OK, summary="Reemplazar un libro por ID")
def reemplazar_libro(datos: LibroCreate, libro_id: int = Path(..., gt=0, description="ID del libro a actualizar")):
    ''' Reemplazar un libro por su ID.'''
    libros = cargar_libros()
    libro = next((libro for libro in libros if libro["id"] == libro_id), None)
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    updated_libro = {**libro, **datos.model_dump()}
    libros = [libro if libro["id"] != libro_id else updated_libro for libro in libros]
    guardar_libros(libros)
    logger.info(f"Libro actualizado:ID {updated_libro['id']} - {updated_libro['titulo']}")
    return updated_libro

@app.delete("/libros/{libro_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar un libro por ID")
def eliminar_libro(libro_id: int = Path(..., gt=0, description="ID del libro a eliminar")):
    ''' Eliminar un libro por su ID.'''
    libros = cargar_libros()
    libros_filtrados = [libro for libro in libros if libro["id"] != libro_id]
    if len(libros) == len(libros_filtrados):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")

    guardar_libros(libros_filtrados)
    logger.info(f"Libro eliminado:ID {libro_id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.patch("/libros/{libro_id}", response_model=Libro, status_code=status.HTTP_200_OK, summary="Actualizar parcialmente un libro por ID")
def actualizar_libro(cambios: LibroUpdate, libro_id: int = Path(..., gt=0, description="ID del libro a actualizar")):
    ''' Actualizar parcialmente un libro por su ID.'''
    libros = cargar_libros()
    libro = next((libro for libro in libros if libro["id"] == libro_id), None)
    if libro is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")
    updated_libro = {**libro, **cambios.model_dump(exclude_unset=True)}
    libros = [libro if libro["id"] != libro_id else updated_libro for libro in libros]
    guardar_libros(libros)
    logger.info(f"Libro actualizado:ID {updated_libro['id']} - {updated_libro['titulo']}")
    return updated_libro

@app.post("/libros/{libro_id}/prestar", response_model=Libro, status_code=status.HTTP_200_OK, summary="Prestar un libro por ID")
def prestar_libro(libro_id: int = Path(..., gt=0, description="ID del libro a prestar")):
    ''' Prestar un libro por su ID.'''
    libros = cargar_libros()
    libro = next((libro for libro in libros if libro["id"] == libro_id), None)
    if libro is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")
    if not libro["disponible"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El libro ya se encuentra prestado")
    libro["disponible"] = False
    guardar_libros(libros)
    logger.info(f"Libro prestado:ID {libro['id']} - {libro['titulo']}")
    return libro

@app.post("/libros/{libro_id}/devolver", response_model=Libro, status_code=status.HTTP_200_OK, summary="Devolver un libro por ID")
def devolver_libro(libro_id: int = Path(..., gt=0, description="ID del libro a devolver")):
    ''' Devolver un libro por su ID.'''
    libros = cargar_libros()
    libro = next((libro for libro in libros if libro["id"] == libro_id), None)
    if libro is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")
    if libro["disponible"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El libro ya se encuentra disponible")
    libro["disponible"] = True
    guardar_libros(libros)
    logger.info(f"Libro devuelto:ID {libro['id']} - {libro['titulo']}")
    return libro

