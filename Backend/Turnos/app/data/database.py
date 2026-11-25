import os
from contextlib import contextmanager
from sqlalchemy import Column, Integer, DATETIME, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

#cargar variables de entorno
load_dotenv()

#base de orm
Base = declarative_base()

#tabla de turnos
class Turn(Base):
    #nombre de tabla
    __tablename__ = "turnos"
    
    #columnas
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    start_hour = Column(
        DATETIME,
        nullable=False,
        name="hora_apertura"
    )
    close_hour = Column(
        DATETIME,
        nullable=True,
        name="hora_cierre"
    )
    machine_id = Column(
        Integer,
        nullable=False,
        name="maquinas_id"
    )
    client_id = Column(
        Integer,
        nullable=False,
        name="clientes_id"
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