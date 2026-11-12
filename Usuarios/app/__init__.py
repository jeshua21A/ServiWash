from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from app.database import db_session, init_app_db

# Exponemos db_session como db para mantener la importacion desde 'app'
db = db_session

def seed_users(app):
    """Crea el administrador y el empleado iniciales si no existen."""
    from app.models import Usuario, RolEnum
    from app.auth import hash_password

    iniciales = [
        (app.config['ADMIN_USER'], app.config['ADMIN_PASS'], RolEnum.ADMIN),
        (app.config['EMPLEADO_USER'], app.config['EMPLEADO_PASS'], RolEnum.EMPLEADO),
    ]

    for nombre, password, rol in iniciales:
        existe = db.query(Usuario).filter(Usuario.nombre_usuario == nombre).first()
        if not existe:
            db.add(Usuario(
                nombre_usuario = nombre,
                password_hash = hash_password(password),
                rol = rol
            ))
            db.commit()
            print(f"Usuario inicial '{nombre}' ({rol.value}) creado.")

    db.remove()

def create_app(config_class = None):
    app = Flask(__name__)
    if config_class:
        app.config.from_object(config_class)

    # Sin clave secreta no se pueden firmar tokens
    if not app.config.get('JWT_SECRET'):
        raise RuntimeError("Falta JWT_SECRET en el archivo .env")

    # Habilitar CORS para permitir peticiones del frontend
    CORS(app)

    # Inicializar la base de datos (crea base y tablas si no existen)
    init_app_db(app)

    # Crear usuarios iniciales (admin y empleado)
    seed_users(app)

    # Remove/cerrar la sesión automaticamente al finalizar cada peticion HTTP
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.remove()

    # Manejadores de error
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"detail": "not found"}), 404

    @app.errorhandler(HTTPException)
    def http_error(e):
        return jsonify({"detail": e.description}), e.code

    @app.errorhandler(Exception)
    def internal_error(e):
        return jsonify({"detail": str(e)}), 500

    # Registro de Blueprints por módulos
    from app.routers import usuarios_bp
    app.register_blueprint(usuarios_bp)

    return app
