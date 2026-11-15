import logging
import json
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_websockets import WebSockets, WebSocket
import requests
from .sockets import SocketManager, TurnDispatcher
from .routes import bp
from .data import TurnRepository
from .auth import get_token

#configuracion de logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d/%m/%Y - %H:%M:%S"
)
logger = logging.getLogger(__name__)

#obtener el modo
DEBUG = os.environ.get("DEBUG")

#capa de websockets
websockets = WebSockets()

#manager de sockets
manager = SocketManager()

#dispatcher de turnos
dispatcher = TurnDispatcher(manager,TurnRepository())

#endpoint de sockets
@websockets.route("/ws")
def handle_socket(ws:WebSocket):
    #manejo de error
    try:
        #añadir el cliente
        manager.addClient(ws)
        
        #evento inicial
        data = json.loads(ws.receive())
        
        #registra cliente
        res = requests.post(
            "http://localhost:5001/",
            json={
                "name": data["payload"]["client_name"]
            }
        ).json()
        
        #añadir al dispatcher
        dispatcher.queue_client(res["id"],data["payload"]["machine_type"])
        
        #manejo de socket
        while True:
            #recibir datos del cliente
            data = json.loads(ws.receive())
            
            #segun el evento
            if data["event"] == "release":
                #liberar el recurso
                dispatcher.release_client(
                    data["payload"]["machine"],
                    data["payload"]["stored_id"],
                    data["payload"]["machine_type"]
                )
                continue
            
            if data["event"] == "leave":
                #elimiar ws del manager
                manager.dropClient(ws)
                
                #respuesta
                ws.send_json({
                    "event": "leave_reply",
                    "emiter_id": 0,
                    "emiter_type": "server",
                    "payload": "leave ok"
                })
                ws.close()
                break
    except RuntimeError as e:
        logger.warning("Connection interrupted!!!")
        logger.warning(f"log: {e}")

#factory de app
def create_app()->Flask:
    #app de flask
    app = Flask(__name__)

    #capa de websockets y cors
    CORS(app)
    websockets.init_app(app)
    
    #manejadores de error
    @app.errorhandler(404)
    def not_found(error):
        #retornar respuesta
        return jsonify({"detail":"not found"}), 404

    @app.errorhandler(Exception)
    def internal_error(e):
        #retornar mensaje
        return jsonify({"detail":str(e)}), 500

    @app.before_request
    def middleware():
        #validar modo
        if DEBUG:
            return
        
        #obtener token
        tk = get_token()
        
        #validar header de token
        if not tk:
            return jsonify({"msg":"not allowed"}), 401
    
    #añadir empoint rest
    app.register_blueprint(bp)
    
    return app