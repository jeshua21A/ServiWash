import os
from contextlib import contextmanager
from sqlalchemy import Column, String, Integer, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

#cargar variables de entorno
load_dotenv()

#base de orm
Base = declarative_base()

#modelo de tabla
class User(Base):
    #nombre de tabla sql
    __tablename__ = "Usuarios"

    #campos
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    nombre_usuario = Column(
        String(100),
        unique=True,
        nullable=False
    )
    password_hash = Column(
        String(100),
        nullable=False
    )
    rol = Column(
        String(20),
        nullable=False
    )
    esta_activo = Column(
        Boolean,
        nullable=False,
        default=True
    )

#datos de conexion desde .env
DBUSER = os.environ.get("DBUSER")
DBPASS = os.environ.get("DBPASS")
DBSERVER = os.environ.get("DBSERVER")
DBNAME = os.environ.get("DBNAME")

#url de conexion
CONURL = (
    "mysql+mysqlconnector://"
    f"{DBUSER}:{DBPASS}"
    f"@{DBSERVER}/{DBNAME}?charset=utf8mb4"
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