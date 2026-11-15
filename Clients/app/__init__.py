import logging
import os
from flask import Flask, jsonify
from flask_cors import CORS
from .auth import get_token
from .router import bp

#obtener el modo
DEBUG = os.environ.get("DEBUG")

#configuracion de logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%d/%m/%Y - %H:%M:%S"
)

logger = logging.getLogger(__name__)

#factory de app de flask
def create_app()->Flask:
    #app principal de flask
    app = Flask(__name__)

    #añadir cors
    CORS(app)

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

    @app.before_request
    def middleware():
        #validar modo
        if DEBUG:
            return
        
        #obtener token
        tk = get_token()
        
        #validar header de token
        if not tk:
            return jsonify({"msg":"not allowed"}), 401
        
    #registrar blueprints
    app.register_blueprint(bp)
    
    #retornar la app
    return app