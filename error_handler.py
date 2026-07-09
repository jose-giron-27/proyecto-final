# error_handler.py - Manejo centralizado de errores de AutoMenu AI
# Captura excepciones, imprime el detalle en terminal con print()
# y devuelve un JSON al frontend para mostrar el modal de error

from flask import jsonify

# ─── Manejador principal de errores ──────────────────────────
def manejar_error(error, contexto=""):
    """
    Recibe un error, lo imprime completo en terminal con print()
    y devuelve un JSON con mensaje amigable para el frontend.
    El frontend muestra un modal con el mensaje y pide revisar la terminal.
    """
    # Imprimir error completo en terminal
    print("=" * 50)
    print(f"[ERROR] Contexto: {contexto}")
    print(f"[ERROR] Tipo: {type(error).__name__}")
    print(f"[ERROR] Detalle: {str(error)}")
    print("=" * 50)

    # Determinar código HTTP según tipo de error
    if "no encontrada" in contexto.lower() or "404" in str(error):
        codigo_http = 404
        mensaje = "Página no encontrada."
    elif "no autorizado" in contexto.lower() or "401" in str(error):
        codigo_http = 401
        mensaje = "No tenés permiso para hacer esto."
    else:
        codigo_http = 500
        mensaje = "Algo salió mal en el servidor."

    # Respuesta JSON para el frontend
    # Flask permite retornar una TUPLA (respuesta, código_http); así se
    # manda el JSON y el status code (404/401/500) en un solo return
    return jsonify({
        "ok": False,
        "mensaje": mensaje,
        "contexto": contexto,
        "detalle": "Revisá la terminal para ver el error completo."
    }), codigo_http

# ─── Manejador para errores de validación ────────────────────
def manejar_validacion(campo, mensaje_error):
    """
    Para errores de validación de formularios.
    Los imprime en terminal y los devuelve al frontend.
    """
    print(f"[VALIDACIÓN] Campo '{campo}': {mensaje_error}")

    return jsonify({
        "ok": False,
        "campo": campo,
        "mensaje": mensaje_error,
        "detalle": "Revisá los datos ingresados."
    }), 400

# ─── Punto de entrada para pruebas ───────────────────────────
if __name__ == "__main__":
    print("Probando error_handler...")
    print("manejar_error y manejar_validacion están listos para usarse.")