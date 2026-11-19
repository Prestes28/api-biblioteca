from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/libros")
def read_libros():
    return {"message": "Lista de libros"}

@app.get("/libros/buscar")
def buscar_libros(query: str):
    return {"message": f"Buscando libros con la consulta: {query}"} 

@app.get("/libros/{libro_id}")
def read_libro(libro_id: int): 
    return {"message": f"Detalles del libro con ID: {libro_id}"}    

@app.post("/libros")
def crear_libro(libro: dict):
    return {"message": "Libro creado", "libro": libro}

@app.put("/libros/{libro_id}")
def actualizar_libro(libro_id: int, libro: dict):  
    return {"message": f"Libro con ID {libro_id} actualizado", "libro": libro}

@app.delete("/libros/{libro_id}")
def eliminar_libro(libro_id: int):
    return {"message": f"Libro con ID {libro_id} eliminado"}

@app.patch("/libros/{libro_id}")
def actualizar_parcial_libro(libro_id: int, libro: dict):
    return {"message": f"Libro con ID {libro_id} actualizado parcialmente", "libro": libro} 


