import uuid
import logging
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from flask import request, current_app

logger = logging.getLogger(__name__)

# ultima actividad de cada token (por jti). Se guarda en memoria.
last_activity = {}

def hash_password(password: str) -> str:
    # Generar hash con sal
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, password_hash: str) -> bool:
    # Comparar contraseña con el hash guardado
    return bcrypt.checkpw(password.encode(), password_hash.encode())

def create_token(user_id, rol: str) -> str:
    now = datetime.now(timezone.utc)

    # Limpiar registros de tokens que ya vencieron por inactividad
    limite = now - timedelta(minutes=current_app.config['INACTIVITY_MINUTES'])
    for k in [k for k, v in last_activity.items() if v < limite]:
        del last_activity[k]

    # Id unico del token y actividad inicial
    jti = str(uuid.uuid4())
    last_activity[jti] = now

    payload = {
        "sub": str(user_id),
        "rol": rol,
        "jti": jti,
        "exp": now + timedelta(hours=current_app.config['MAX_SESSION_HOURS'])
    }

    # Firmar token
    return jwt.encode(payload, current_app.config['JWT_SECRET'], algorithm="HS256")

def get_token() -> str | None:
    # Leer header Authorization: Bearer <token>
    header = request.headers.get("Authorization", "")

    # Validar formato
    if not header.startswith("Bearer "):
        return None

    return header.split(" ", 1)[1]

def decode_token(token: str) -> dict | None:
    # Validar firma y expiracion
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET'], algorithms=["HS256"])
    except jwt.InvalidTokenError as e:
        logger.warning(e)
        return None

    # Validar inactividad
    now = datetime.now(timezone.utc)
    last = last_activity.get(payload.get("jti"))
    inactividad = timedelta(minutes=current_app.config['INACTIVITY_MINUTES'])

    if not last or now - last > inactividad:
        last_activity.pop(payload.get("jti"), None)
        return None

    # Hubo actividad: reiniciar el contador
    last_activity[payload["jti"]] = now
    return payload
