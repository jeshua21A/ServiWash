from flask import Blueprint, request, jsonify
from app import db
from app.models import Maquina, TipoMaquinaEnum, EstadoMaquinaEnum

# Creación del Blueprint para el módulo de máquinas con su prefijo base
maquinas_bp = Blueprint('maquinas_bp', __name__, url_prefix='/api/v1/maquinas')

@maquinas_bp.route('', methods=['GET'])
def get_maquinas():
    """
    Obtiene la lista de todas las máquinas registradas.
    Parámetros de consulta (Query Params):
        - estado (opcional): Filtra las máquinas según su estado actual (ej. ?estado=DISPONIBLE).
    """
    estado_param = request.args.get('estado')
    query = db.query(Maquina)
    
    if estado_param:
        query = query.filter(Maquina.estado == estado_param)
    maquinas = query.all()
    return jsonify([m.to_dict() for m in maquinas]), 200

@maquinas_bp.route('/<int:id>', methods=['GET'])
def get_maquina(id):
    """Obtiene los detalles de una máquina específica a partir de su ID único."""
    maquina = db.query(Maquina).filter(Maquina.id == id).first()

    if not maquina:
        return jsonify({"error": "Máquina no encontrada"}), 404
    return jsonify(maquina.to_dict()), 200

@maquinas_bp.route('', methods=['POST'])
def create_maquina():
    """Registra una nueva máquina en el sistema utilizando los datos JSON provistos."""
    data = request.get_json()

    try:
        nueva_maquina = Maquina(
            tipo_maquina = TipoMaquinaEnum(data['tipo_maquina']),
            capacidad = data['capacidad'],
            tiempo_ciclo = data['tiempo_ciclo'],
            estado = EstadoMaquinaEnum(data.get('estado', 'DISPONIBLE'))
        )
        db.add(nueva_maquina)
        db.commit()
        return jsonify(nueva_maquina.to_dict()), 201
    except (ValueError, KeyError) as ex:
        db.rollback()
        return jsonify({"error": f"Datos de entrada inválidos: {str(ex)}"}), 400

@maquinas_bp.route('/<int:id>/estado', methods=['PATCH'])
def update_estado_maquina(id):
    """Actualiza de forma parcial únicamente el estado de una máquina específica."""
    data = request.get_json()

    if not data or 'estado' not in data:
            return jsonify({"error": "El campo 'estado' es requerido"}), 400

    maquina = db.query(Maquina).filter(Maquina.id == id).first()
    if not maquina:
        return jsonify({"error": "Máquina no encontrada"}), 404

    try:
        maquina.estado = EstadoMaquinaEnum(data['estado'])
        db.commit()
        return jsonify(maquina.to_dict()), 200
    except ValueError:
        db.rollback()
        return jsonify({"error": f"Valor de estado no válido"}), 400

@maquinas_bp.route('/<int:id>/tipo_maquina', methods=['PATCH'])
def update_tipo_maquina(id):
    """Actualiza de forma parcial el tipo de máquina (ej. lavadora a secadora)."""
    data = request.get_json()

    if not data or 'tipo_maquina' not in data:
            return jsonify({"error": "El campo 'tipo_maquina' es requerido"}), 400

    maquina = db.query(Maquina).filter(Maquina.id == id).first()
    if not maquina:
        return jsonify({"error": "Máquina no encontrada"}), 404

    try:
        maquina.tipo_maquina = TipoMaquinaEnum(data['tipo_maquina'])
        db.commit()
        return jsonify(maquina.to_dict()), 200
    except ValueError:
        db.rollback()
        return jsonify({"error": f"Valor de tipo_maquina no válido"}), 400

@maquinas_bp.route('/<int:id>', methods=['DELETE'])
def delete_maquina(id):
    """Elimina permanentemente una máquina del sistema a partir de su ID."""
    maquina = db.query(Maquina).filter(Maquina.id == id).first()

    if not maquina:
        return jsonify({"error": "Máquina no encontrada"}), 404
    db.delete(maquina)
    db.commit()
    return jsonify({"message": f"Máquina {id} eliminada correctamente"}), 200