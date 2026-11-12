import os
import logging
import jwt
from functools import wraps
from flask import jsonify, request
from dotenv import load_dotenv

#cargar variables de entorno
load_dotenv()

#logger de seguridad
logger = logging.getLogger(__name__)
 
#configuracion de seguridad
SECRET = os.environ.get("SECRET_KEY")

def get_token()->str|None:
    #leer header Authorization: Bearer <token>
    header = request.headers.get("Authorization", "")

    #validar formato
    if not header.startswith("Bearer "):
        return None

    return header.split(" ", 1)[1]

def decode_token(token:str)->dict|None:
    """Valida la firma criptográfica y la expiración automática (exp) del token."""
    try:
        # PyJWT valida automaticamente la firma y el 'exp' (expiración)
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Intento de acceso con toekn expirado.")
        return None
    except jwt.InvalidTokenError as e:
        #log de error
        logger.warning(f"Token inválido: {e}")
        return None

def token_required(f):
    """Decorador para proteger endpoints exigiendo un token JWT válido."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # 1. Extraer el token del header Authorization
        token = get_token()

        if not token:
            return jsonify({"error": "Token de autenticacion faltante o formato incorrecto (Bearer <token>)"}), 401

        # 2. Validar el token (firma, expiración e inactividad)
        payloads = decode_token(token)

        if not payloads:
            return jsonify({"error": "Token inválido o expirado"}), 401

        # Opcional: Inyectar los datos del payload en el objeto request
        # por si necesitas usar ID del usuario u otros datos dentro del endpoint
        request.user_payload = payloads

        # Si todo es correcto, ejecuta la función del endpoint original
        return f(*args, **kwargs)

    return decorated