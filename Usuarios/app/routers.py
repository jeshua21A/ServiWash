from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Usuario, RolEnum
from app.auth import hash_password, check_password, create_token, get_token, decode_token

# Blueprint del modulo de usuarios con su prefijo base
usuarios_bp = Blueprint('usuarios_bp', __name__)

@usuarios_bp.route('/register', methods=['POST'])
def register():
    """Registra un usuario nuevo. Solo un ADMIN autenticado puede hacerlo."""
    # Validar token y rol
    payload = decode_token(get_token() or "")
    if not payload:
        return jsonify({"detail": "token invalido o expirado"}), 401
    if payload["rol"] != "ADMIN":
        return jsonify({"detail": "solo un admin puede registrar usuarios"}), 403

    # Obtener datos
    data = request.get_json(silent=True) or {}
    nombre_usuario = data.get("nombre_usuario")
    password = data.get("password")
    rol = data.get("rol")

    # Validar datos
    if not nombre_usuario or not password or rol not in [r.value for r in RolEnum]:
        return jsonify({"detail": "datos invalidos"}), 400

    # Verificar que el usuario no exista
    if db.query(Usuario).filter(Usuario.nombre_usuario == nombre_usuario).first():
        return jsonify({"detail": "usuario ya registrado"}), 409

    # Guardar usuario con contraseña hasheada
    try:
        nuevo = Usuario(
            nombre_usuario = nombre_usuario,
            password_hash = hash_password(password),
            rol = RolEnum(rol)
        )
        db.add(nuevo)
        db.commit()
        return jsonify({"msg": "usuario creado!", "id": nuevo.id}), 200
    except Exception:
        db.rollback()
        return jsonify({"detail": "usuario no creado"}), 500

@usuarios_bp.route('/login', methods=['POST'])
def login():
    """Valida credenciales y devuelve un token JWT."""
    data = request.get_json(silent=True) or {}
    nombre_usuario = data.get("nombre_usuario")
    password = data.get("password") or ""

    # Buscar usuario
    user = db.query(Usuario).filter(Usuario.nombre_usuario == nombre_usuario).first()

    # Validar credenciales y que el usuario esté activo (mismo mensaje en todos los casos)
    if not user or not user.esta_activo or not check_password(password, user.password_hash):
        return jsonify({"detail": "invalid credentials"}), 401

    # Retornar token
    return jsonify({
        "token": create_token(user.id, user.rol.value),
        "rol": user.rol.value,
        "expires_in": int(current_app.config['INACTIVITY_MINUTES'] * 60)
    }), 200

@usuarios_bp.route('/verify', methods=['POST'])
def verify():
    """Lo usan los demás microservicios para validar un token."""
    payload = decode_token(get_token() or "")

    # Token inválido, expirado o inactivo
    if not payload:
        return jsonify({"valid": False, "detail": "token invalido o expirado"}), 401

    return jsonify({"valid": True, "id": payload["sub"], "rol": payload["rol"]}), 200

@usuarios_bp.route('/refresh', methods=['POST'])
def refresh():
    """Cambia un token válido por uno nuevo."""
    payload = decode_token(get_token() or "")

    if not payload:
        return jsonify({"detail": "token invalido o expirado"}), 401

    return jsonify({
        "token": create_token(payload["sub"], payload["rol"]),
        "expires_in": int(current_app.config['INACTIVITY_MINUTES'] * 60)
    }), 200
