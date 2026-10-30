import math
from datetime import datetime
from flask import Blueprint, request, jsonify
from app import db
from app.models import TipoServicioEnum, MetricaCobroEnum, Servicio

# Creación del Blueprint para modularizar las rutas del servicio de lavandería
servicios_bp = Blueprint('servicios_bp', __name__, url_prefix='/api/v1/servicios')

# ENDPOINTS CRUD (Gestión del Catálogo)

@servicios_bp.route('', methods=['GET'])
def get_servicios():
    """Obtiene y lista todos los servicios registrados en el catálogo de la base de datos."""
    servicios = db.query(Servicio).all()
    return jsonify([s.to_dict() for s in servicios]), 200

@servicios_bp.route('/<int:id>', methods=['GET'])
def get_servicio(id):
    """Busca y devuelve un servicio específico según su ID único."""
    servicio = db.query(Servicio).filter(Servicio.id == id).first()
    if not servicio:
        return jsonify({"error": "Servicio no encontrado"}), 404
    return jsonify(servicio.to_dict()), 200

@servicios_bp.route('', methods=['POST'])
def create_servicio():
    """Registra un nuevo servicio en el catálogo validando sus enums y datos obligatorios."""
    data = request.get_json()
    try:
        nuevo_servicio = Servicio(
            tipo_servicio = TipoServicioEnum(data['tipo_servicio']),
            metrica_cobro = MetricaCobroEnum(data['metrica_cobro']),
            costo_referencia = data['costo_referencia']
        )
        db.add(nuevo_servicio)
        db.commit()
        return jsonify(nuevo_servicio.to_dict()), 201
    
    except (ValueError, KeyError) as ex:
        db.rollback()
        return jsonify({"error:", f"Datos de entrada inválidos: {str(ex)}"}), 400

@servicios_bp.route('/<int:id>', methods=['PUT'])
def update_servicio(id):
    """Actualiza la información de un servicio existente de forma parcial o total."""
    servicio = db.query(Servicio).filter(Servicio.id == id).first()
    if not servicio:
        return jsonify({"error": "Servicio no encontrado"}), 404

    data = request.get_json()
    try:
        if 'tipo_servicio' in data:
            servicio.tipo_servicio = TipoServicioEnum(data['tipo_servicio'])
        if 'metrica_cobro' in data:
            servicio.metrica_cobro = MetricaCobroEnum(data['metrica_cobro'])
        if 'costo_referencia' in data:
            servicio.costo_referencia = data['costo_referencia']

        db.commit()
        return jsonify(servicio.to_dict()), 200
    except ValueError as ex:
        db.rollback()
        return jsonify({"error", f"Valor ENUM inválido: {str(ex)} "}), 400

# 2. MICROSERVICIO DE CÁLCULO Y COTIZACIÓN

# Función auxiliar para calcular el recargo express
def aplicar_cargo_express(subtotal, es_express):
    """Aplica una tarifa fija express si el servicio o la petición lo requieren."""
    if es_express:
        tarifa_express = 50.0
        subtotal += tarifa_express
    return subtotal

# A) COTIZACIÓN: PAGO POR KILO
@servicios_bp.route('/cotizar/kilo', methods=['POST'])
def cotizar_por_kilo():
    """Calcula el subtotal basado en el peso (kilos) superando un límite base."""
    data = request.get_json()

    try:
        servicio_id = data.get('servicio_id')
        cantidad_kilos = float(data.get('cantidad_kilos', 0.0)) 
        forzar_express = data.get('express', False) # Opcional: forzar express desde el cliente

        if not servicio_id:
            return jsonify({"error": "El campo 'servicio_id' es obligatorio"}), 400

        # 1. Consultar el servicio directamente de la base de datos
        servicio_db = db.query(Servicio).filter(Servicio.id == servicio_id).first()
        if not servicio_db:
            return jsonify({"error": "El servicio especificado no existe en la base de datos"}), 404
        
        costo_referencia = float(servicio_db.costo_referencia)

        # Regla de negocio: Pago por Kilo
        peso_base = 2.0 # Límite base en kg
        peso_extra = 25.0 # Costo por kilo excedente

        if cantidad_kilos <= peso_base: 
            subtotal = costo_referencia
        else:
            subtotal = costo_referencia + ((cantidad_kilos - peso_base) * peso_extra)

        subtotal = aplicar_cargo_express(subtotal, forzar_express)

        return jsonify({
            "servicio_id": servicio_id,
            "metrica_cobro": "PAGO_POR_KILO",
            "cantidad_procesada": cantidad_kilos,
            "costo_referencia": costo_referencia,
            "es_express": forzar_express,
            "subtotal_calculado": round(subtotal, 2)
        }), 200

    except (ValueError, TypeError) as ex:
        return jsonify({"error": f"Datos de entrada inválidos: {str(ex)}"}), 400

# B) COTIZACIÓN: PAGO POR USO (T_inicio / T_final)
@servicios_bp.route('/cotizar/uso', methods=['POST'])
def cotizar_por_uso():
    """Calcula el subtotal en base a los minutos transcurridos (T_inicio y T_final)."""
    data = request.get_json()

    try:
        servicio_id = data.get('servicio_id')
        # Formato: YYYY-MM-DDTHH:MM:SS
        tiempo_inicio_str = data.get('t_inicio')
        tiempo_final_str = data.get('t_final') 
        forzar_express = data.get('express', False) # Opcional: forzar express desde el cliente

        if not servicio_id:
            return jsonify({"error": "El campo 'servicio_id' es obligatorio"}), 400

        # 1. Consultar el servicio directamente de la base de datos
        servicio_db = db.query(Servicio).filter(Servicio.id == servicio_id).first()
        if not servicio_db:
            return jsonify({"error": "El servicio especificado no existe en la base de datos"}), 404
        
        costo_referencia = float(servicio_db.costo_referencia)
        # Conversión de tiempos y cálculo de minutos
        tiempo_inicio = datetime.fromisoformat(tiempo_inicio_str)
        tiempo_final = datetime.fromisoformat(tiempo_final_str)
        duracion_minutos = (tiempo_final - tiempo_inicio).total_seconds() / 60.0

        if duracion_minutos < 0:
            return jsonify({"error": "El tiempo final no puede ser menor al de inicio"}), 400

        # Regla de ciclos (40 min por ciclo con techo matemático)
        duracion_ciclo = 40.0
        numero_ciclos = math.ceil(duracion_minutos / duracion_ciclo) if duracion_minutos > 0 else 1

        subtotal = numero_ciclos * costo_referencia
        subtotal = aplicar_cargo_express(subtotal, forzar_express)

        return jsonify({
            "servicio_id": servicio_id,
            "metrica_cobro": "PAGO_POR_USO",
            "minutos_totales": round(duracion_minutos, 2),
            "numero_ciclos": numero_ciclos,
            "costo_referencia": costo_referencia,
            "es_express": forzar_express,
            "subtotal_calculado": round(subtotal, 2)
        }), 200

    except (ValueError, TypeError) as ex:
        return jsonify({"error": f"Datos de entrada inválidos: {str(ex)}"}), 400

# C) COTIZACIÓN: PAGO POR PRENDA / SERVICIO ESPECIAL
@servicios_bp.route('/cotizar/prenda-especial', methods=['POST'])
def cotizar_por_prendas_especiales():
    """Calcula el subtotal multiplicando la cantidad de piezas/unidades por el costo de referencia."""
    data = request.get_json()
    
    try:
        servicio_id = data.get('servicio_id')
        cantidad_prendas = float(data.get('cantidad_prendas_especiales', 0.0))
        forzar_express = data.get('express', False) # Opcional: forzar express desde el cliente

        if not servicio_id:
            return jsonify({"error": "El campo 'servicio_id' es obligatorio"}), 400

        # 1. Consultar el servicio directamente de la base de datos
        servicio_db = db.query(Servicio).filter(Servicio.id == servicio_id).first()
        if not servicio_db:
            return jsonify({"error": "El servicio especificado no existe en la base de datos"}), 404

        costo_referencia = float(servicio_db.costo_referencia)

        # Regla de negocio: Pago por servicio especial (unidades o piezas)
        subtotal = costo_referencia * cantidad_prendas
        subtotal = aplicar_cargo_express(subtotal, forzar_express)

        return jsonify({
            "servicio_id": servicio_id,
            "metrica_cobro": "PAGO_POR_PRENDA_ESPECIAL",
            "cantidad_piezas": cantidad_prendas,
            "costo_referencia": costo_referencia,
            "es_express": forzar_express,
            "subtotal_calculado": round(subtotal, 2)
        }), 200

    except (ValueError, TypeError) as ex:
        return jsonify({"error": f"Datos de entrada inválidos: {str(ex)}"}), 400

@servicios_bp.route('/<int:id>', methods=['DELETE'])
def delete_servicio(id):
    """Elimina permanentemente un servicio del sistema a partir de su ID."""
    servicio = db.query(Servicio).filter(Servicio.id == id).first()
    if not servicio:
            return jsonify({"error": "Servicio no encontrado"}), 404

    db.delete(servicio)
    db.commit()
    return jsonify({"message": f"Servicio {id} eliminado correctamente"}), 200