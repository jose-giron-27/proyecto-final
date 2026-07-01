# app.py - Punto de entrada principal de AutoMenu AI
# Importa las rutas y corre el servidor Flask

from flask import Flask
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

# TODO: importar blueprints de rutas aquí (Fase 03 en adelante)
# from routes.auth import auth_bp
# from routes.dashboard import dashboard_bp
# app.register_blueprint(auth_bp)

@app.route("/")
def index():
    return "AutoMenu AI - En construcción 🍽️"

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False") == "True"
    app.run(debug=debug_mode)
