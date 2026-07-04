# app.py - Punto de entrada principal de AutoMenu AI
# Inicializa Flask, registra las rutas y corre el servidor

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
from db import auth_register, auth_login, auth_logout
from dotenv import load_dotenv
from error_handler import manejar_error
import os
from functools import wraps
# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

# ─── Decorador para proteger rutas ────────────────────────────
def login_required(func):
    """
    Permite acceder a la ruta solo si existe una sesión activa.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "user" not in session:
            flash("Debés iniciar sesión para continuar.", "warning")
            return redirect(url_for("login"))

        return func(*args, **kwargs)

    return wrapper

# ─── Rutas base ───────────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        resultado = auth_register(email, password)

        if resultado["ok"]:
            flash("Cuenta creada correctamente.", "success") # usamos flash para mostrar mensajes sin escribir java adicional 
            return redirect(url_for("login"))

        flash(resultado["error"], "danger")

    return render_template("auth/register.html")

@app.route("/login", methods=["GET", "POST"])

def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        resultado = auth_login(email, password)

        if resultado["ok"]:

            session["user"] = resultado["user"].id # por que flask necesita recordar quien inició sesión po r si el dashboard más adelante quiere preguntar quien inició sesión y se sepa quien fue

            flash("Bienvenido.", "success")

            return redirect(url_for("index"))

        flash(resultado["error"], "danger")

    return render_template("auth/login.html")
@app.route("/logout")
def logout():

    auth_logout()

    session.clear()

    flash("Sesión cerrada correctamente.", "info")

    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    """
    Dashboard temporal mientras se desarrolla la Fase 09.
    """
    return "Bienvenido al Dashboard de AutoMenu AI"

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