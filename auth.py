import os
import logging
import jwt
from functools import wraps
from flask import jsonify, request
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Configuración del logger para registrar eventos de seguridad y advertencias
logger = logging.getLogger(__name__)
 
# Configuración de seguridad: Obtiene la clave secreta para verificar la firma del token
SECRET = os.environ.get("SECRET_KEY")

def get_token()->str|None:
    """
    Extrae el token JWT de la cabecera 'Authorization' de la petición HTTP.
    Se espera el formato estándar: 'Bearer <token>'
    """
    # Lee el header Authorization; si no existe, devuelve una cadena vacía
    header = request.headers.get("Authorization", "")

    # Valida que la cabecera comience estrictamente con el prefijo 'Bearer '
    if not header.startswith("Bearer "):
        return None

    # Divide la cadena en dos partes ('Bearer' y el token) y retorna únicamente el token
    return header.split(" ", 1)[1]

def decode_token(token:str)->dict|None:
    """
    Valida criptográficamente la firma del token y comprueba 
    que su tiempo de vida (expiración 'exp') siga vigente usando PyJWT.
    """
    try:
        # jwt.decode verifica automáticamente la firma con la clave SECRET y el 'exp'
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload # Retorna los datos internos del token (ej. sub, rol) si es válido
    except jwt.ExpiredSignatureError:
        # Captura el error específico cuando el token ha caducado
        logger.warning("Intento de acceso con toekn expirado.")
        return None
    except jwt.InvalidTokenError as e:
        # Captura cualquier otro error de alteración o formato inválido del token
        logger.warning(f"Token inválido: {e}")
        return None

def token_required(f):
    """
    Decorador de Flask para proteger endpoints perimetrales en el API Gateway.
    Exige la presencia y validez de un token JWT antes de permitir el acceso a la ruta.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Extrae el token desde la cabecera de la petición HTTP
        token = get_token()

        # Si el token no viene o tiene mal formato, bloquea el acceso con un 401 Unauthorized
        if not token:
            return jsonify({"error": "Token de autenticacion faltante o formato incorrecto (Bearer <token>)"}), 401

        # Valida la integridad, firma y vigencia temporal del token
        payloads = decode_token(token)

        # Si el token falló en la validación (expirado o falso), rechaza la petición
        if not payloads:
            return jsonify({"error": "Token inválido o expirado"}), 401

        # Inyecta los datos decodificados del usuario (payload) en el objeto request de Flask
        # Esto permite que los microservicios o endpoints consuman datos como el ID o rol si lo necesitan
        request.user_payload = payloads

        # Si todas las validaciones son exitosas, deja continuar la ejecución de la función original
        return f(*args, **kwargs)

    return decorated