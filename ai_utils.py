# ai_utils.py - Funciones de IA generativa de AutoMenu AI
# Usa la API de OpenAI para generar contenido para los platillos
# Importado por app.py para las rutas de generacion con IA

from openai import OpenAI
import base64
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Inicializar el cliente de OpenAI con la API key del .env
cliente = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ─── Generador de descripciones ───────────────────────────────
def generar_descripcion(nombre, ingredientes, precio, tono="casual", max_intentos=3):
    """
    Genera una descripcion atractiva del platillo.
    Usa while para reintentar si la API falla.
    """
    intentos = 0
    while intentos < max_intentos:
        try:
            prompt = f"""Genera una descripcion atractiva para un platillo de restaurante.
Nombre: {nombre}
Ingredientes: {ingredientes}
Precio: Q{precio}
Tono: {tono}
La descripcion debe ser breve (2-3 oraciones), clara y vendedora. Solo devuelve la descripcion, sin titulos ni explicaciones."""

            respuesta = cliente.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            return {"ok": True, "descripcion": respuesta.choices[0].message.content.strip()}

        except Exception as e:
            intentos += 1
            print(f"[ai_utils] Intento {intentos} fallido en generar_descripcion: {e}")

    return {"ok": False, "error": "No se pudo generar la descripcion despues de varios intentos"}

# ─── Traductor de descripcion ─────────────────────────────────
def traducir_descripcion(descripcion, idioma="ingles", max_intentos=3):
    """Traduce la descripcion del platillo al idioma indicado."""
    intentos = 0
    while intentos < max_intentos:
        try:
            prompt = f"""Traduce esta descripcion de platillo al {idioma}.
Solo devuelve la traduccion, sin explicaciones:
{descripcion}"""

            respuesta = cliente.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            return {"ok": True, "traduccion": respuesta.choices[0].message.content.strip()}

        except Exception as e:
            intentos += 1
            print(f"[ai_utils] Intento {intentos} fallido en traducir_descripcion: {e}")

    return {"ok": False, "error": "No se pudo traducir despues de varios intentos"}

# ─── Generador de captions para redes ────────────────────────
def generar_caption(nombre, descripcion, precio, red="instagram", max_intentos=3):
    """Genera un caption listo para publicar en redes sociales."""
    intentos = 0
    while intentos < max_intentos:
        try:
            prompt = f"""Genera un caption para {red} de este platillo de restaurante.
Nombre: {nombre}
Descripcion: {descripcion}
Precio: Q{precio}
Debe incluir emojis, ser llamativo y tener hashtags relevantes. Solo devuelve el caption."""

            respuesta = cliente.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            return {"ok": True, "caption": respuesta.choices[0].message.content.strip()}

        except Exception as e:
            intentos += 1
            print(f"[ai_utils] Intento {intentos} fallido en generar_caption: {e}")

    return {"ok": False, "error": "No se pudo generar el caption despues de varios intentos"}

# ─── Sugeridor de combos ──────────────────────────────────────
def sugerir_combo(lista_platillos, max_intentos=3):
    """Analiza los platillos existentes y sugiere un combo con descripcion."""
    intentos = 0
    while intentos < max_intentos:
        try:
            nombres = [p["nombre"] for p in lista_platillos]
            prompt = f"""Tengo estos platillos en mi restaurante: {", ".join(nombres)}.
Sugiere el mejor combo posible combinando 2 o 3 de ellos.
Devuelve: nombre del combo, platillos incluidos y una descripcion corta de venta."""

            respuesta = cliente.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            return {"ok": True, "combo": respuesta.choices[0].message.content.strip()}

        except Exception as e:
            intentos += 1
            print(f"[ai_utils] Intento {intentos} fallido en sugerir_combo: {e}")

    return {"ok": False, "error": "No se pudo sugerir el combo despues de varios intentos"}

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

            respuesta = cliente.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            etiquetas = [e.strip() for e in respuesta.choices[0].message.content.split(",")]
            return {"ok": True, "etiquetas": etiquetas}

        except Exception as e:
            intentos += 1
            print(f"[ai_utils] Intento {intentos} fallido en recomendar_etiquetas: {e}")

    return {"ok": False, "error": "No se pudieron recomendar etiquetas despues de varios intentos"}

# ─── Mejorador de nombres ─────────────────────────────────────
def mejorar_nombre(nombre_original, max_intentos=3):
    """Sugiere nombres mas llamativos para el platillo."""
    intentos = 0
    while intentos < max_intentos:
        try:
            prompt = f"""Sugiere 4 nombres mas atractivos y creativos para este platillo: {nombre_original}.
Solo devuelve los 4 nombres, uno por linea, sin numeracion ni explicaciones."""

            respuesta = cliente.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}]
            )
            nombres = [n.strip() for n in respuesta.choices[0].message.content.strip().split("\n") if n.strip()]
            return {"ok": True, "nombres": nombres}

        except Exception as e:
            intentos += 1
            print(f"[ai_utils] Intento {intentos} fallido en mejorar_nombre: {e}")

    return {"ok": False, "error": "No se pudieron sugerir nombres despues de varios intentos"}

# ─── Escaneo de menu desde imagen ────────────────────────────
def escanear_menu_desde_imagen(imagen_bytes, max_intentos=3):
    """
    Recibe una imagen de un menu fisico y extrae los platillos con IA de vision.
    Retorna una lista de dicts con nombre, precio y categoria detectados.
    """
    intentos = 0
    while intentos < max_intentos:
        try:
            # Convertir los bytes de la imagen a base64
            imagen_base64 = base64.standard_b64encode(imagen_bytes).decode("utf-8")

            prompt = """Analiza esta imagen de un menu de restaurante.
Extrae todos los platillos que puedas identificar y devuelve SOLO un JSON valido con esta estructura:
[{"nombre": "...", "precio": 0.0, "categoria": "..."}]
Si no puedes leer el precio, usa 0.0. Si no puedes identificar la categoria, usa "general"."""

            # Llamar a la API con vision (gpt-4o soporta imagenes)
            respuesta = cliente.chat.completions.create(
                model="gpt-4o",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{imagen_base64}"
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }]
            )

            # Limpiar la respuesta y parsear el JSON
            texto = respuesta.choices[0].message.content.strip()
            texto_limpio = texto.replace("```json", "").replace("```", "").strip()
            platillos = json.loads(texto_limpio)
            return {"ok": True, "platillos": platillos}

        except json.JSONDecodeError as e:
            intentos += 1
            print(f"[ai_utils] Intento {intentos} fallido en escanear_menu_desde_imagen (JSON invalido): {e}")
        except Exception as e:
            intentos += 1
            print(f"[ai_utils] Intento {intentos} fallido en escanear_menu_desde_imagen: {e}")

    return {"ok": False, "error": "No se pudo escanear la imagen despues de varios intentos"}
