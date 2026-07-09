# app.py - Punto de entrada principal de AutoMenu AI
# Inicializa Flask, registra las rutas y corre el servidor
import io
import os
import re
from io import BytesIO
from functools import wraps

import qrcode

from dotenv import load_dotenv

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file
)

from error_handler import manejar_error

from db import (
    auth_register,
    auth_login,
    auth_logout,
    guardar_restaurante,
    actualizar_restaurante,
    obtener_restaurante,
    get_restaurant_by_slug,
    get_dishes
)

# Fase 12 - Stripe (demo/simulación de pagos, modo test/sandbox)
from stripe_utils import crear_checkout_session, verificar_pago

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

from db import get_dishes, get_dish_by_id, insert_dish, update_dish, delete_dish, toggle_dish_availability, db_get, subir_imagen_platillo, subir_imagen_restaurante
from menu_logic import agregar_platillo, editar_platillo, eliminar_platillo, filtrar_por_categoria, promedio_precios, platillo_mas_caro, platillo_mas_barato, sugerir_platillo_del_dia
from functools import wraps

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


# ─── Fase 12: Verificación de Plan (Free vs Pro) ──────────────────
def es_plan_pro(restaurant_id):
    """
    Verifica si un restaurante tiene el Plan Pro activo.
    Se usa para bloquear funciones de IA y el límite de platillos
    en el Plan Gratis.
    """
    resultado = db_get("restaurants", filtros={"id": restaurant_id})
    if resultado["ok"] and resultado["data"]:
        return resultado["data"][0].get("plan") == "pro"
    return False


LIMITE_PLATILLOS_PLAN_GRATIS = 10

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

            return redirect(url_for("dashboard"))

        flash(resultado["error"], "danger")

    return render_template("auth/login.html")
@app.route("/logout")
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

        # Logo: si subieron un archivo, tiene prioridad sobre la URL
        archivo_logo = request.files.get("logo_archivo")
        if archivo_logo and archivo_logo.filename:
            resultado_logo = subir_imagen_restaurante(archivo_logo)
            if not resultado_logo["ok"]:
                return manejar_error(resultado_logo["error"], contexto="Subir logo del restaurante")
            logo_url = resultado_logo["url"]
        else:
            logo_url = request.form.get("logo", "")

        # Imagen de portada: misma lógica
        archivo_portada = request.files.get("imagen_portada_archivo")
        if archivo_portada and archivo_portada.filename:
            resultado_portada = subir_imagen_restaurante(archivo_portada)
            if not resultado_portada["ok"]:
                return manejar_error(resultado_portada["error"], contexto="Subir imagen de portada")
            portada_url = resultado_portada["url"]
        else:
            portada_url = request.form.get("imagen_portada", "")

        datos = {

            "name": request.form["nombre"],
            "description": request.form["descripcion"],
            "address": request.form["direccion"],
         "phone": request.form["telefono"],
         "whatsapp": request.form["whatsapp"],
         "instagram": request.form["instagram"],
         "opening_hours": request.form["horarios"],
         "logo_url": logo_url,
        "cover_image_url": portada_url,
        "user_id": session["user"]
}

        # genera el slug automáticamente
        slug = datos["name"].lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")
        datos["slug"] = slug

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

@app.route("/dashboard")
@login_required
def dashboard():
    """
    Vista principal del restaurante.
    """

    try:

        restaurante = obtener_restaurante(session["user"])

        if not restaurante["ok"] or not restaurante["data"]:
            flash("Completá el perfil de tu restaurante para empezar.", "info")
            return redirect(url_for("profile"))

        restaurante = restaurante["data"][0]

        resultado = get_dishes(restaurante["id"])

        total_platillos = 0
        menu_activo = False

        if resultado["ok"]:
            total_platillos = len(resultado["data"])

            for platillo in resultado["data"]:
                if platillo["is_available"]:
                    menu_activo = True
                    break

        menu_publico = url_for(
            "public_menu",
            slug=restaurante["slug"],
            _external=True
        )

        return render_template(
            "dashboard/index.html",
            restaurante=restaurante,
            total_platillos=total_platillos,
            menu_activo=menu_activo,
            menu_publico=menu_publico
        )

    except Exception as e:

        print(f"[Dashboard] {e}")

        return manejar_error(
            e,
            contexto="Dashboard"
        )
@app.route("/dashboard/qr")
@login_required
def qr_dashboard():
    """
    Muestra el código QR del restaurante.
    """

    restaurante = obtener_restaurante(session["user"])

    if not restaurante["ok"] or not restaurante["data"]:
        return manejar_error(
            "Restaurante no encontrado",
            contexto="Código QR"
        )

    restaurante = restaurante["data"][0]

    return render_template(
        "dashboard/qr.html",
        restaurante=restaurante
    )

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/planes")
def planes():
    """
    Muestra solo la sección de precios/planes, tanto para visitantes
    sin cuenta como para usuarios logueados (a quienes además se les
    marca cuál es su plan actual).
    """
    plan_actual = None

    if session.get("user"):
        restaurante = obtener_restaurante(session["user"])
        if restaurante["ok"] and restaurante["data"]:
            plan_actual = restaurante["data"][0].get("plan", "free")

    return render_template("planes.html", plan_actual=plan_actual)

# Fase 12+: textos fijos de la interfaz del menú público, traducidos.
# Solo son 3 etiquetas + 7 categorías conocidas, así que usamos un
# diccionario fijo en vez de llamar a la IA para esto (más rápido y confiable).
TEXTOS_UI_MENU_PUBLICO = {
    "es": {"horario": "Horario", "direccion": "Dirección", "etiquetas": "Etiquetas"},
    "en": {"horario": "Hours", "direccion": "Address", "etiquetas": "Tags"},
    "fr": {"horario": "Horaires", "direccion": "Adresse", "etiquetas": "Étiquettes"},
    "pt": {"horario": "Horário", "direccion": "Endereço", "etiquetas": "Etiquetas"},
    "de": {"horario": "Öffnungszeiten", "direccion": "Adresse", "etiquetas": "Tags"},
    "it": {"horario": "Orario", "direccion": "Indirizzo", "etiquetas": "Etichette"},
}

CATEGORIAS_TRADUCIDAS_MENU_PUBLICO = {
    "es": {"entradas": "Entradas", "platos fuertes": "Platos fuertes", "hamburguesas": "Hamburguesas", "tacos": "Tacos", "bebidas": "Bebidas", "postres": "Postres", "combos": "Combos"},
    "en": {"entradas": "Appetizers", "platos fuertes": "Main courses", "hamburguesas": "Burgers", "tacos": "Tacos", "bebidas": "Drinks", "postres": "Desserts", "combos": "Combos"},
    "fr": {"entradas": "Entrées", "platos fuertes": "Plats principaux", "hamburguesas": "Burgers", "tacos": "Tacos", "bebidas": "Boissons", "postres": "Desserts", "combos": "Formules"},
    "pt": {"entradas": "Entradas", "platos fuertes": "Pratos principais", "hamburguesas": "Hambúrgueres", "tacos": "Tacos", "bebidas": "Bebidas", "postres": "Sobremesas", "combos": "Combos"},
    "de": {"entradas": "Vorspeisen", "platos fuertes": "Hauptgerichte", "hamburguesas": "Burger", "tacos": "Tacos", "bebidas": "Getränke", "postres": "Desserts", "combos": "Kombis"},
    "it": {"entradas": "Antipasti", "platos fuertes": "Piatti principali", "hamburguesas": "Hamburger", "tacos": "Tacos", "bebidas": "Bevande", "postres": "Dolci", "combos": "Combo"},
}


@app.route("/menu/<slug>")
def public_menu(slug): 
    """
    Muestra el menú público de un restaurante.
    No requiere iniciar sesión.
    """

    restaurante = get_restaurant_by_slug(slug) #busca el restaurante

    if not restaurante["ok"] or not restaurante["data"]:
        return manejar_error(
            "Restaurante no encontrado",
            contexto="Menú público"
        ) #por si no existe el restarurante se cumple este if 

    restaurante = restaurante["data"][0]

    resultado = get_dishes(restaurante["id"]) # se cumple si el restaaurante si existe 

    platillos = []

    if resultado["ok"]:
        for platillo in resultado["data"]:
            if platillo["is_available"]: #solo muestran los platillos disponibles
                platillos.append(platillo)

    # Fase 12+: deteccion automatica de idioma para turistas.
    # Leemos el header "Accept-Language" que el navegador manda solo,
    # sin que el visitante tenga que hacer nada ni elegir un idioma.
    idiomas_soportados = {
        "en": "ingles",
        "fr": "frances",
        "pt": "portugues",
        "de": "aleman",
        "it": "italiano",
    }
    codigo_idioma = request.accept_languages.best_match(list(idiomas_soportados.keys()) + ["es"])

    # Si el navegador del visitante no es español y detectamos un idioma
    # soportado, traducimos las descripciones al vuelo (no se guarda en
    # la base de datos, es solo para esta visita).
    if codigo_idioma and codigo_idioma != "es":
        idioma_nombre = idiomas_soportados[codigo_idioma]
        for platillo in platillos:
            if platillo.get("description"):
                resultado_traduccion = traducir_descripcion(platillo["description"], idioma=idioma_nombre)
                if resultado_traduccion["ok"]:
                    platillo["description"] = resultado_traduccion["traduccion"]

    # Textos fijos de la interfaz (Horario, Dirección, Etiquetas) y las
    # categorías, traducidos con el diccionario fijo (sin llamar a la IA)
    idioma_final = codigo_idioma if codigo_idioma in TEXTOS_UI_MENU_PUBLICO else "es"
    textos = TEXTOS_UI_MENU_PUBLICO[idioma_final]
    categorias_traducidas = CATEGORIAS_TRADUCIDAS_MENU_PUBLICO[idioma_final]
    for platillo in platillos:
        categoria_original = platillo.get("category", "")
        platillo["category"] = categorias_traducidas.get(categoria_original, categoria_original)

    return render_template(
         "menu/public.html",
         restaurante=restaurante,
         platillos=platillos,
         textos=textos
        ) # envía toda la info a html

@app.route("/qr/<slug>") # genera un qr que automáticamente redirige al menú público del restaurante
def generate_qr(slug):
    """
    Generates a QR code that points to the restaurant's public menu.
    """

    url = request.host_url.rstrip("/") + url_for("public_menu", slug=slug)

    qr = qrcode.make(url)

    buffer = BytesIO()

    qr.save(buffer, format="PNG")

    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="image/png"
    )
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
    5. Guarda el resultado en el campo description del platillo en Supabase
    6. Redirige de vuelta a la lista de platillos
    """
    # Paso 1: Buscar el platillo en Supabase usando su ID
    resultado = get_dish_by_id(dish_id)
    
    # Si no se encontro el platillo, mostrar error en terminal y modal
    if not resultado["ok"]:
        return manejar_error(resultado["error"], contexto="Obtener platillo para descripcion IA")

    # Guardamos los datos del platillo en una variable
    platillo = resultado["data"]

    # Fase 12: las funciones de IA son exclusivas del Plan Pro
    if not es_plan_pro(platillo["restaurant_id"]):
        flash("Esta función de IA es exclusiva del Plan Pro. Actualizá tu plan para usarla.", "warning")
        return redirect(url_for("dish_list"))

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

    # Paso 5: Guardar la descripcion generada directo en el campo "description",
    # que es el mismo campo editable que ve el usuario, para que pueda seguir
    # modificandolo antes de guardar (en vez de un campo aparte de solo lectura)
    update_dish(dish_id, {"description": resultado_ia["descripcion"]})

    # Paso 6: Redirigir de vuelta a donde vino el click (lista o pantalla de editar)
    if request.form.get("next") == "edit":
        return redirect(url_for("dish_edit", dish_id=dish_id))
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

    # Fase 12: las funciones de IA son exclusivas del Plan Pro
    if not es_plan_pro(platillo["restaurant_id"]):
        flash("Esta función de IA es exclusiva del Plan Pro. Actualizá tu plan para usarla.", "warning")
        return redirect(url_for("dish_list"))

    # Paso 2: Obtener la red social elegida, por defecto instagram
    red = request.form.get("red", "instagram")

    # Usamos la descripcion generada por IA si existe, si no la normal
    descripcion = platillo.get("description", "")

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

    # Paso 5: Mostrar el caption generado como mensaje flash (se copia
    # automáticamente al portapapeles también, ver el script en base.html)
    flash(resultado_ia["caption"], "caption")

    # Paso 6: Redirigir de vuelta a la lista de platillos
    return redirect(url_for("dish_list"))


@app.route("/ai/combo", methods=["POST"])
@login_required
def ai_combo():
    """
    Sugiere un combo usando los platillos existentes del restaurante.
    
    Flujo:
    1. Obtiene el restaurante del usuario desde Supabase
    2. Obtiene todos los platillos disponibles del restaurante
    3. Llama a sugerir_combo() en ai_utils.py pasando la lista de platillos
    4. Guarda la sugerencia en ai_generations para historial
    5. Redirige de vuelta a la lista de platillos
    """
    # Paso 1: Obtener el restaurante del usuario actual
    user_id = session.get("user")
    restaurante = obtener_restaurante(user_id)
    
    if not restaurante["ok"] or not restaurante["data"]:
        return manejar_error("Restaurante no encontrado", contexto="Sugerir combo")

    restaurant_id = restaurante["data"][0]["id"]

    # Fase 12: las funciones de IA son exclusivas del Plan Pro
    if not es_plan_pro(restaurant_id):
        flash("Esta función de IA es exclusiva del Plan Pro. Actualizá tu plan para usarla.", "warning")
        return redirect(url_for("dish_list"))

    # Paso 2: Obtener todos los platillos disponibles del restaurante
    # Usamos un for loop para filtrar solo los disponibles
    resultado = get_dishes(restaurant_id)
    todos_los_platillos = resultado["data"] if resultado["ok"] else []
    
    platillos_disponibles = []
    for platillo in todos_los_platillos:
        if platillo["is_available"]:
            platillos_disponibles.append(platillo)

    # Si no hay platillos disponibles, no podemos sugerir combo
    if not platillos_disponibles:
        return manejar_error("No hay platillos disponibles para sugerir un combo", contexto="Sugerir combo")

    # Paso 3: Llamar a la funcion de combos con while loop de reintentos
    resultado_ia = sugerir_combo(lista_platillos=platillos_disponibles)

    if not resultado_ia["ok"]:
        return manejar_error(resultado_ia["error"], contexto="Sugerir combo con IA")

    # Paso 4: Guardar la sugerencia en ai_generations
    # Como el combo no pertenece a un platillo especifico, usamos el primer platillo como referencia
    from db import db_insert
    db_insert("ai_generations", {
        "dish_id": platillos_disponibles[0]["id"],
        "type": "combo",
        "prompt": f"platillos={[p['name'] for p in platillos_disponibles]}",
        "response": resultado_ia["combo"]
    })

    # Paso 5: Mostrar el combo sugerido como mensaje flash (visible en pantalla)
    flash(resultado_ia["combo"], "caption")

    # Paso 6: Redirigir de vuelta a la lista de platillos
    return redirect(url_for("dish_list"))


@app.route("/ai/tags/<dish_id>", methods=["POST"])
@login_required
def ai_tags(dish_id):
    """
    Recomienda etiquetas para un platillo analizando sus ingredientes con IA.
    Etiquetas posibles: vegetariano, vegano, picante, sin gluten, popular, nuevo, recomendado.
    
    Flujo:
    1. Busca el platillo en Supabase por su ID
    2. Extrae los ingredientes del platillo
    3. Llama a recomendar_etiquetas() en ai_utils.py
    4. Guarda las etiquetas recomendadas en ai_generations para historial
    5. Actualiza las etiquetas del platillo en Supabase
    6. Redirige de vuelta a la lista de platillos
    """
    # Paso 1: Buscar el platillo en Supabase
    resultado = get_dish_by_id(dish_id)
    if not resultado["ok"]:
        return manejar_error(resultado["error"], contexto="Obtener platillo para etiquetas")

    platillo = resultado["data"]

    # Fase 12: las funciones de IA son exclusivas del Plan Pro
    if not es_plan_pro(platillo["restaurant_id"]):
        flash("Esta función de IA es exclusiva del Plan Pro. Actualizá tu plan para usarla.", "warning")
        return redirect(url_for("dish_list"))

    # Paso 2: Extraer los ingredientes del platillo
    ingredientes = platillo.get("ingredients", "")
    
    # Si no tiene ingredientes, no podemos recomendar etiquetas
    if not ingredientes:
        return manejar_error("El platillo no tiene ingredientes registrados", contexto="Recomendar etiquetas")

    # Paso 3: Llamar a la funcion de etiquetas con while loop de reintentos
    resultado_ia = recomendar_etiquetas(ingredientes=ingredientes)

    if not resultado_ia["ok"]:
        return manejar_error(resultado_ia["error"], contexto="Recomendar etiquetas con IA")

    # Paso 4: Guardar las etiquetas en ai_generations para historial
    from db import db_insert
    db_insert("ai_generations", {
        "dish_id": dish_id,
        "type": "tags",
        "prompt": f"ingredientes={ingredientes}",
        "response": str(resultado_ia["etiquetas"])
    })

    # Paso 5: Actualizar las etiquetas del platillo en Supabase
    update_dish(dish_id, {"tags": resultado_ia["etiquetas"]})

    # Paso 6: Mostrar confirmación de las etiquetas aplicadas
    flash("Etiquetas aplicadas: " + ", ".join(resultado_ia["etiquetas"]), "success")

    # Paso 7: Redirigir de vuelta a la lista de platillos
    return redirect(url_for("dish_list"))


@app.route("/ai/name/<dish_id>", methods=["POST"])
@login_required
def ai_name(dish_id):
    """
    Sugiere nombres mas llamativos para un platillo usando IA.
    La IA devuelve 4 opciones de nombres basandose en el nombre original.
    
    Flujo:
    1. Busca el platillo en Supabase por su ID
    2. Obtiene el nombre original del platillo
    3. Llama a mejorar_nombre() en ai_utils.py
    4. Guarda las sugerencias en ai_generations para historial
    5. Redirige de vuelta a la lista de platillos
    """
    # Paso 1: Buscar el platillo en Supabase
    resultado = get_dish_by_id(dish_id)
    if not resultado["ok"]:
        return manejar_error(resultado["error"], contexto="Obtener platillo para mejorar nombre")

    platillo = resultado["data"]

    # Fase 12: las funciones de IA son exclusivas del Plan Pro
    if not es_plan_pro(platillo["restaurant_id"]):
        flash("Esta función de IA es exclusiva del Plan Pro. Actualizá tu plan para usarla.", "warning")
        return redirect(url_for("dish_list"))

    # Paso 2: Obtener el nombre original del platillo
    nombre_original = platillo.get("name", "")

    if not nombre_original:
        return manejar_error("El platillo no tiene nombre registrado", contexto="Mejorar nombre")

    # Paso 3: Llamar a la funcion de mejora de nombre con while loop de reintentos
    resultado_ia = mejorar_nombre(nombre_original=nombre_original)

    if not resultado_ia["ok"]:
        return manejar_error(resultado_ia["error"], contexto="Mejorar nombre con IA")

    # Paso 4: Guardar las sugerencias en ai_generations para historial
    # Unimos la lista de nombres en un string para guardarlo
    from db import db_insert
    db_insert("ai_generations", {
        "dish_id": dish_id,
        "type": "name_suggestion",
        "prompt": f"nombre_original={nombre_original}",
        "response": ", ".join(resultado_ia["nombres"])
    })

    # Paso 5: Mostrar los nombres sugeridos como mensaje flash (visible en pantalla)
    flash("Nombres sugeridos: " + ", ".join(resultado_ia["nombres"]), "caption")

    # Paso 6: Redirigir de vuelta a la lista de platillos
    return redirect(url_for("dish_list"))


@app.route("/ai/scan", methods=["GET", "POST"])
@login_required
def ai_scan():
    """
    Escanea una foto de un menu fisico y extrae los platillos automaticamente.
    
    Flujo GET: Muestra el formulario para subir la imagen
    Flujo POST:
    1. Recibe la imagen subida por el usuario
    2. Lee los bytes de la imagen
    3. Llama a escanear_menu_desde_imagen() en ai_utils.py que usa vision artificial
    4. Devuelve los platillos detectados a la pantalla de revision
    5. El usuario revisa y confirma cuales guardar en scan_review.html
    """
    # Fase 12: el escaneo de menú con IA es exclusivo del Plan Pro
    user_id = session.get("user")
    restaurante = obtener_restaurante(user_id)
    if not restaurante["ok"] or not restaurante["data"]:
        return redirect(url_for("profile"))
    restaurant_id = restaurante["data"][0]["id"]
    if not es_plan_pro(restaurant_id):
        flash("El escaneo de menús con IA es exclusivo del Plan Pro. Actualizá tu plan para usarlo.", "warning")
        return redirect(url_for("dish_list"))

    # Si es GET, simplemente mostrar el formulario de escaneo
    if request.method == "GET":
        return render_template("dishes/scan.html")

    # Paso 1: Verificar que se subio una imagen
    if "imagen" not in request.files:
        return manejar_error("No se subio ninguna imagen", contexto="Escanear menu")

    imagen = request.files["imagen"]

    # Verificar que el archivo no esta vacio
    if imagen.filename == "":
        return manejar_error("El archivo de imagen esta vacio", contexto="Escanear menu")

    # Paso 2: Leer los bytes de la imagen para enviarlos a la API de vision
    imagen_bytes = imagen.read()

    # Paso 3: Llamar a la funcion de vision artificial con while loop de reintentos
    # La IA analiza la imagen y devuelve un JSON con los platillos detectados
    resultado_ia = escanear_menu_desde_imagen(imagen_bytes=imagen_bytes)

    if not resultado_ia["ok"]:
        return manejar_error(resultado_ia["error"], contexto="Escanear imagen del menu")

    # Paso 4: Obtener los platillos que detecto la IA
    platillos_detectados = resultado_ia["platillos"]

    # Paso 5: Mostrar la pantalla de revision para que el dueno confirme
    # El dueno puede editar o quitar platillos antes de guardarlos
    return render_template("dishes/scan_review.html",
        platillos=platillos_detectados
    )


@app.route("/ai/scan/confirm", methods=["POST"])
@login_required
def ai_scan_confirm():
    """
    Guarda los platillos confirmados por el dueno despues del escaneo de imagen.
    
    Flujo:
    1. Obtiene el restaurante del usuario actual
    2. Recibe la lista de platillos que el dueno aprobo en scan_review.html
    3. Usa un for loop para insertar cada platillo aprobado en Supabase
    4. Redirige a la lista de platillos cuando termina
    """
    # Paso 1: Obtener el restaurante del usuario
    user_id = session.get("user")
    restaurante = obtener_restaurante(user_id)

    if not restaurante["ok"] or not restaurante["data"]:
        return redirect(url_for("profile"))

    restaurant_id = restaurante["data"][0]["id"]

    # Paso 2: Obtener los nombres y precios que el dueno confirmo en el formulario
    nombres = request.form.getlist("nombre")
    precios = request.form.getlist("precio")
    categorias = request.form.getlist("categoria")

    # Verificar que hay platillos para guardar
    if not nombres:
        return manejar_error("No hay platillos para guardar", contexto="Confirmar escaneo")

    # Paso 3: Usar for loop para insertar cada platillo aprobado en Supabase
    platillos_guardados = 0
    for i in range(len(nombres)):
        # Validar cada platillo con menu_logic antes de guardarlo
        try:
            precio = float(precios[i]) if i < len(precios) else 0.0
        except ValueError:
            precio = 0.0

        categoria = categorias[i] if i < len(categorias) else "general"

        # Usar agregar_platillo() de menu_logic para validar
        validacion = agregar_platillo(
            nombre=nombres[i],
            precio=precio,
            categoria=categoria,
            ingredientes=""
        )

        # Solo guardar si paso la validacion
        if validacion["ok"]:
            datos = validacion["platillo"]
            datos["restaurant_id"] = restaurant_id
            insert_dish(datos)
            platillos_guardados += 1

    # Paso 4: Redirigir a la lista de platillos
    print(f"[ai_scan_confirm] {platillos_guardados} platillos guardados exitosamente")
@app.route("/dishes")
@login_required
def dish_list():
    user_id = session.get("user")
    restaurante = obtener_restaurante(user_id)
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

    # Fase 12: pasamos info del plan para mostrar el aviso de límite/IA en la UI
    plan_pro = es_plan_pro(restaurant_id)

    return render_template(
        "dishes/list.html",
        platillos=platillos, categoria=categoria, promedio=promedio,
        mas_caro=mas_caro, mas_barato=mas_barato, platillo_dia=platillo_dia,
        plan_pro=plan_pro,
        limite_platillos=LIMITE_PLATILLOS_PLAN_GRATIS,
        cantidad_platillos=len(platillos)
    )

@app.route("/dishes/create", methods=["GET", "POST"])
@login_required
def dish_create():
    user_id = session.get("user")
    restaurante = obtener_restaurante(user_id)
    if not restaurante["ok"] or not restaurante["data"]:
        return redirect(url_for("profile"))
    restaurant_id = restaurante["data"][0]["id"]

    # Fase 12: el Plan Gratis solo permite hasta 10 platillos
    if not es_plan_pro(restaurant_id):
        platillos_existentes = get_dishes(restaurant_id)
        cantidad_actual = len(platillos_existentes["data"]) if platillos_existentes["ok"] else 0
        if cantidad_actual >= LIMITE_PLATILLOS_PLAN_GRATIS:
            flash(
                f"Alcanzaste el límite de {LIMITE_PLATILLOS_PLAN_GRATIS} platillos del Plan Gratis. "
                "Actualizá a Pro para agregar platillos ilimitados.",
                "warning"
            )
            return redirect(url_for("dish_list"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "")
        try:
            precio = float(request.form.get("precio", 0))
        except ValueError:
            return manejar_error("El precio debe ser un numero valido", contexto="Crear platillo")
        categoria = request.form.get("categoria", "")
        ingredientes = request.form.get("ingredientes", "")
        etiquetas = request.form.getlist("etiquetas")
        descripcion = request.form.get("descripcion", "")

        # Imagen: si el usuario subió un archivo, tiene prioridad sobre la URL
        archivo_imagen = request.files.get("imagen_archivo")
        if archivo_imagen and archivo_imagen.filename:
            resultado_subida = subir_imagen_platillo(archivo_imagen)
            if not resultado_subida["ok"]:
                return manejar_error(resultado_subida["error"], contexto="Subir imagen del platillo")
            imagen_url = resultado_subida["url"]
        else:
            imagen_url = request.form.get("imagen_url", "")

        validacion = agregar_platillo(nombre, precio, categoria, ingredientes, imagen_url, etiquetas, descripcion)
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
        # Imagen: si el usuario subió un archivo, tiene prioridad sobre la URL
        archivo_imagen = request.files.get("imagen_archivo")
        if archivo_imagen and archivo_imagen.filename:
            resultado_subida = subir_imagen_platillo(archivo_imagen)
            if not resultado_subida["ok"]:
                return manejar_error(resultado_subida["error"], contexto="Subir imagen del platillo")
            imagen_url = resultado_subida["url"]
        else:
            imagen_url = request.form.get("imagen_url", "")

        campos = {
            "name": request.form.get("nombre", ""),
            "price": float(request.form.get("precio", 0)),
            "category": request.form.get("categoria", ""),
            "ingredients": request.form.get("ingredientes", ""),
            "image_url": imagen_url,
            "tags": request.form.getlist("etiquetas"),
            "description": request.form.get("descripcion", ""),
            "is_available": request.form.get("disponible") == "on",
        }
        platillo_actualizado = editar_platillo(platillo, campos)
        if not platillo_actualizado["ok"]:
            return manejar_error(platillo_actualizado["error"], contexto="Editar platillo")
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

# ─── Fase 12: Stripe (demo/simulación de suscripción al Plan Pro) ──────────
# IMPORTANTE: todo esto corre en modo TEST de Stripe. No se procesan pagos
# reales bajo ninguna circunstancia; es únicamente para la demostración.

@app.route("/subscribe", methods=["POST"])
@login_required
def subscribe():
    """
    Inicia el proceso de suscripción al Plan Pro.
    Crea una sesión de Stripe Checkout y redirige al usuario a la página
    de pago hosteada por Stripe (no construimos ningún formulario propio).
    """
    user_id = session.get("user")
    restaurante = obtener_restaurante(user_id)

    if not restaurante["ok"] or not restaurante["data"]:
        flash("Primero completá el perfil de tu restaurante.", "warning")
        return redirect(url_for("profile"))

    restaurant_id = restaurante["data"][0]["id"]

    # Stripe necesita el {CHECKOUT_SESSION_ID} literal en la URL: lo agrega
    # automáticamente al redirigir de vuelta a nuestro sitio.
    success_url = url_for("subscription_success", _external=True) + "?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = url_for("subscription_cancel", _external=True)

    resultado = crear_checkout_session(
        restaurant_id=restaurant_id,
        success_url=success_url,
        cancel_url=cancel_url,
        email=session.get("email"),
    )

    if not resultado["ok"]:
        return manejar_error(resultado["error"], contexto="Crear sesión de pago")

    # Redirige al usuario a la página de Stripe Checkout (fuera de nuestro sitio)
    return redirect(resultado["url"])


@app.route("/subscription/success")
@login_required
def subscription_success():
    """
    Stripe redirige acá después de un pago exitoso.
    NUNCA confiamos únicamente en el redirect: verificamos directamente
    con la API de Stripe que el pago sí se completó antes de activar el
    Plan Pro en la base de datos.
    """
    session_id = request.args.get("session_id")

    if not session_id:
        flash("No se recibió información de la sesión de pago.", "danger")
        return redirect(url_for("profile"))

    resultado = verificar_pago(session_id)

    if not resultado["ok"]:
        return manejar_error(resultado["error"], contexto="Verificar pago")

    if resultado["pagado"] and resultado["restaurant_id"]:
        actualizar_restaurante(resultado["restaurant_id"], {"plan": "pro"})
        flash("¡Listo! Tu restaurante ahora tiene el Plan Pro. 🎉", "success")
    else:
        flash("El pago no se pudo confirmar. Intentá de nuevo.", "warning")

    return redirect(url_for("profile"))


@app.route("/subscription/cancel")
@login_required
def subscription_cancel():
    """El usuario canceló el checkout desde Stripe antes de pagar."""
    flash("Cancelaste el proceso de pago. Podés intentarlo de nuevo cuando quieras.", "info")
    return redirect(url_for("profile"))


@app.errorhandler(404)
def pagina_no_encontrada(error):
    return manejar_error(error, contexto="Pagina no encontrada")

@app.errorhandler(500)
def error_interno(error):
    return manejar_error(error, contexto="Error interno del servidor")

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False") == "True"
    app.run(debug=debug_mode)
