import os
import logging
import jwt
from flask import request
from dotenv import load_dotenv

#cargar variables de entorno
load_dotenv()

#logger de seguridad
logger = logging.getLogger(__name__)

#configuracion de seguridad
SECRET = os.environ.get("JWT_SECRET")
INACTIVITY_MINUTES = 50

#limite maximo de sesion, aunque haya actividad
MAX_SESSION_HOURS = 12

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
    
    return payload