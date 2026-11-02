import os
import logging
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from flask import request
from dotenv import load_dotenv
import uuid

#cargar variables de entorno
load_dotenv()

#logger de seguridad
logger = logging.getLogger(__name__)

#configuracion de seguridad
SECRET = os.environ.get("JWT_SECRET")
INACTIVITY_MINUTES = 50

#limite maximo de sesion, aunque haya actividad
MAX_SESSION_HOURS = 12

#ultima actividad de cada token
last_activity = {}

#funciones de seguridad
def hash_password(password:str)->str:
    #generar hash con sal
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password:str, password_hash:str)->bool:
    #comparar contraseña con el hash guardado
    return bcrypt.checkpw(password.encode(), password_hash.encode())

def create_token(user:dict)->str:
    #id unico del token
    jti = str(uuid.uuid4())
    
    #registrar actividad inicial
    last_activity[jti] = datetime.now(timezone.utc)
    
    #datos del token
    payload = {
        "sub": str(user["id"]),
        "rol": user["rol"],
        "jti": jti,
        "exp": datetime.now(timezone.utc) + timedelta(hours=MAX_SESSION_HOURS)
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
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.InvalidTokenError as e:
        #log de error
        logger.warning(e)
        return None
    
    #validar inactividad
    now = datetime.now(timezone.utc)
    last = last_activity.get(payload["jti"])
    
    if not last or now - last > timedelta(minutes=INACTIVITY_MINUTES):
        last_activity.pop(payload["jti"], None)
        return None
    
    #hubo actividad: reiniciar el contador
    last_activity[payload["jti"]] = now
    return payload