import os
import requests
from flask import Flask, request, Response, jsonify
from dotenv import load_dotenv
from auth import token_required

load_dotenv()
app = Flask(__name__)

# Apunta al puerto interno donde corre tu microservicio de servicios
SERVICES = {
    "usuarios": os.getenv("USERS_URL", "http://127.0.0.1:5003"),
    "clientes": os.getenv("CLIENTS_URL", "http://127.0.0.1:5001"),
    "maquinas": os.getenv("MACHINES_URL", "http://127.0.0.1:5004"),
    "servicios": os.getenv("SERVICES_URL", "http://127.0.0.1:5005"),
    "turnos": os.getenv("TURNS_URL", "http://127.0.0.1:5002"),
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)