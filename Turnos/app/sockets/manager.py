from typing import List
from flask_websockets import WebSocket

class SocketManager:
    #constructor
    def __init__(self):
        self.sockets:List[WebSocket] = []
        
    #metodos del manager
    def addClient(self, ws:WebSocket):
        #añadir a la lista
        self.sockets.append(ws)
        
    def dropClient(self, ws:WebSocket):
        #eliminar socket
        self.sockets.remove(ws)
        
    def notifyEvent(self, event:dict):
        #reenviar a todos
        for ws in self.sockets:
            #enviar datos
            ws.send_json(event)