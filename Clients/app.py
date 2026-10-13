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

#manejadores de error
@app.errorhandler(404)
def not_found(error):
    #retornar respuesta
    return jsonify({"detail":"not found"}), 404

@app.errorhandler(Exception)
def internal_error(e):
    #retornar mensaje
    return jsonify({"detail":str(e)}), 500

#metodos rest
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
    client = repo.get_client(id)
    
    #verificar estado
    if not client:
        return jsonify({"detail":"client not found"}), 404
    
    #retornar cliente
    return jsonify(client), 200

@app.post("/")
def create():
    #obtener datos
    data = request.get_json()
    
    #ejecutar operacion
    id = repo.create_client(data)
    
    #verificar creacion
    if not id:
        return jsonify({"detail":"client not created"}), 500
    
    #retornar respuesta
    return jsonify({"msg":"client created!!!","id":id}), 200

@app.put("/<id>")
def update(id:int):
    #obtener los datos
    data = request.get_json()
    
    #ejecutar operacion
    res = repo.update_client(id,data)
    
    #validar actualziacion
    if not res:
        return jsonify({"detail":"client not updated"}), 500
    
    #obtener cliente
    return jsonify({"id": id, "updated":res}), 200

@app.delete("/<id>")
def delete(id:int):
    #ejecutar operacion
    res = repo.delete_client(id)
    
    #validar eliminacion
    if not res:
        return jsonify({"detail":"client not deleted"}), 500
    
    #obtener cliente
    return jsonify({"id": id, "deleted":res}), 200