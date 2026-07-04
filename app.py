# app.py - Punto de entrada principal de AutoMenu AI
# Inicializa Flask, registra las rutas y corre el servidor

from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
from error_handler import manejar_error
import os

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

from db import get_dishes, get_dish_by_id, insert_dish, update_dish, delete_dish, toggle_dish_availability, db_get
from menu_logic import agregar_platillo, editar_platillo, eliminar_platillo, filtrar_por_categoria, promedio_precios, platillo_mas_caro, platillo_mas_barato, sugerir_platillo_del_dia
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function
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
    return render_template("index.html")

@app.route("/dishes")
@login_required
def dish_list():
    user_id = session.get("user")
    restaurante = db_get("restaurants", filtros={"user_id": user_id})
    if not restaurante["ok"] or not restaurante["data"]:
        return redirect(url_for("index"))
    restaurant_id = restaurante["data"][0]["id"]
    resultado = get_dishes(restaurant_id)
    platillos = resultado["data"] if resultado["ok"] else []
    categoria = request.args.get("categoria", "")
    if categoria:
        platillos = filtrar_por_categoria(platillos, categoria)
    promedio = promedio_precios(platillos)
    mas_caro = platillo_mas_caro(platillos)
    mas_barato = platillo_mas_barato(platillos)
    platillo_dia = sugerir_platillo_del_dia(platillos)
    return render_template("dishes/list.html", platillos=platillos, categoria=categoria, promedio=promedio, mas_caro=mas_caro, mas_barato=mas_barato, platillo_dia=platillo_dia)

@app.route("/dishes/create", methods=["GET", "POST"])
@login_required
def dish_create():
    user_id = session.get("user")
    restaurante = db_get("restaurants", filtros={"user_id": user_id})
    if not restaurante["ok"] or not restaurante["data"]:
        return redirect(url_for("index"))
    restaurant_id = restaurante["data"][0]["id"]
    if request.method == "POST":
        nombre = request.form.get("nombre", "")
        precio = float(request.form.get("precio", 0))
        categoria = request.form.get("categoria", "")
        ingredientes = request.form.get("ingredientes", "")
        imagen_url = request.form.get("imagen_url", "")
        etiquetas = request.form.getlist("etiquetas")
        validacion = agregar_platillo(nombre, precio, categoria, ingredientes, imagen_url, etiquetas)
        if not validacion["ok"]:
            return manejar_error(validacion["error"], contexto="Crear platillo")
        datos = validacion["platillo"]
        datos["restaurant_id"] = restaurant_id
        resultado = insert_dish(datos)
        if not resultado["ok"]:
            return manejar_error(resultado["error"], contexto="Guardar platillo")
        return redirect(url_for("dish_list"))
    return render_template("dishes/create.html")


@app.route("/dishes/edit/<dish_id>", methods=["GET", "POST"])
@login_required
def dish_edit(dish_id):
    """Edita un platillo existente usando la logica de menu_logic."""
    resultado = get_dish_by_id(dish_id)
    if not resultado["ok"]:
        return manejar_error(resultado["error"], contexto="Obtener platillo")

    platillo = resultado["data"]

    if request.method == "POST":
        campos = {
            "nombre": request.form.get("nombre", ""),
            "precio": float(request.form.get("precio", 0)),
            "categoria": request.form.get("categoria", ""),
            "ingredientes": request.form.get("ingredientes", ""),
            "imagen_url": request.form.get("imagen_url", ""),
            "etiquetas": request.form.getlist("etiquetas"),
        }
        platillo_actualizado = editar_platillo(platillo, campos)
        resultado_update = update_dish(dish_id, platillo_actualizado["platillo"])
        if not resultado_update["ok"]:
            return manejar_error(resultado_update["error"], contexto="Editar platillo")
        return redirect(url_for("dish_list"))

    return render_template("dishes/edit.html", platillo=platillo)


@app.route("/dishes/delete/<dish_id>", methods=["POST"])
@login_required
def dish_delete(dish_id):
    """Elimina un platillo de la base de datos."""
    resultado = delete_dish(dish_id)
    if not resultado["ok"]:
        return manejar_error(resultado["error"], contexto="Eliminar platillo")
    return redirect(url_for("dish_list"))


@app.route("/dishes/toggle/<dish_id>", methods=["POST"])
@login_required
def dish_toggle(dish_id):
    """
    Activa o desactiva la disponibilidad de un platillo.
    Recibe el estado actual y lo invierte (True -> False o False -> True).
    """
    # Obtener el estado actual que mandó el formulario
    is_available = request.form.get("is_available") == "true"
    
    # Invertir el estado actual
    nuevo_estado = not is_available
    
    # Actualizar en Supabase usando el helper de db.py
    resultado = toggle_dish_availability(dish_id, nuevo_estado)
    
    # Si algo salió mal, imprimir en terminal y mostrar error
    if not resultado["ok"]:
        return manejar_error(resultado["error"], contexto="Toggle disponibilidad")
    
    # Redirigir de vuelta a la lista de platillos
    return redirect(url_for("dish_list"))

@app.errorhandler(404)
def pagina_no_encontrada(error):
    return manejar_error(error, contexto="Pagina no encontrada")

@app.errorhandler(500)
def error_interno(error):
    return manejar_error(error, contexto="Error interno del servidor")

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False") == "True"
    app.run(debug=debug_mode)
