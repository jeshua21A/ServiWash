from flask import Blueprint, jsonify, request
from .data import TurnRepository

#blueprint de turno
bp = Blueprint("turns",__file__)

#repositorio de turnos
repo = TurnRepository()
    
#metodos rest
@bp.get("/")
def root():
    #obtener parametro query
    page = request.args.get('page',0,int)
    per_page = request.args.get('per_page',10,int)
    client_id = request.args.get('client_id',0,int)
    
    #obtener turnes
    turns = repo.get_turns(page,per_page,client_id)
    
    return jsonify(turns), 200

@bp.get("/<id>")
def info(id:int):
    #obtener turne
    turn = repo.get_turn(id)
    
    #verificar estado
    if not turn:
        return jsonify({"detail":"turn not found"}), 404
    
    #retornar turne
    return jsonify(turn), 200

@bp.delete("/<id>")
def delete(id:int):
    #ejecutar operacion
    res = repo.delete_turn(id)
    
    #validar eliminacion
    if not res:
        return jsonify({"detail":"turn not deleted"}), 500
    
    #obtener turne
    return jsonify({"id": id, "msg": "turn deleted!!!"}), 200