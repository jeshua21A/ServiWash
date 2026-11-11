import os
from sqlalchemy import create_engine, Column, String, Integer, DECIMAL, TIMESTAMP, Enum, func
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine import URL
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv() # cargar variables de entorno

Base = declarative_base() # Base ORM

# Configuracion de la base de datos
DATABASE_URL = URL.create(
    drivername="mysql+mysqlconnector",
    username=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_NAME')
)

# Crear el motor de base de datos
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True, # verificar la conexión antes de usarla
    pool_recycle=3600, # recycle de la conexión cada 3600 segundos (1 hora)
    echo=True # echo=True para ver las consultas SQL
)

# Crear la sesión de base de datos
Session = sessionmaker(
    bind=engine,
    autocommit=False, # desactivar autocommit para manejar transacciones manualmente
    autoflush=False, # desactivar autoflush para controlar cuándo se envían los cambios a la base de datos
    expire_on_commit=False # desactivar expire_on_commit para que los objetos no se expiren automáticamente después de un commit
)

# sesión de base de datos
@contextmanager
def get_db_session():
    session = Session() # instancia de sesión
    try:
        yield session # ciclo de vida de sesión
    except Exception:
        session.rollback()
        raise
    finally:
        session.close() # cierre de sesión