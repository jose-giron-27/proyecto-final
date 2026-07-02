# ai_utils.py - Funciones de IA generativa de AutoMenu AI
# Importado por app.py para las rutas de generación con IA
# Usa while loop para reintentar llamadas fallidas a la API

import anthropic
import base64
import os
from dotenv import load_dotenv

load_dotenv()

cliente = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ─── Generador de descripciones ───────────────────────────────
def generar_descripcion(nombre, ingredientes, precio, tono="casual", max_intentos=3):
    """
    Genera una descripción atractiva del platillo.
    Usa while para reintentar si la API falla.
    """
    intentos = 0
    while intentos < max_intentos:
        try:
            prompt = f"""Genera una descripción atractiva para un platillo de restaurante.
Nombre: {nombre}
Ingredientes: {ingredientes}
Precio: Q{precio}
Tono: {tono}
La descripción debe ser breve (2-3 oraciones), clara y vendedora. Solo devuelve la descripción, sin títulos ni explicaciones."""

            respuesta = cliente.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            return {"ok": True, "descripcion": respuesta.content[0].text.strip()}

        except Exception as e:
            intentos += 1
            print(f"[ai_utils] Intento {intentos} fallido en generar_descripcion: {e}")

    return {"ok": False, "error": "No se pudo generar la descripción después de varios intentos"}

# ─── Traductor de descripción ─────────────────────────────────
def traducir_descripcion(descripcion, idioma="inglés", max_intentos=3):
    """Traduce la descripción del platillo al idioma indicado."""
    intentos = 0
    while intentos < max_intentos:
        try:
            prompt = f"""Traduce esta descripción de platillo al {idioma}. 
Solo devuelve la traducción, sin explicaciones:
{descripcion}"""

            respuesta = cliente.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            return {"ok": True, "traduccion": respuesta.content[0].text.strip()}

        except Exception as e:
            intentos += 1
            print(f"[ai_utils] Intento {intentos} fallido en traducir_descripcion: {e}")

    return {"ok": False, "error": "No se pudo traducir después de varios intentos"}

# ─── Generador de captions para redes ────────────────────────
def generar_caption(nombre, descripcion, precio, red="instagram", max_intentos=3):
    """Genera un caption listo para publicar en redes sociales."""
    intentos = 0
    while intentos < max_intentos:
        try:
            prompt = f"""Genera un caption para {red} de este platillo de restaurante.
Nombre: {nombre}
Descripción: {descripcion}
Precio: Q{precio}
Debe incluir emojis, ser llamativo y tener hashtags relevantes. Solo devuelve el caption."""

            respuesta = cliente.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            return {"ok": True, "caption": respuesta.content[0].text.strip()}

        except Exception as e:
            intentos += 1
            print(f"[ai_utils] Intento {intentos} fallido en generar_caption: {e}")

    return {"ok": False, "error": "No se pudo generar el caption después de varios intentos"}

# ─── Sugeridor de combos ──────────────────────────────────────
def sugerir_combo(lista_platillos, max_intentos=3):
    """Analiza los platillos existentes y sugiere un combo con descripción."""
    intentos = 0
    while intentos < max_intentos:
        try:
            nombres = [p["nombre"] for p in lista_platillos]
            prompt = f"""Tengo estos platillos en mi restaurante: {', '.join(nombres)}.
Sugiere el mejor combo posible combinando 2 o 3 de ellos.
Devuelve: nombre del combo, platillos incluidos y una descripción corta de venta."""

            respuesta = cliente.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            return {"ok": True, "combo": respuesta.content[0].text.strip()}

        except Exception as e:
            intentos += 1
            print(f"[ai_utils] Intento {intentos} fallido en sugerir_combo: {e}")

    return {"ok": False, "error": "No se pudo sugerir el combo después de varios intentos"}

# ─── Recomendador de etiquetas ────────────────────────────────
def recomendar_etiquetas(ingredientes, max_intentos=3):
    """Analiza ingredientes y sugiere etiquetas como vegetariano, picante, etc."""
    intentos = 0
    while intentos < max_intentos:
        try:
            prompt = f"""Analiza estos ingredientes y sugiere etiquetas para el platillo.
Ingredientes: {ingredientes}
Etiquetas posibles: vegetariano, vegano, picante, sin gluten, nuevo, popular, recomendado, ligero.
Solo devuelve las etiquetas que apliquen, separadas por comas."""

            respuesta = cliente.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            etiquetas = [e.strip() for e in respuesta.content[0].text.split(",")]
            return {"ok": True, "etiquetas": etiquetas}

        except Exception as e:
            intentos += 1
            print(f"[ai_utils] Intento {intentos} fallido en recomendar_etiquetas: {e}")

    return {"ok": False, "error": "No se pudieron recomendar etiquetas después de varios intentos"}

# ─── Mejorador de nombres ─────────────────────────────────────
def mejorar_nombre(nombre_original, max_intentos=3):
    """Sugiere nombres más llamativos para el platillo."""
    intentos = 0
    while intentos < max_intentos:
        try:
            prompt = f"""Sugiere 4 nombres más atractivos y creativos para este platillo: {nombre_original}.
Solo devuelve los 4 nombres, uno por línea, sin numeración ni explicaciones."""

            respuesta = cliente.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            nombres = [n.strip() for n in respuesta.content[0].text.strip().split("\n") if n.strip()]
            return {"ok": True, "nombres": nombres}

        except Exception as e:
            intentos += 1
            print(f"[ai_utils] Intento {intentos} fallido en mejorar_nombre: {e}")

    return {"ok": False, "error": "No se pudieron sugerir nombres después de varios intentos"}

# ─── Escaneo de menú desde imagen ────────────────────────────
def escanear_menu_desde_imagen(imagen_bytes, max_intentos=3):
    """
    Recibe una imagen de un menú físico y extrae los platillos con IA de visión.
    Retorna una lista de dicts con nombre, precio y categoría detectados.
    """
    intentos = 0
    while intentos < max_intentos:
        try:
            imagen_base64 = base64.standard_b64encode(imagen_bytes).decode("utf-8")

            prompt = """Analizá esta imagen de un menú de restaurante.
Extraé todos los platillos que puedas identificar y devolvé SOLO un JSON válido con esta estructura:
[{"nombre": "...", "precio": 0.0, "categoria": "..."}]
Si no podés leer el precio, usá 0.0. Si no podés identificar la categoría, usá "general"."""

            respuesta = cliente.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": imagen_base64
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }]
            )
            import json
            platillos = json.loads(respuesta.content[0].text.strip())
            return {"ok": True, "platillos": platillos}

        except Exception as e:
            intentos += 1
            print(f"[ai_utils] Intento {intentos} fallido en escanear_menu_desde_imagen: {e}")

    return {"ok": False, "error": "No se pudo escanear la imagen después de varios intentos"}