import os
import contextlib
import logging
import threading
from urllib.parse import urlparse

import requests
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from flask_websockets import WebSockets, WebSocket
from websockets.sync.client import connect as ws_connect
from dotenv import load_dotenv
from auth import token_required

load_dotenv()
app = Flask(__name__)
CORS(app)

# Configuración del logger
logger = logging.getLogger(__name__)

# Capa de websockets del gateway
ws_server = WebSockets(app)

# Apunta al puerto interno donde corre tu microservicio de servicios
SERVICES = {
    "usuarios": os.getenv("USERS_URL", "http://127.0.0.1:5003"),
    "clientes": os.getenv("CLIENTS_URL", "http://127.0.0.1:5001"),
    "maquinas": os.getenv("MACHINES_URL", "http://127.0.0.1:5004"),
    "servicios": os.getenv("SERVICES_URL", "http://127.0.0.1:5005"),
    "turnos": os.getenv("TURNS_URL", "http://127.0.0.1:5002"),
    "tickets": os.getenv("TICKETS_URL", "http://127.0.0.1:5006")
}

def proxy_request(service_base_url, path):
    """
    Función genérica de reenvío (Proxy Reverso).
    Intercepta la petición que llega al Gateway y la redirige al microservicio 
    interno correspondiente, manteniendo cabeceras, parámetros, datos y cookies.
    """
    # Construye la URL de destino combinando la base del servicio y la ruta (path)
    target_url = f"{service_base_url}/{path}"
    # Copia las cabeceras originales de la petición del cliente, excluyendo el 'Host'
    headers = {key: value for (key, value) in request.headers if key != 'Host'}

    try:
        # Reenvía la petición HTTP al microservicio interno utilizando la librería requests
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            params=request.args,      # Reenvía los Query Params
            data=request.get_data(),  # Reenvía el cuerpo de la petición (JSON)
            cookies=request.cookies,  # Reenvía las cookies si las hubiera
            timeout=10                # Tiempo límite de espera de respuesta (10 segundos)
        )

        # Encabezados de red que deben excluirse al retornar la respuesta al cliente final
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = [
            (name, value) for (name, value) in resp.raw.headers.items()
            if name.lower() not in excluded_headers
        ]

        # Retorna la respuesta obtenida del microservicio interno manteniendo su estatus y headers
        return Response(resp.content, resp.status_code, response_headers)

    except requests.exceptions.ConnectionError:
        # Si el microservicio interno está apagado o no responde, devuelve un error HTTP 503
        return jsonify({"error": "El microservicio de destino no está disponible o encendido"}), 503

def websocket_url(service_base_url, path):
    """
    Convierte la URL base HTTP de un microservicio en su equivalente WebSocket.
    Ej: http://127.0.0.1:5002 -> ws://127.0.0.1:5002/ws
    """
    parsed = urlparse(service_base_url)
    scheme = "wss" if parsed.scheme == "https" else "ws"
    return f"{scheme}://{parsed.netloc}/{path}"

# RUTA WEBSOCKET DEL API GATEWAY (Proxy Reverso de sockets)
# Endpoint expuesto SIN validación de token: el cliente se conecta a
# ws://<gateway>/ws y el gateway retransmite los mensajes hacia y desde
# el endpoint /ws del microservicio de turnos.
@ws_server.route("/ws")
def gateway_turnos_ws(client:WebSocket):
    target_url = websocket_url(SERVICES["turnos"], "ws")

    try:
        # Abrir la conexión WebSocket contra el microservicio de turnos
        stack = contextlib.ExitStack()
        upstream = stack.enter_context(
            ws_connect(target_url, proxy=None)
        )
    except Exception as e:
        # Si el microservicio no está disponible, se cierra el socket del cliente
        logger.warning(f"No se pudo conectar al websocket de turnos: {e}")
        with contextlib.suppress(RuntimeError):
            client.close(1011, "turnos service unavailable")
        return

    # Reenvía los mensajes del microservicio hacia el cliente del gateway
    def pump_upstream():
        try:
            for message in upstream:
                client.send(message)
        except Exception as e:
            logger.info(f"Websocket de turnos finalizado: {e}")
        finally:
            # Al cerrarse el microservicio, se cierra también el cliente del gateway
            with contextlib.suppress(RuntimeError, OSError):
                client.close(1000, "upstream closed")

    thread = threading.Thread(target=pump_upstream, name="gateway-ws-upstream", daemon=True)
    thread.start()

    try:
        # Reenvía los mensajes del cliente del gateway hacia el microservicio
        for message in client.iter_data():
            upstream.send(message)
    except Exception as e:
        logger.info(f"Websocket del cliente finalizado: {e}")
    finally:
        # Limpieza de ambas conexiones al terminar el relay
        with contextlib.suppress(Exception):
            stack.close()
        with contextlib.suppress(RuntimeError, OSError):
            client.close()
        thread.join(timeout=5)

# RUTAS DEL API GATEWAY (Puntos de entrada centralizados)
@app.route("/api/v1/usuarios/", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@app.route("/api/v1/usuarios/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def gateway_usuarios(path=""):
    return proxy_request(SERVICES["usuarios"], path)

@app.route("/api/v1/clientes/", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@app.route("/api/v1/clientes/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@token_required # Autenticación implementada
def gateway_clientes(path=""):
    return proxy_request(SERVICES["clientes"], path)

@app.route("/api/v1/maquinas/", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@app.route("/api/v1/maquinas/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@token_required # Autenticación implementada
def gateway_maquinas(path=""):
    return proxy_request(SERVICES["maquinas"], path)

@app.route("/api/v1/servicios/", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@app.route("/api/v1/servicios/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@token_required # Autenticación implementada
def gateway_servicios(path=""):
    return proxy_request(SERVICES["servicios"], path)

@app.route("/api/v1/turnos/", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@app.route("/api/v1/turnos/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@token_required # Autenticación implementada
def gateway_turnos(path=""):
    return proxy_request(SERVICES["turnos"], path)

@app.route("/api/v1/tickets/", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@app.route("/api/v1/tickets/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@token_required # Autenticación implementada
def gateway_tickets(path=""):
    return proxy_request(SERVICES["tickets"], path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)