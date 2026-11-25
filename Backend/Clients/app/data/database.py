import os
from contextlib import contextmanager
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

#cargar variables de entorno
load_dotenv()

#base de orm
Base = declarative_base()

#modelo de tabla
class Client(Base):
    #nombre de tabla sql
    __tablename__ = "clientes"
    
    #campos
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    name = Column(
        String(100),
        name="nombre_cliente"
    )
    email = Column(
        String(100),
        name="email_cliente"
    )

# Parámetros de conexión a MySQL
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'serviwash')

#url de conexion
CONURL = (
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

#motor de conexion y sesion
engine = create_engine(CONURL)
Session = sessionmaker(bind=engine)

#crear en bd
Base.metadata.create_all(bind=engine)

#manejador de sesiones
@contextmanager
def get_session():
    #instancia de sesion
    session = Session()
    
    #ciclo de vida de sesion
    try:
        #guardar sesion
        yield session
    finally:
        #cierre de sesion
        session.close()