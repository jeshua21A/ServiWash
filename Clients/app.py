import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from repository import ClientRepository

#configuracion de logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d/%m/%Y - %H:%M:%S"
)

logger = logging.getLogger(__name__)

#app principal de flask
app = Flask(__name__)

#añadir cors
CORS(app)

#repositorio de clientes
repo = ClientRepository()

#log de inicio
logger.info("app started!!!")

#metodo raiz
@app.get("/")
def root():
    #obtener parametro query
    page = request.args.get('page',0,int)
    
    #obtener clientes
    clients = repo.get_clients(page)
    
    return jsonify(clients), 200

@app.get("/<id>")
def info(id:int):
    #obtener cliente
    return jsonify(repo.get_client(id)), 200

@app.post("/")
def create():
    #obtener datos
    data = request.get_json()
    
    #ejecutar operacion
    id = repo.create_client(data)
    
    #retornar respuesta
    return jsonify({"msg":"client created!!!","id":id}), 200

@app.put("/<id>")
def update(id:int):
    #obtener los datos
    data = request.get_json()
    
    #ejecutar operacion
    res = repo.update_client(id,data)
    
    #obtener cliente
    return jsonify({"id": id, "updated":res}), 200

@app.delete("/<id>")
def delete(id:int):
    #ejecutar operacion
    res = repo.delete_client(id)
    
    #obtener cliente
    return jsonify({"id": id, "deleted":res}), 200