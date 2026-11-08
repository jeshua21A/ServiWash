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

#url de conexion
CONURL = (
    "mysql+mysqlconnector://"
    f"{os.environ.get("DBUSER")}:{os.environ.get("DBPASS")}"
    f"@{os.environ.get("DBSERVER")}/{os.environ.get("DBNAME")}?charset=utf8mb4"
)

#motor de conexion y sesion
engine = create_engine(CONURL)
Session = sessionmaker(bind=engine)

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