import os
import logging
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from flask import request
from dotenv import load_dotenv

#cargar variables de entorno
load_dotenv()

#logger de seguridad
logger = logging.getLogger(__name__)

#configuracion de seguridad
SECRET = os.environ.get("SECRET_KEY")
SESSION_MINUTES = 60

#funciones de seguridad
def hash_password(password:str)->str:
    #generar hash con sal
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password:str, password_hash:str)->bool:
    #comparar contraseña con el hash guardado
    return bcrypt.checkpw(password.encode(), password_hash.encode())

def create_token(user:dict)->str:

    #datos del token
    payload = {
        "sub": str(user["id"]),
        "rol": user["rol"],
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=SESSION_MINUTES)
    }
    
    #firmar token
    return jwt.encode(payload, SECRET, algorithm="HS256")

def get_token()->str|None:
    #leer header Authorization: Bearer <token>
    header = request.headers.get("Authorization", "")

    #validar formato
    if not header.startswith("Bearer "):
        return None

    return header.split(" ", 1)[1]

def decode_token(token:str)->dict|None:
    #validar firma y expiracion
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