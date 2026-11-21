# API de Biblioteca

API REST desarrollada con Python y FastAPI para administrar libros, consultar estadísticas y gestionar préstamos y devoluciones.

Los datos se guardan en archivos JSON dentro de `datos/`, por lo que no es necesario configurar una base de datos.

## Requisitos

- Python 3.10 o superior
- `pip`

## Instalación

Desde la raíz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Si PowerShell bloquea la activación del entorno:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Para salir del entorno virtual:

```powershell
deactivate
```

## Ejecutar la aplicación

Ejecuta el servidor desde la carpeta raíz del proyecto:

```powershell
uvicorn main:app --reload
```

La API estará disponible en:

- API: http://127.0.0.1:8000
- Documentación interactiva Swagger: http://127.0.0.1:8000/docs
- Documentación ReDoc: http://127.0.0.1:8000/redoc

También puedes iniciar FastAPI con:

```powershell
fastapi dev main.py
```

## Uso desde Swagger

1. Abre http://127.0.0.1:8000/docs.
2. Selecciona un endpoint.
3. Presiona **Try it out**.
4. Completa los parámetros o el cuerpo de la solicitud.
5. Presiona **Execute**.

Esta interfaz permite probar todos los métodos sin instalar una herramienta adicional.

## Modelo de un libro

```json
{
  "titulo": "Cien años de soledad",
  "autor": "Gabriel García Márquez",
  "anio": 1967,
  "disponible": true
}
```

Validaciones:

- `titulo`: entre 3 y 100 caracteres.
- `autor`: entre 3 y 60 caracteres.
- `anio`: entero entre 1000 y 2100.
- `disponible`: booleano; su valor predeterminado es `true`.

Las respuestas que incluyen un libro registrado agregan el campo `id`.

## Endpoints

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/` | Comprueba que la API está activa |
| `GET` | `/libros` | Lista libros con filtros y paginación |
| `GET` | `/libros/buscar?texto=...` | Busca texto en título o autor |
| `GET` | `/libros/estadisticas` | Devuelve totales de libros disponibles y prestados |
| `POST` | `/libros` | Crea un libro |
| `GET` | `/libros/{libro_id}` | Obtiene un libro por ID |
| `PUT` | `/libros/{libro_id}` | Reemplaza todos los datos editables |
| `PATCH` | `/libros/{libro_id}` | Modifica uno o varios datos |
| `DELETE` | `/libros/{libro_id}` | Elimina un libro |
| `POST` | `/libros/{libro_id}/prestar` | Marca un libro como prestado |
| `POST` | `/libros/{libro_id}/devolver` | Marca un libro como disponible |

## Ejemplos con PowerShell

Comprueba la API:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/"
```

Crea un libro:

```powershell
$libro = @{
    titulo = "Cien años de soledad"
    autor = "Gabriel García Márquez"
    anio = 1967
    disponible = $true
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/libros" `
  -ContentType "application/json" `
  -Body $libro
```

Lista todos los libros:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/libros"
```

Filtra por autor y disponibilidad:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/libros?autor=Gabriel García Márquez&disponible=true"
```

Usa paginación para omitir registros y limitar resultados:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/libros?desde=0&limite=10"
```

Busca por texto en el título o el autor:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/libros/buscar?texto=García"
```

Consulta las estadísticas:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/libros/estadisticas"
```

Consulta un libro por ID:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/libros/1"
```

Actualiza parcialmente un libro:

```powershell
$cambios = @{ disponible = $false } | ConvertTo-Json

Invoke-RestMethod `
  -Method Patch `
  -Uri "http://127.0.0.1:8000/libros/1" `
  -ContentType "application/json" `
  -Body $cambios
```

Reemplaza un libro completo:

```powershell
$libro = @{
    titulo = "El amor en los tiempos del cólera"
    autor = "Gabriel García Márquez"
    anio = 1985
    disponible = $true
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Put `
  -Uri "http://127.0.0.1:8000/libros/1" `
  -ContentType "application/json" `
  -Body $libro
```

Presta y devuelve un libro:

```powershell
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/libros/1/prestar"
Invoke-RestMethod -Method Post "http://127.0.0.1:8000/libros/1/devolver"
```

Elimina un libro:

```powershell
Invoke-RestMethod -Method Delete "http://127.0.0.1:8000/libros/1"
```

## Filtros de listado

`GET /libros` admite estos parámetros opcionales:

| Parámetro | Tipo | Predeterminado | Descripción |
|---|---|---:|---|
| `autor` | texto | — | Coincidencia exacta sin distinguir mayúsculas |
| `disponible` | booleano | — | `true` para disponibles o `false` para prestados |
| `desde` | entero | `0` | Cantidad de registros que se omiten |
| `limite` | entero | `100` | Máximo de registros devueltos |

Ejemplo:

```text
GET /libros?autor=python&disponible=true&desde=0&limite=20
```

## Respuestas y errores

| Código | Situación |
|---:|---|
| `200` | Operación completada |
| `201` | Libro creado |
| `204` | Libro eliminado |
| `400` | Conflicto con un identificador existente |
| `404` | Libro no encontrado |
| `409` | Libro duplicado, ya prestado o ya disponible |
| `422` | Datos de entrada inválidos |

## Persistencia

Los datos se almacenan localmente en:

- `datos/libros.json`: listado de libros.
- `datos/contador.json`: próximo identificador disponible.

Conserva estos archivos si necesitas preservar los registros. Al eliminar un libro, su identificador no se reutiliza.

Ejecuta la aplicación desde la raíz del proyecto, ya que el código accede a las rutas JSON mediante rutas relativas.

## Estructura del proyecto

```text
api-biblioteca/
├── main.py
├── requirements.txt
├── README.md
└── datos/
    ├── libros.json
    └── contador.json
```
