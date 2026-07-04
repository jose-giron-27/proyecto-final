# db.py - Conexión con Supabase para AutoMenu AI
# Importado por app.py y menu_logic.py para operaciones de base de datos

from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

# ─── Conexión con Supabase ────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = None

def get_db():
    """
    Retorna la conexión a Supabase.
    Si no existe, la crea. Si faltan las variables de entorno, lanza un error.
    """
    global supabase
    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("Faltan las variables SUPABASE_URL o SUPABASE_KEY en el .env")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase

# ─── Helpers de base de datos ─────────────────────────────────
def db_get(tabla, filtros=None):
    """Obtiene registros de una tabla con filtros opcionales."""
    if filtros is None:
        filtros = {}
    try:
        db = get_db()
        query = db.table(tabla).select("*")
        for clave, valor in filtros.items():
            query = query.eq(clave, valor)
        return {"ok": True, "data": query.execute().data}
    except Exception as e:
        print(f"[db] Error en db_get ({tabla}): {e}")
        return {"ok": False, "error": str(e)}

def db_insert(tabla, datos):
    """Inserta un registro en la tabla indicada."""
    try:
        db = get_db()
        resultado = db.table(tabla).insert(datos).execute()
        return {"ok": True, "data": resultado.data}
    except Exception as e:
        print(f"[db] Error en db_insert ({tabla}): {e}")
        return {"ok": False, "error": str(e)}

def db_update(tabla, record_id, datos):
    """Actualiza un registro por su id."""
    try:
        db = get_db()
        resultado = db.table(tabla).update(datos).eq("id", record_id).execute()
        return {"ok": True, "data": resultado.data}
    except Exception as e:
        print(f"[db] Error en db_update ({tabla}): {e}")
        return {"ok": False, "error": str(e)}

def db_delete(tabla, record_id):
    """Elimina un registro por su id."""
    try:
        db = get_db()
        resultado = db.table(tabla).delete().eq("id", record_id).execute()
        return {"ok": True, "data": resultado.data}
    except Exception as e:
        print(f"[db] Error en db_delete ({tabla}): {e}")
        return {"ok": False, "error": str(e)}

# ─── Autenticación con Supabase ─────────────────────────────── #lo agragamos aquí justo para que se mantenga la arquitectura constante
def auth_register(email, password):
    """
    Registra un nuevo usuario utilizando Supabase Auth.
    """
    try:
        db = get_db()
        resultado = db.auth.sign_up({
            "email": email,
            "password": password
        })

        return {
            "ok": True,
            "user": resultado.user
        }

    except Exception as e:
        print(f"[db] Error en auth_register: {e}")
        return {
            "ok": False,
            "error": str(e)
        }


def auth_login(email, password):
    """
    Inicia sesión con Supabase Auth.
    """
    try:
        db = get_db()

        resultado = db.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        return {
            "ok": True,
            "session": resultado.session,
            "user": resultado.user
        }

    except Exception as e:
        print(f"[db] Error en auth_login: {e}")
        return {
            "ok": False,
            "error": str(e)
        }


def auth_logout():
    """
    Cierra la sesión actual.
    """
    try:
        db = get_db()

        db.auth.sign_out()

        return {"ok": True}

    except Exception as e:
        print(f"[db] Error en auth_logout: {e}")
        return {
            "ok": False,
            "error": str(e)
        }


# ─── Punto de entrada para pruebas ───────────────────────────

# ─── Helpers específicos de platillos ─────────────────────────
def get_dishes(restaurant_id):
    """Obtiene todos los platillos de un restaurante."""
    return db_get("dishes", filtros={"restaurant_id": restaurant_id})

def get_dish_by_id(dish_id):
    """Obtiene un platillo por su id."""
    try:
        db = get_db()
        resultado = db.table("dishes").select("*").eq("id", dish_id).execute()
        if resultado.data:
            return {"ok": True, "data": resultado.data[0]}
        return {"ok": False, "error": "Platillo no encontrado"}
    except Exception as e:
        print(f"[db] Error en get_dish_by_id: {e}")
        return {"ok": False, "error": str(e)}

def insert_dish(datos):
    """Inserta un nuevo platillo en la base de datos."""
    return db_insert("dishes", datos)

def update_dish(dish_id, datos):
    """Actualiza un platillo por su id."""
    return db_update("dishes", dish_id, datos)

def delete_dish(dish_id):
    """Elimina un platillo por su id."""
    return db_delete("dishes", dish_id)

def toggle_dish_availability(dish_id, is_available):
    """Activa o desactiva la disponibilidad de un platillo."""
    from datetime import datetime
    return db_update("dishes", dish_id, {
        "is_available": is_available,
        "updated_at": datetime.now().isoformat()
    })

if __name__ == "__main__":
    print("Probando conexión con Supabase...")
    resultado = db_get("dishes")
    if resultado["ok"]:
        print(f"Conexión exitosa. Platillos encontrados: {len(resultado['data'])}")
    else:
        print(f"Error de conexión: {resultado['error']}")