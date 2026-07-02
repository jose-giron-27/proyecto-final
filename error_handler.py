# error_handler.py - Manejo centralizado de errores de AutoMenu AI
# Captura excepciones, imprime el detalle en terminal con print()
# y devuelve un JSON al frontend para mostrar el modal de error

from flask import jsonify

def manejar_error(error, contexto=""):
    """
    Recibe un error, lo imprime en terminal y devuelve
    un JSON con un mensaje amigable para el frontend.
    """
    mensaje_terminal = f"[ERROR] {contexto}: {str(error)}"
    print(mensaje_terminal)

    return jsonify({
        "ok": False,
        "mensaje": "Algo salió mal. Revisá la terminal para más detalles.",
        "contexto": contexto
    }), 500
