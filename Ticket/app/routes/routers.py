from flask import Blueprint, request, jsonify
from app.services.ticket import generar_ticket
from app.services.servicios import cotizar_servicio
from app.database import Base

tickets_bp = Blueprint('tickets_bp', __name__, url_prefix='/api/v1/tickets')

@tickets_bp.route('', methods=['GET'])
def get_tickets():
    Base


@tickets_bp.route('', methods=['POST'])
def crear_ticket():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Se requiere un objeto JSON válido"
        }), 400

    try:
        resultado = generar_ticket(data)

        return jsonify(resultado), 201

    except ValueError as ex:
        return jsonify({
            "error": str(ex)
        }), 400

    except Exception as ex:
        print(f"Error al generar ticket: {str(ex)}")

        return jsonify({
            "error": "Ocurrió un error al generar el ticket"
        }), 500
