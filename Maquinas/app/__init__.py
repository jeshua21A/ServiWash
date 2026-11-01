from flask import Flask
from flask_cors import CORS
from app.database import db_session, init_app_db

# Exponemos db_session como db para mantener la importación desde 'app'
db = db_session

def create_app(config_class = None):
    app = Flask(__name__)
    if config_class:
        app.config.from_object(config_class)

    # Habilitar CORS para permitir peticiones del frontend
    CORS(app)

    # Inicializar la base de datos con la configuración de la app
    init_app_db(app)

    # Remove/cerrar la sesión automáticamente al finalizar cada petición HTTP
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.remove()

    # Registro de Blueprints por módulos
    from app.routers import maquinas_bp
    app.register_blueprint(maquinas_bp)

    return app