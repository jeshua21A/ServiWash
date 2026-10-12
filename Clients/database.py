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
    __tablename__ = "cliente"
    
    #campos
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    name = Column(
        String(100),
        name="nombre"
    )
    email = Column(String(100))

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