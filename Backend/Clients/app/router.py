from flask import Blueprint, jsonify, request
from .data import ClientRepository

#blueprint de cliente
bp = Blueprint("clients",__file__)

#repositorio de clientes
repo = ClientRepository()
    
#metodos rest
@bp.get("/")
def root():
    #obtener parametro query
    page = request.args.get('page',0,int)
    per_page = request.args.get('per_page',10,int)
    
    #obtener clientes
    clients = repo.get_clients(page,per_page)
    
    return jsonify(clients), 200

@bp.get("/<id>")
def info(id:int):
    #obtener cliente
    client = repo.get_client(id)
    
    #verificar estado
    if not client:
        return jsonify({"detail":"client not found"}), 404
    
    #retornar cliente
    return jsonify(client), 200

@bp.post("/")
def create():
    #obtener datos
    data = request.get_json()
    
    #validar si ya existe
    prev = repo.get_client(name=data["name"])
    if prev:
        return jsonify({"msg":"client already exists!!!","id":prev["id"]}), 200
    
    #ejecutar operacion
    id = repo.create_client(data)
    
    #verificar creacion
    if not id:
        return jsonify({"detail":"client not created"}), 500
    
    #retornar respuesta
    return jsonify({"msg":"client created!!!","id":id}), 200

@bp.put("/<id>")
def update(id:int):
    #obtener los datos
    data = request.get_json()
    
    #ejecutar operacion
    res = repo.update_client(id,data)
    
    #validar actualziacion
    if not res:
        return jsonify({"detail":"client not updated"}), 500
    
    #obtener cliente
    return jsonify({"id": id, "msg": "client updated!!!"}), 200

@bp.delete("/<id>")
def delete(id:int):
    #ejecutar operacion
    res = repo.delete_client(id)
    
    #validar eliminacion
    if not res:
        return jsonify({"detail":"client not deleted"}), 500
    
    #obtener cliente
    return jsonify({"id": id, "msg": "client deleted!!!"}), 200