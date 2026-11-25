import json
import time
import random
from websockets.sync.client import connect

#variables
CLIENT_NAME = "Prueba"
SERVER_URL = "ws://localhost:5002/ws"
MACHINE_TYPE = "LAVADORA"
CLIENT_ID = 0
TRANSACTION_ID = 0

#conexion websocket
with connect(SERVER_URL) as ws:
    #mandar evento join
    ws.send(json.dumps({
        "event":"join",
        "emiter_id":CLIENT_ID,
        "emiter_type":"customer",
        "payload": {
            "client_name": CLIENT_NAME,
            "machine_type": MACHINE_TYPE
        }
    }))
    res = ws.recv()
    data = json.loads(res)
    CLIENT_ID = data["payload"]["client_id"]
    print("Replica: "+str(data["payload"]))
    
    #recibir evento
    res = ws.recv()
    #decodificar json
    data = json.loads(res)
    
    #validar evento
    if data["event"] == "asign":
        print("Asignacion: "+str(data["payload"]["client"])+" a "+str(data["payload"]["machine"]))
        if data["payload"]["client"] == CLIENT_ID:
            TRANSACTION_ID = data["payload"]["stored_id"]
            time.sleep(random.randint(0,5))
    
    #liberar recurso
    ws.send(json.dumps({
        "event":"release",
        "emiter_id":CLIENT_ID,
        "emiter_type":"customer",
        "payload": { 
            "machine": data["payload"]["machine"],
            "stored_id": TRANSACTION_ID,
            "machine_type": MACHINE_TYPE
        }
    }))
    res = ws.recv()
    data = json.loads(res)
    print("Replica: "+str(data["payload"]))
    
    #abandonar la sala
    ws.send(json.dumps({
        "event":"leave",
        "emiter_id":CLIENT_ID,
        "emiter_type":"customer",
        "payload": {}
    }))
    res = ws.recv()
    data = json.loads(res)
    print("Replica: "+data["payload"])