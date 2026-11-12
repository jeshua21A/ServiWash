import logging
from datetime import datetime, timezone, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
from repository import UserRepository
from auth import (
    hash_password, check_password,
    create_token, get_token, decode_token
)
from database import engine, Base
 
#configuracion de logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d/%m/%Y - %H:%M:%S"
)
 
logger = logging.getLogger(__name__)
 
#configuracion de seguridad
#roles permitidos
ROLES = ("ADMIN", "EMPLEADO")

#app principal de flask
app = Flask(__name__)
 
#añadir cors
CORS(app)
 
#repositorio de usuarios
repo = UserRepository()
 
#log de inicio
logger.info("app started!!!")
  
#manejadores de error
@app.errorhandler(404)
def not_found(error):
    #retornar respuesta
    return jsonify({"detail":"not found"}), 404
 
@app.errorhandler(Exception)
def internal_error(e):
    #retornar mensaje
    return jsonify({"detail":str(e)}), 500
 
#metodos rest
@app.post("/register")
def register():
    #solo un admin puede registrar usuarios
    payload = decode_token(get_token() or "")
    
    #token invalido o expirado
    if not payload:
        return jsonify({"detail":"token invalido o expirado"}), 401
    
    #validar rol
    if payload["rol"] != "ADMIN":
        return jsonify({"detail":"solo un admin puede registrar usuarios"}), 403
    
    #obtener datos
    data = request.get_json()
    nombre_usuario = data.get("nombre_usuario")
    password = data.get("password")
    rol = data.get("rol")
    
    #validar datos
    if not nombre_usuario or not password or rol not in ROLES:
        return jsonify({"detail":"datos invalidos"}), 400
    
    #verificar que el usuario no exista
    if repo.get_user_by_name(nombre_usuario):
        return jsonify({"detail":"usuario ya registrado"}), 409
    
    #guardar usuario con contraseña hasheada
    id = repo.create_user({
        "nombre_usuario": nombre_usuario,
        "password_hash": hash_password(password),
        "rol": rol
    })
    
    #verificar creacion
    if not id:
        return jsonify({"detail":"usuario no creado"}), 500
    
    #retornar respuesta
    return jsonify({"msg":"usuario creado!","id":id}), 200
 
@app.post("/login")
def login():
    #obtener datos
    data = request.get_json()
    nombre_usuario = data.get("nombre_usuario")
    password = data.get("password")
    
    #buscar usuario
    user = repo.get_user_by_name(nombre_usuario)
    
    # Validar que el usuario exista y la contraseña sea correcta
    if not user or not check_password(password, user["password_hash"]):
        return jsonify({"detail": "Credenciales inválidas"}), 401

    # Comprobar si la cuenta está activa
    if not user["esta_activo"] :
        return jsonify({"detail": "La cuenta está inactiva"}), 401

    # Calcular expiración en formato string ISO (evita el error de JSON)
    expiration_time = datetime.now(timezone.utc) + timedelta(hours=12)
    
    #retornar token
    return jsonify({
        "token": create_token(user),
        "rol": user["rol"],
        "expires_in": expiration_time.isoformat()
    }), 200
 
@app.post("/verify")
def verify():
    #validar token
    payload = decode_token(get_token() or "")
    
    #token invalido o expirado
    if not payload:
        return jsonify({"valid":False,"detail":"token invalido o expirado"}), 401
    
    #retornar datos del usuario
    return jsonify({"valid":True,"id":payload["sub"],"rol":payload["rol"]}), 200
 
@app.post("/refresh")
def refresh():
    #validar token actual
    payload = decode_token(get_token() or "")
    
    #token invalido o expirado
    if not payload:
        return jsonify({"detail":"token invalido o expirado"}), 401
    
    #generar uno nuevo, reinicia los 50 min
    user = {"id": payload["sub"], "rol": payload["rol"]}

    # Calcular expiración en formato string ISO (evita el error de JSON)
    expiration_time = datetime.now(timezone.utc) + timedelta(hours=12)
    
    return jsonify({
        "token": create_token(user),
        "expires_in": expiration_time.isoformat()
    }), 200

if __name__ == '__main__':

    Base.metadata.create_all(engine)
    logger.info("¡Tablas verificadas/creadas exitosamente en MySQL!")
    
    app.run(debug=True, host='0.0.0.0', port=5003)
