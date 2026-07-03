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
from db import (
    auth_register,
    auth_login,
    auth_logout,
    guardar_restaurante,
    actualizar_restaurante,
    obtener_restaurante
)
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
# ─── Autenticación ────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        resultado = auth_register(email, password)

        if resultado["ok"]:
            flash("Cuenta creada correctamente.", "success")
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

            session["user"] = resultado["user"].id

            flash("Bienvenido.", "success")

            return redirect(url_for("index"))

        flash(resultado["error"], "danger")

    return render_template("auth/login.html")


@app.route("/logout")
@login_required
def logout():

    auth_logout()

    session.clear()

    flash("Sesión cerrada correctamente.", "info")

    return redirect(url_for("login"))

# ─── Perfil del restaurante ───────────────────────────────────

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    if request.method == "POST":

        datos = {

            "user_id": session["user"],
            "nombre": request.form["nombre"],
            "descripcion": request.form["descripcion"],
            "direccion": request.form["direccion"],
            "telefono": request.form["telefono"],
            "whatsapp": request.form["whatsapp"],
            "instagram": request.form["instagram"],
            "tipo_comida": request.form["tipo_comida"],
            "horarios": request.form["horarios"],
            "logo": request.form["logo"],
            "imagen_portada": request.form["imagen_portada"]

        }

        restaurante = obtener_restaurante(session["user"])

        if restaurante["ok"] and restaurante["data"]:

            actualizar_restaurante(
                restaurante["data"][0]["id"],
                datos
            )

            flash("Perfil actualizado correctamente.", "success")

        else:

            guardar_restaurante(datos)

            flash("Perfil creado correctamente.", "success")

        return redirect(url_for("profile"))

    restaurante = obtener_restaurante(session["user"])

    datos_restaurante = {}

    if restaurante["ok"] and restaurante["data"]:
        datos_restaurante = restaurante["data"][0]

    return render_template(
        "dashboard/profile.html",
        restaurante=datos_restaurante
    )
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