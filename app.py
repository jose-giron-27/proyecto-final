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

# ─── Rutas de platillos ───────────────────────────────────────
from db import get_dishes, get_dish_by_id, insert_dish, update_dish, delete_dish, toggle_dish_availability
from menu_logic import agregar_platillo, editar_platillo, eliminar_platillo, filtrar_por_categoria, promedio_precios, platillo_mas_caro, platillo_mas_barato, sugerir_platillo_del_dia

@app.route("/dishes")
@login_required
def dish_list():
    """Lista todos los platillos del restaurante con estadísticas."""
    user_id = session.get("user")
    
    # Obtener restaurante del usuario
    from db import db_get
    restaurante = db_get("restaurants", filtros={"user_id": user_id})
    
    if not restaurante["ok"] or not restaurante["data"]:
        return redirect(url_for("index"))
    
    restaurant_id = restaurante["data"][0]["id"]
    resultado = get_dishes(restaurant_id)
    
    platillos = resultado["data"] if resultado["ok"] else []
    categoria = request.args.get("categoria", "")
    
    # Filtrar por categoría si se especificó
    if categoria:
        platillos = filtrar_por_categoria(platillos, categoria)
    
    # Calcular estadísticas con for loop
    promedio = promedio_precios(platillos)
    mas_caro = platillo_mas_caro(platillos)
    mas_barato = platillo_mas_barato(platillos)
    platillo_dia = sugerir_platillo_del_dia(platillos)

    return render_template("dishes/list.html",
        platillos=platillos,
        categoria=categoria,
        promedio=promedio,
        mas_caro=mas_caro,
        mas_barato=mas_barato,
        platillo_dia=platillo_dia
    )

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