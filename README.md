# ServiWash

## Entorno Virtual (.venv)

Comando para crear el entorno virtual.
```bash
python -m venv .venv
```
Comando para activar el entorno virtual.
- En Windows:
    ```bash
    .venv\Scripts\activate
    ```
- En Mac o Linux:
    ```bash
    source .venv/bin/activate
    ```
Comando para desactivar el entorno virtual.
```bash
deactivate
```

**Aviso: Solo se ejecuta "run.py" cuando se tengan los archivos ".env" y "config.py" creados**

Comando para ejecutar run.py.

```bash
python run.py
```

## Instalar las dependencias

Comando para instalar requirements.txt.
```bash
pip install -r requirements.txt
```

## Archivo de variables de entorno

Estructura del archivo (.env) para usar variables de entorno y conectar la base de datos.

**Crear el archivo .env dentro del directorio de la API.**

```bash
SECRET_KEY=
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
DB_NAME=serviwash
```

Comando para generar la SECRET_KEY.
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Estructura del archivo (.env) para usar variables de entorno dentro de la API Gateway.

```bash
SECRET_KEY=
USERS_URL=http://127.0.0.1:5003
CLIENTS_URL=http://127.0.0.1:5001
MACHINES_URL=http://127.0.0.1:5004
SERVICES_URL=http://127.0.0.1:5005
TURNS_URL=http://127.0.0.1:5002
```

## Archivo de configuración de python para usar las variables de entorno

Estructura del archivo (config.py) para usar variables de entorno dentro de los archivos de python.

**Crear el archivo config.py dentro del directorio de la API**

```bash
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

# Endpoints de Maquinas

## Mostrar todas las máquinas

Retorna una lista con todas las máquinas registradas en el sistema.

**Método:** `GET`

**Autenticación:** Sin aplicar todavía.

**Parámetros:** 
- Estado (opcional): Filtra las máquinas según su estado actual.

**Endpoint:** `http://127.0.0.1:8000/api/v1/maquinas?estado=DISPONIBLE`

**Request Body (JSON):**
```bash
No lleva Request Body (JSON)
```

**Response Body 200 Ok (JSON):**
```bash
{
    "capacidad": 22.0,
    "estado": "DISPONIBLE",
    "id": 1,
    "tiempo_ciclo": 40,
    "tipo_maquina": "LAVADORA"
}
```

## Mostrar la máquina por el ID

Obtiene los detalles específicos de una máquina a partir de su identificador único numérico.

**Método:** `GET`

**Autenticación:** Sin aplicar todavía.

**Parámetros:** 
- id: ID único de la máquina.

**Endpoint:** `http://127.0.0.1:8000/api/v1/maquinas/{id}`

**Request Body (JSON):**
```bash
No lleva Request Body (JSON)
```

**Response Body 200 Ok (JSON):**
```bash
{
    "capacidad": 16.0,
    "estado": "DISPONIBLE",
    "id": 2,
    "tiempo_ciclo": 40,
    "tipo_maquina": "SECADORA"
}
```

**404 Not Found (JSON):**
```bash
{
    "error": "Máquina no encontrada"
}
```

## Registrar una nueva máquina

Registra una nueva máquina en el sistema utilizando los datos JSON provistos.

**Método:** `POST`

**Autenticación:** Sin aplicar todavía.

**Parámetros:** 
- Ninguno

**Endpoint:** `http://127.0.0.1:8000/api/v1/maquinas`

**Request Body (JSON):**
| Campo | Tipo | Requerido | Descripción |
| :--- | :--- | :--- | :--- |
| `tipo_maquina` | String | **Sí** | Tipo de equipo (LAVADORA o SECADORA). |
| `capacidad` | Float | **Sí** | Capacidad de carga en kilogramos. |
| `tiempo_ciclo` | Integer | **Sí** | Duración estándar de cada ciclo en minutos. |
| `estado` | String | **No** | Estado inicial (por defecto se asigna DISPONIBLE). |

```bash
{
    "tipo_maquina": "LAVADORA",
    "capacidad": 12.0,
    "tiempo_ciclo": 40
}
```

**Response Body 201 Created (JSON):**
```bash
{
    "capacidad": 12.0,
    "estado": "DISPONIBLE",
    "id": 3,
    "tiempo_ciclo": 40,
    "tipo_maquina": "LAVADORA"
}
```

**400 Bad Request (JSON):**
```bash
{
  "error": "Datos de entrada inválidos: 'tipo_maquina'"
}
```

## Actualizar el estado de la máquina

Modifica de forma parcial únicamente el estado operativo de una máquina específica.

**Método:** `PATCH`

**Autenticación:** Sin aplicar todavía.

**Parámetros:** 
- id (Path): ID único de la máquina.
- estado (Body): Parte del cuerpo de la URL para ejecutar el endpoint.

**Endpoint:** `http://127.0.0.1:8000/api/v1/maquinas/{id}/estado`

**Request Body (JSON):**
| Campo | Tipo | Requerido | Descripción |
| :--- | :--- | :--- | :--- |
| `estado` | String | **Sí** | Nuevo estado de la máquina (ej. EN_MANTENIMIENTO, OCUPADA, DISPONIBLE).|

```bash
{
    "estado": "EN_MANTENIMIENTO"
}
```

**Response Body 200 Ok (JSON):**
```bash
{
    "capacidad": 16.0,
    "estado": "EN_MANTENIMIENTO",
    "id": 2,
    "tiempo_ciclo": 40,
    "tipo_maquina": "SECADORA"
}
```

**400 Bad Request (JSON):**
- Mensaje 1 (Valor no permitido en el Enum):
    ```bash
    {
        "error": "Valor de estado no válido"
    }
    ```
- Mensaje 2 (Campo faltante o valor de estado no válido):
    ```bash
    {
        "error": "El campo 'estado' es requerido"
    }
    ```

**404 Not Found (JSON):**
```bash
{
    "error": "Máquina no encontrada"
}
```

## Actualizar el tipo de máquina

Permite cambiar el tipo de un equipo ya registrado (por ejemplo, de secadora a lavadora o viceversa).

**Método:** `PATCH`

**Autenticación:** Sin aplicar todavía.

**Parámetros:** 
- id (Path): ID único de la máquina.
- tipo_maquina (Body): Parte del cuerpo de la URL para ejecutar el endpoint.

**Endpoint:** `http://127.0.0.1:8000/api/v1/maquinas/{id}/tipo_maquina`

**Request Body (JSON):**
| Campo | Tipo | Requerido | Descripción |
| :--- | :--- | :--- | :--- |
| `tipo_maquina` | String | **Sí** | Nuevo tipo de máquina (LAVADORA o SECADORA).

```bash
{
    "tipo_maquina": "SECADORA"
}
```

**Response Body 200 Ok (JSON):**
```bash
{
    "capacidad": 16.0,
    "estado": "EN_MANTENIMIENTO",
    "id": 2,
    "tiempo_ciclo": 40,
    "tipo_maquina": "SECADORA"
}
```

**400 Bad Request (JSON):**
- Mensaje 1 (Valor no permitido en el Enum):
    ```bash
    {
        "error": "Valor de tipo_maquina no válido"
    }
    ```
- Mensaje 2 (Campo faltante o valor de estado no válido):
    ```bash
    {
        "error": "El campo 'tipo_maquina' es requerido"
    }
    ```

**404 Not Found (JSON):**
```bash
{
    "error": "Máquina no encontrada"
}
```

## Borrar una máquina

Elimina permanentemente una máquina del sistema utilizando su ID.

**Método:** `DELETE`

**Autenticación:** Sin aplicar todavía.

**Parámetros:** 
- id: ID único de la máquina a eliminar.

**Endpoint:** `http://127.0.0.1:8000/api/v1/maquinas/{id}`

**Request Body (JSON):**
```bash
No lleva Request Body (JSON)
```

**Response Body 200 Ok (JSON):**
```bash
{
    "message": "Máquina 4 eliminada correctamente"
}
```

**404 Not Found (JSON):**
```bash
{
    "error": "Máquina no encontrada"
}
```

# Endpoints de Servicios

## Mostrar todos los servicios

Retorna una lista con todos los servicios configurados en el sistema.

**Método:** `GET`

**Autenticación:** Sin aplicar todavía.

**Parámetros:** 
- Ninguno

**Endpoint:** `http://127.0.0.1:8050/api/v1/servicios`

**Request Body (JSON):**
```bash
No lleva Request Body (JSON)
```

**Response Body 200 Ok (JSON):**
```bash
[
    {
        "costo_referencia": 35.0,
        "id": 1,
        "metrica_cobro": "PAGO_POR_KILO",
        "tipo_servicio": "SERVICIO_POR_KILO"
    },
    {
        "costo_referencia": 50.0,
        "id": 2,
        "metrica_cobro": "PAGO_POR_USO",
        "tipo_servicio": "SERVICIO_POR_USO"
    },
    {
        "costo_referencia": 100.0,
        "id": 3,
        "metrica_cobro": "PAGO_POR_PRENDA_ESPECIAL",
        "tipo_servicio": "SERVICIO_POR_PRENDA_ESPECIAL"
    }
]
```

## Mostrar el servicio por el ID

Retorna la información detallada de un servicio específico según su identificador numérico único.

**Método:** `GET`

**Autenticación:** Sin aplicar todavía.

**Parámetros:** 
- id: ID único de la máquina.

**Endpoint:** `http://127.0.0.1:8050/api/v1/servicios/{id}`

**Request Body (JSON):**
```bash
No lleva Request Body (JSON)
```

**Response Body 200 Ok (JSON):**
```bash
{
    "costo_referencia": 35.0,
    "id": 1,
    "metrica_cobro": "PAGO_POR_KILO",
    "tipo_servicio": "SERVICIO_POR_KILO"
}
```

**404 Not Found (JSON):**
```bash
{
    "error": "Servicio no encontrado"
}
```

## Registrar un nuevo servicio

Da de alta un nuevo tipo de servicio de lavandería en el sistema.

**Método:** `POST`

**Autenticación:** Sin aplicar todavía.

**Parámetros:** 
- Ninguno

**Endpoint:** `http://127.0.0.1:8050/api/v1/servicios`

**Request Body (JSON):**
| Campo | Tipo | Requerido | Descripción |
| :--- | :--- | :--- | :--- |
| `tipo_servicio` | String | **Sí** | Nombre descriptivo del tipo de servicio.
| `metrica_cobro` | String | **Sí** | Métrica asociada (PAGO_POR_KILO, PAGO_POR_USO, etc.).
| `costo_referencia` | Float | **Sí** | Costo base o de referencia del servicio.

```bash
{
    "tipo_servicio": "SERVICIO_POR_PRENDA_ESPECIAL",
    "metrica_cobro": "PAGO_POR_PRENDA_ESPECIAL",
    "costo_referencia": 100.0
}
```

**Response Body 201 Created (JSON):**
```bash
{
    "costo_referencia": 100.0,
    "id": 5,
    "metrica_cobro": "PAGO_POR_PRENDA_ESPECIAL",
    "tipo_servicio": "SERVICIO_POR_PRENDA_ESPECIAL"
}
```

**400 Bad Request (JSON):**
```bash
{
    "error:": "Datos de entrada inválidos: 'SERVICIO_ESPECIAL' is not a valid TipoServicioEnum"
}
```

## Cotizar cobro por kilo

Calcula el subtotal del servicio basándose en la cantidad de kilos procesados, tomando el estatus express directamente del JSON enviado por el cliente.

**Método:** `POST`

**Autenticación:** Sin aplicar todavía.

**Parámetros:** 
- cotizar (Body): Parte del cuerpo de la URL para ejecutar el endpoint. 
- kilo (Body): Parte del cuerpo de la URL para ejecutar el endpoint.

**Endpoint:** `http://127.0.0.1:8050/api/v1/servicios/cotizar/kilo`

**Request Body (JSON):**
| Campo | Tipo | Requerido | Descripción |
| :--- | :--- | :--- | :--- |
| `servicio_id` | Integer | **Sí** | ID del servicio configurado para kilos.
| `cantidad_kilos` | Float | **Sí** | Peso total en kilogramos.
| `express` | Boolean | **No** | Define si es un servicio express (true o false, por defecto false).

```bash
{
    "servicio_id": 1,
    "cantidad_kilos": 13.0,
    "express": false
}
```

**Response Body 200 Ok (JSON):**
```bash
{
    "cantidad_procesada": 13.0,
    "es_express": false,
    "servicio_id": 1,
    "subtotal_calculado": 310.0
}
```

**400 Bad Request (JSON):**
- Mensaje 1 (campo 'servicio_id' requerido):
    ```bash
    {
        "error": "El campo 'servicio_id' es obligatorio"
    }
    ```
- Mensaje 2 (datos incorrectos dentro del JSON):
    ```bash
    {
        "error": "Datos de entrada inválidos: invalid literal for int() with base 10: ''"
    }
    ```

**404 Not Found (JSON):**
```bash
{
    "error": "El servicio especificado no existe en la base de datos"
}
```

## Cotizar cobro por uso

Calcula el subtotal basándose en el tiempo transcurrido entre t_inicio y t_final (calculando ciclos mediante techo matemático), tomando el estatus express directamente del JSON enviado por el cliente.

**Método:** `POST`

**Autenticación:** Sin aplicar todavía.

**Parámetros:** 
- cotizar (Body): Parte del cuerpo de la URL para ejecutar el endpoint. 
- uso (Body): Parte del cuerpo de la URL para ejecutar el endpoint.

**Endpoint:** `http://127.0.0.1:8050/api/v1/servicios/cotizar/uso`

**Request Body (JSON):**
| Campo | Tipo | Requerido | Descripción |
| :--- | :--- | :--- | :--- |
| `servicio_id` | Integer | **Sí** | ID del servicio por uso.
| `t_inicio` | String | **Sí** | Hora de inicio en formato ISO 8601.
| `t_final` | String | **Sí** | Hora de fin en formato ISO 8601.
| `express` | Boolean | **No** | Define si es un servicio express (true o false, por defecto false).

```bash
{
    "servicio_id": 2,
    "t_inicio": "2026-10-29T12:00:00",
    "t_final": "2026-10-29T12:45:00",
    "express": false
}
```

**Response Body 200 Ok (JSON):**
```bash
{
    "es_express": false,
    "minutos_totales": 45.0,
    "numero_ciclos": 2,
    "servicio_id": 2,
    "subtotal_calculado": 100.0
}
```

**400 Bad Request (JSON):**
- Mensaje 1 (campo 'servicio_id' requerido):
    ```bash
    {
        "error": "El campo 'servicio_id' es obligatorio"
    }
    ```
- Mensaje 2 (tiempo final menor que el inicial):
    ```bash
    {
        "error": "El tiempo final no puede ser menor al de inicio"
    }
    ```
- Mensaje 3 (datos incorrectos dentro del JSON):
    ```bash
    {
        "error": "Datos de entrada inválidos: invalid literal for int() with base 10: ''"
    }
    ```

**404 Not Found (JSON):**
```bash
{
    "error": "El servicio especificado no existe en la base de datos"
}
```

## Cotizar cobro por prenda especial

Calcula el subtotal multiplicando la cantidad de piezas o prendas especiales por el costo de referencia, tomando el estatus express directamente del JSON enviado por el cliente.

**Método:** `POST`

**Autenticación:** Sin aplicar todavía.

**Parámetros:** 
- cotizar (Body): Parte del cuerpo de la URL para ejecutar el endpoint. 
- prenda-especial (Body): Parte del cuerpo de la URL para ejecutar el endpoint.

**Endpoint:** `http://127.0.0.1:8050/api/v1/servicios/cotizar/prenda-especial`

**Request Body (JSON):**
| Campo | Tipo | Requerido | Descripción |
| :--- | :--- | :--- | :--- |
| `servicio_id` | Integer | **Sí** | ID del servicio especial.
| `cantidad_prendas_especiales` | Integer | **Sí** | Número de piezas o prendas a procesar.
| `express` | Boolean | **No** | Bandera express opcional (true / false).

```bash
{
    "servicio_id": 3,
    "cantidad_prendas_especiales": 3,
    "express": true
}
```

**Response Body 200 Ok (JSON):**
```bash
{
    "cantidad_piezas": 3,
    "es_express": true,
    "servicio_id": 3,
    "subtotal_calculado": 350.0
}
```

**400 Bad Request (JSON):**
- Mensaje 1 (campo 'servicio_id' requerido):
    ```bash
    {
        "error": "El campo 'servicio_id' es obligatorio"
    }
    ```
- Mensaje 2 (datos incorrectos dentro del JSON):
    ```bash
    {
        "error": "Datos de entrada inválidos: invalid literal for int() with base 10: ''"
    }
    ```

**404 Not Found (JSON):**
```bash
{
    "error": "El servicio especificado no existe en la base de datos"
}
```

## Actualizar los datos del servicio

Actualiza los datos de un servicio existente utilizando su ID.

**Método:** `PUT`

**Autenticación:** Sin aplicar todavía.

**Parámetros:** 
- id: ID único del servicio a actualizar.

**Endpoint:** `http://127.0.0.1:8050/api/v1/servicios/{id}`

**Request Body (JSON):**
| Campo | Tipo | Requerido | Descripción |
| :--- | :--- | :--- | :--- |
| `tipo_servicio` | String | **Sí** | ID único del servicio a actualizar.
| `metrica_cobro` | String | **Sí** | Tipo de servicio actualizado.
| `costo_referencia` | Float | **No** | Nuevo costo de referencia.

```bash
{
    "tipo_servicio": "SERVICIO_POR_PRENDA_ESPECIAL",
    "metrica_cobro": "PAGO_POR_PRENDA_ESPECIAL",
    "costo_referencia": 100.0
}
```

**Response Body 200 Ok (JSON):**
```bash
{
    "costo_referencia": 100.0,
    "id": 3,
    "metrica_cobro": "PAGO_POR_PRENDA_ESPECIAL",
    "tipo_servicio": "SERVICIO_POR_PRENDA_ESPECIAL"
}
```

**400 Bad Request (JSON):**
```bash
{
    "error": "Valor ENUM inválido: '' is not a valid TipoServicioEnum "
}
```

**404 Not Found (JSON):**
```bash
{
  "error": "Servicio no encontrado"
}
```

## Borrar un servicio

Elimina un servicio permanentemente del sistema por medio de su ID.

**Método:** `DELETE`

**Autenticación:** Sin aplicar todavía.

**Parámetros:** 
- id: ID único del servicio a eliminar.

**Endpoint:** `http://127.0.0.1:8050/api/v1/servicios/{id}`

**Request Body (JSON):**
```bash
No lleva Request Body (JSON)
```

**Response Body 200 Ok (JSON):**
```bash
{
    "message": "Servicio 6 eliminado correctamente"
}
```

**404 Not Found (JSON):**
```bash
{
    "error": "Servicio no encontrado"
}
```