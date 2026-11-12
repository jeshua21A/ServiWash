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
        self.washing_machines:List[Machine] = requests.get(
            "http://localhost:8000/api/v1/maquinas?tipo_maquina=LAVADORA"
        ).json()
        self.dryer_machines:List[Machine] = requests.get(
            "http://localhost:8000/api/v1/maquinas?tipo_maquina=SECADORA"
        ).json()
        self.wash_asigns = { machine["id"]:"" for machine in self.washing_machines }
        self.dryer_asigns = { machine["id"]:"" for machine in self.dryer_machines }
        self.counter = 0
        self.wash_queue = []
        self.dray_queue = []
    
    #metodos de dispatcher
    def queue_client(self, id:int, machine_type:str)->None:
        #aumentar el contador de turnos
        self.counter += 1
        
        #añadir cliente a la cola
        queue = self.dryer_asigns if machine_type == "SECADORA" else self.wash_queue
        queue.append(id)
        
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
        self.__asign_source(machine_type)
        
    #metodo asignador
    def __asign_source(self, machine_type:str):
        #contenedores
        asigns = {}
        
        #seleccionar asignaciones segun el tipo
        if machine_type == "LAVADORA":
            #seleccionar lavadoras
            asigns = self.wash_asigns
        else:
            #seleccionar 
            asigns = self.dryer_asigns
        
        #obtener el primer recurso libre
        first_free = ""
        for id, asign in asigns.items():
            #verificar si no tiene asignado un cliente
            if not asign:
                first_free = id
                break
            
        #validar disponibilidad
        if not first_free:
            return
        
        #decidir la cola
        queue = self.dryer_asigns if machine_type == "SECADORA" else self.wash_queue
            
        #validar cola (cola vacia)
        if not len(queue):
            return
        
        #obtenemos el primer cliente de la cola
        first = queue.pop(0)
        
        #asignamos el recurso
        asigns[first_free] = first
        
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
        
    def release_client(self, machine:int, stored_id:int, machine_type:str):
        #seleccionar asigns
        asigns = {}
        
        #seleccionar asignaciones segun el tipo
        if machine_type == "LAVADORA":
            #seleccionar lavadoras
            asigns = self.wash_asigns
        else:
            #seleccionar 
            asigns = self.dryer_asigns
        
        #eliminar la asociacion
        asigns[machine] = ""
        
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
        self.__asign_source(machine_type)