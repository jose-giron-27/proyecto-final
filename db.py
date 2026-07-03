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

# ─── Punto de entrada para pruebas ───────────────────────────
if __name__ == "__main__":
    print("Probando conexión con Supabase...")
    resultado = db_get("dishes")
    if resultado["ok"]:
        print(f"Conexión exitosa. Platillos encontrados: {len(resultado['data'])}")
    else:
        print(f"Error de conexión: {resultado['error']}")