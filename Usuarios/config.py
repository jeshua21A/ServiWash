import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '')

    #Parametros de conexion a MySQL
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'serviwash')

    # Cadena de conexion
    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Seguridad (JWT)
    JWT_SECRET = os.getenv('JWT_SECRET', '')
    INACTIVITY_MINUTES = 50   # la sesion expira tras 50 min sin actividad
    MAX_SESSION_HOURS = 12    # límite maximo de un token, aunque haya actividad

    # Usuarios iniciales (se crean al arrancar si no existen)
    ADMIN_USER = os.getenv('ADMIN_USER', 'admin')
    ADMIN_PASS = os.getenv('ADMIN_PASS', 'admin123')
    EMPLEADO_USER = os.getenv('EMPLEADO_USER', 'empleado')
    EMPLEADO_PASS = os.getenv('EMPLEADO_PASS', 'empleado123')
