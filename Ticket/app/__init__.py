from flask import Flask
from dotenv import load_dotenv
import os
from app.database import engine

def create_app():
    load_dotenv()  # cargar variables de entorno del archivo .env
    
    app = Flask(__name__) # Crear instancia de la aplicación Flask
    
    # Configure the app using environment variables
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL') # Configurar la URL de la base de datos desde las variables de entorno
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Desactivar el seguimiento de modificaciones para mejorar el rendimiento
    app.config['JSON_SORT_KEYS'] = False  # Desactivar el ordenamiento de claves JSON para mantener el orden original

    # Registrar rutas
    from app.routes.routers import tickets_bp
    app.register_blueprint(tickets_bp)
    
    # Inicializar database engine y verificar la conexión
    try:
        with engine.connect() as connection:
            print("Conexión establecida correctamente")
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
    
    return app