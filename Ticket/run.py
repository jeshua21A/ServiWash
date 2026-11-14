from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5006)  # Ejecutar la aplicación Flask en modo debug, accesible desde cualquier IP en el puerto 5000