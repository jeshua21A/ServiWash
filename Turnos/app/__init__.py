import logging
import json
from flask import Flask
from flask_cors import CORS
from flask_websockets import WebSockets, WebSocket
import requests
from .sockets import SocketManager, TurnDispatcher

#configuracion de logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d/%m/%Y - %H:%M:%S"
)
logger = logging.getLogger(__name__)

#capa de websockets
websockets = WebSockets()

#manager de sockets
manager = SocketManager()

#dispatcher de turnos
dispatcher = TurnDispatcher(manager)

#endpoint de sockets
@websockets.route("/ws")
def handle_socket(ws:WebSocket):
    #añadir el cliente
    manager.addClient(ws)
    
    #evento inicial
    data = json.loads(ws.receive())
    
    #registra cliente
    res = requests.post(
        "http://localhost:5000/",
        json={
            "name": data["payload"]["client_name"]
        }
    ).json()
    
    #añadir al dispatcher
    dispatcher.queue_client(res["id"])
    
    #manejo de socket
    while True:
        #recibir datos del cliente
        data = json.loads(ws.receive())
        
        #segun el evento
        if data["event"] == "release":
            #liberar el recurso
            dispatcher.release_client(data["payload"]["machine"])
            continue
        
        if data["event"] == "leave":
            #elimiar ws del manager
            manager.dropClient(ws)
            
            #respuesta
            manager.notifyEvent({
                "event": "leave_reply",
                "emiter_id": 0,
                "emiter_type": "server",
                "payload": "leave ok"
            })
            break

#factory de app
def create_app()->Flask:
    #app de flask
    app = Flask(__name__)

    #capa de websockets y cors
    CORS(app)
    websockets.init_app(app)
    
    #TODO: registrar rutas REST
    
    return app