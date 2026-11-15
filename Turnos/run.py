from app import create_app

#app de flask
app = create_app()

#punto de entrada
if __name__ == "__main__":
    app.run("127.0.0.1",5002,debug=True)