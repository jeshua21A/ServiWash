from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
import urllib.parse

engine = None
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False))
Base = declarative_base()
Base.query = db_session.query_property()

def init_app_db(app):
    global engine
    # Crear engine usando la URI configurada en config.py
    database_url = app.config['SQLALCHEMY_DATABASE_URI']

    try:
        # 1. Extraer el nombre de la base de datos y la URL raíz desde la URI de configuración
        parsed_url = urllib.parse.urlparse(database_url)
        db_name = parsed_url.path.lstrip('/')

        # Reconstruir una URL temporal conectándose al servidor MySQL sin especificar la base de datos
        root_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # 2. Conectarse al servidor MySQL y crear la base de datos si no existe
        temp_engine = create_engine(root_url)
        with temp_engine.connect() as connection:
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}`;"))
            connection.commit()
        temp_engine.dispose()
        print(f"Base de datos '{db_name}' verificada/creada exitosamente.")

    except Exception as ex:
        print(f"No se pudo verificar la creación automática de la base de datos: {ex}")

    # 3. Proceder con la conexión formal a la base de datos ya existente
    engine = create_engine(database_url, pool_recycle = 3600, pool_pre_ping = True)
    # Vincular el engine al scoped_session
    db_session.configure(bind = engine)

    # 4. Importar los modelos para registrarlos en los metadatos de SQLAlchemy
    import app.models

    # 5. Crear las tablas automáticamente si no existen
    Base.metadata.create_all(bind = engine)
