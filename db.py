# db.py - Conexión con Supabase
# Importado por app.py y menu_logic.py para operaciones de base de datos

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

# TODO: activar en Fase 02 cuando esté configurado Supabase
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
