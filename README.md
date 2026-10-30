# ServiWash

## Entorno Virtual (.venv)

Comando para crear el entorno virtual.
```
python -m venv .venv
```
Comando para activar el entorno virtual.
- En Windows:
    ```
    .venv\Scripts\activate
    ```
- En Mac o Linux:
    ```
    source .venv/bin/activate
    ```
Comando para desactivar el entorno virtual.
```
deactivate
```

**Aviso: Solo se ejecuta "run.py" cuando se tengan los archivos ".env" y "config.py" creados**

Comando para ejecutar run.py

```
python run.py
```

## Instalar las dependencias

Comando para instalar requirements.txt
```
pip install -r requirements.txt.
```

## Archivo de variables de entorno

Estructura del archivo (.env) para usar variables de entorno y conectar la base de datos.

**Crear el archivo .env dentro del directorio de la API.**

```
SECRET_KEY=
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
DB_NAME=serviwash
```

Comando para generar la SECRET_KEY.
```
python -c "import secrets; print(secrets.token_hex(32))"
```

## Archivo de configuración de python para usar las variables de entorno

Estructura del archivo (config.py) para usar variables de entorno dentro de los archivos de python.

**Crear el archivo config.py dentro del directorio de la API**

```
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '')

    # Parámetros de conexión a MySQL
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'serviwash')

    # Cadena de conexión
    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
```

## Distribución de archivos para las APIs Maquinas y Servicios

```bash
.
├── app
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   └── routers.py
├── .env
├── config.py
└── run.py
```