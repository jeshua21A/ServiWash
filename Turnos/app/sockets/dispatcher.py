from datetime import datetime
from typing import TypedDict, List
import requests
from .manager import SocketManager
from ..data import TurnRepository

class Machine(TypedDict):
    #campos
    id:int
    capacidad:float
    estado:str
    tiempo_ciclo:int
    tipo_maquina:str

#despachador de turnos
class TurnDispatcher:
    #constructor
    def __init__(self, manager:SocketManager, repo:TurnRepository):
        self.repo = repo
        self.manager = manager
        self.machines:List[Machine] = requests.get(
            "http://localhost:8000/api/v1/maquinas"
        ).json()
        self.asigns = { machine["id"]:"" for machine in self.machines }
        self.counter = 0
        self.queue = []
    
    #metodos de dispatcher
    def queue_client(self, id:int)->None:
        #aumentar el contador de turnos
        self.counter += 1
        
        #añadir cliente a la cola
        self.queue.append(id)
        
        #notificar al cliente
        self.manager.notifyEvent({
            "event": "join_reply",
            "emiter_id": 0,
            "emiter_type": "server",
            "payload": {
                "turn": self.counter,
                "client_id": id
            }
        })
        
        #ver si se le puede asignar un recurso
        self.__asign_source()
        
    #metodo asignador
    def __asign_source(self):
        #obtener el primer recurso libre
        first_free = ""
        for id, asign in self.asigns.items():
            #verificar si no tiene asignado un cliente
            if not asign:
                first_free = id
                break
            
        #validar disponibilidad
        if not first_free:
            return
            
        #validar cola (cola vacia)
        if not len(self.queue):
            return
        
        #obtenemos el primer cliente de la cola
        first = self.queue.pop(0)
        
        #asignamos el recurso
        self.asigns[first_free] = first
        
        #registrar turno en bd aqui
        stored_id = self.repo.create_turn({
            "start_hour": datetime.now(),
            "machine_id": first_free,
            "client_id": first
        })
        
        #notificar evento
        self.manager.notifyEvent({
            "event": "asign",
            "emiter_id": 0,
            "emiter_type": "server",
            "payload": {
                "client": first,
                "machine": first_free,
                "stored_id": stored_id
            }
        })
        
    def release_client(self, machine:int, stored_id:int):
        #eliminar la asociacion
        self.asigns[machine] = ""
        
        #cerrar turno en bd
        self.repo.update_turn(stored_id,{
            "close_hour": datetime.now()
        })
        
        #notificar al cliente
        self.manager.notifyEvent({
            "event": "release_reply",
            "emiter_id": 0,
            "emiter_type": "server",
            "payload": {
                "machine": machine
            }
        })
        
        #asignar recurso liberado
        self.__asign_source()