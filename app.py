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

# ─── Rutas de IA generativa ───────────────────────────────────
# Importamos todas las funciones de IA que viven en ai_utils.py
from ai_utils import (
    generar_descripcion,       # Genera descripcion atractiva del platillo
    traducir_descripcion,      # Traduce la descripcion a otro idioma
    generar_caption,           # Genera caption para redes sociales
    sugerir_combo,             # Sugiere combos con los platillos existentes
    recomendar_etiquetas,      # Recomienda etiquetas segun los ingredientes
    mejorar_nombre,            # Sugiere nombres mas llamativos
    escanear_menu_desde_imagen # Lee una foto de menu fisico y extrae platillos
)

@app.route("/ai/description/<dish_id>", methods=["POST"])
@login_required
def ai_description(dish_id):
    """
    Genera una descripcion atractiva para un platillo usando IA.
    
    Flujo:
    1. Busca el platillo en Supabase por su ID
    2. Obtiene el tono elegido por el usuario (casual, elegante, juvenil, premium)
    3. Llama a generar_descripcion() en ai_utils.py (tiene while loop de reintentos)
    4. Guarda la generacion en la tabla ai_generations para historial
    5. Actualiza el campo ai_description del platillo en Supabase
    6. Redirige de vuelta a la lista de platillos
    """
    # Paso 1: Buscar el platillo en Supabase usando su ID
    resultado = get_dish_by_id(dish_id)
    
    # Si no se encontro el platillo, mostrar error en terminal y modal
    if not resultado["ok"]:
        return manejar_error(resultado["error"], contexto="Obtener platillo para descripcion IA")

    # Guardamos los datos del platillo en una variable
    platillo = resultado["data"]
    
    # Paso 2: Obtener el tono que eligio el usuario en el formulario
    # Si no eligio ninguno, usamos "casual" por defecto
    tono = request.form.get("tono", "casual")

    # Paso 3: Llamar a la funcion de IA con los datos del platillo
    # Esta funcion tiene un while loop que reintenta si la API falla
    resultado_ia = generar_descripcion(
        nombre=platillo["name"],
        ingredientes=platillo["ingredients"],
        precio=platillo["price"],
        tono=tono
    )

    # Si la IA fallo despues de todos los reintentos, mostrar error
    if not resultado_ia["ok"]:
        return manejar_error(resultado_ia["error"], contexto="Generar descripcion con IA")

    # Paso 4: Guardar la generacion en ai_generations para historial
    from db import db_insert
    db_insert("ai_generations", {
        "dish_id": dish_id,
        "type": "description",
        "prompt": f"nombre={platillo['name']}, tono={tono}",
        "response": resultado_ia["descripcion"]
    })

    # Paso 5: Actualizar el campo ai_description del platillo en Supabase
    update_dish(dish_id, {"ai_description": resultado_ia["descripcion"]})

    # Paso 6: Redirigir de vuelta a la lista de platillos
    return redirect(url_for("dish_list"))


@app.route("/ai/translate/<dish_id>", methods=["POST"])
@login_required
def ai_translate(dish_id):
    """
    Traduce la descripcion de un platillo al idioma indicado.
    
    Flujo:
    1. Busca el platillo en Supabase por su ID
    2. Obtiene el idioma elegido por el usuario (por defecto ingles)
    3. Llama a traducir_descripcion() en ai_utils.py
    4. Guarda la traduccion en ai_generations para historial
    5. Redirige de vuelta a la lista de platillos
    """
    # Paso 1: Buscar el platillo en Supabase
    resultado = get_dish_by_id(dish_id)
    if not resultado["ok"]:
        return manejar_error(resultado["error"], contexto="Obtener platillo para traduccion")

    platillo = resultado["data"]

    # Paso 2: Obtener el idioma elegido, por defecto ingles
    idioma = request.form.get("idioma", "ingles")

    # Usamos la descripcion generada por IA si existe, si no la descripcion normal
    descripcion = platillo.get("ai_description") or platillo.get("description", "")

    # Si el platillo no tiene descripcion, no hay nada que traducir
    if not descripcion:
        return manejar_error("El platillo no tiene descripcion para traducir", contexto="Traduccion IA")

    # Paso 3: Llamar a la funcion de traduccion con while loop de reintentos
    resultado_ia = traducir_descripcion(descripcion=descripcion, idioma=idioma)

    if not resultado_ia["ok"]:
        return manejar_error(resultado_ia["error"], contexto="Traducir descripcion con IA")

    # Paso 4: Guardar la traduccion en ai_generations para historial
    from db import db_insert
    db_insert("ai_generations", {
        "dish_id": dish_id,
        "type": "translation",
        "prompt": f"idioma={idioma}",
        "response": resultado_ia["traduccion"]
    })

    # Paso 5: Redirigir de vuelta a la lista de platillos
    return redirect(url_for("dish_list"))


@app.route("/ai/caption/<dish_id>", methods=["POST"])
@login_required
def ai_caption(dish_id):
    """
    Genera un caption listo para publicar en redes sociales.
    
    Flujo:
    1. Busca el platillo en Supabase por su ID
    2. Obtiene la red social elegida por el usuario (instagram, facebook, tiktok)
    3. Llama a generar_caption() en ai_utils.py
    4. Guarda el caption en ai_generations para historial
    5. Redirige de vuelta a la lista de platillos
    """
    # Paso 1: Buscar el platillo en Supabase
    resultado = get_dish_by_id(dish_id)
    if not resultado["ok"]:
        return manejar_error(resultado["error"], contexto="Obtener platillo para caption")

    platillo = resultado["data"]

    # Paso 2: Obtener la red social elegida, por defecto instagram
    red = request.form.get("red", "instagram")

    # Usamos la descripcion generada por IA si existe, si no la normal
    descripcion = platillo.get("ai_description") or platillo.get("description", "")

    # Paso 3: Llamar a la funcion de caption con while loop de reintentos
    resultado_ia = generar_caption(
        nombre=platillo["name"],
        descripcion=descripcion,
        precio=platillo["price"],
        red=red
    )

    if not resultado_ia["ok"]:
        return manejar_error(resultado_ia["error"], contexto="Generar caption con IA")

    # Paso 4: Guardar el caption en ai_generations para historial
    from db import db_insert
    db_insert("ai_generations", {
        "dish_id": dish_id,
        "type": "caption",
        "prompt": f"red={red}",
        "response": resultado_ia["caption"]
    })

    # Paso 5: Redirigir de vuelta a la lista de platillos
    return redirect(url_for("dish_list"))

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