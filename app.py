# app.py - Punto de entrada principal de AutoMenu AI
# Inicializa Flask, registra las rutas y corre el servidor

from flask import Flask, render_template
from dotenv import load_dotenv
from error_handler import manejar_error
import os

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

# ─── Rutas base ───────────────────────────────────────────────
@app.route("/")
def index():
    """Landing page de AutoMenu AI"""
    return render_template("index.html")

# ─── Manejo global de errores ─────────────────────────────────
@app.errorhandler(404)
def pagina_no_encontrada(error):
    return manejar_error(error, contexto="Página no encontrada")

@app.errorhandler(500)
def error_interno(error):
    return manejar_error(error, contexto="Error interno del servidor")

# ─── Punto de entrada ─────────────────────────────────────────
if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False") == "True"
    app.run(debug=debug_mode)