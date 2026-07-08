# menu_logic.py - Lógica de negocio pura de AutoMenu AI
# Contiene todas las funciones de manejo de platillos
# Importado por app.py para las rutas del dashboard

from datetime import datetime
import random
import math

# ─── Agregar platillo ─────────────────────────────────────────
def agregar_platillo(nombre, precio, categoria, ingredientes, imagen_url="", etiquetas=None, descripcion=""):
    """Crea un diccionario con la info del platillo y lo valida."""
    # Condicionales de validación
    if not nombre or nombre.strip() == "":
        return {"ok": False, "error": "El nombre no puede estar vacío"}
    if precio <= 0:
        return {"ok": False, "error": "El precio debe ser mayor a 0"}
    if not categoria or categoria.strip() == "":
        return {"ok": False, "error": "La categoría no puede estar vacía"}
    
    if etiquetas is None:
        etiquetas = []

    # Diccionario del platillo
    # IMPORTANTE: estas llaves deben coincidir EXACTAMENTE con las columnas
    # reales de la tabla "dishes" en Supabase (id, restaurant_id, name,
    # description, ai_description, price, category, ingredients, image_url,
    # is_available, tags, created_at, updated_at). Los parámetros de esta
    # función siguen en español, pero el diccionario que se inserta a la
    # base de datos usa los nombres de columna reales (en inglés).
    platillo = {
        "name": nombre.strip(),            # str
        "price": float(precio),            # float
        "category": categoria.strip(),     # str
        "ingredients": ingredientes,       # str
        "image_url": imagen_url,           # str
        "description": descripcion,        # str
        "tags": etiquetas,                 # lista
        "is_available": True,              # bool
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    return {"ok": True, "platillo": platillo}

# ─── Editar platillo ──────────────────────────────────────────
def editar_platillo(platillo, campos):
    """Actualiza los campos de un platillo y registra la fecha de edición."""
    for clave, valor in campos.items():
        if clave in platillo:
            platillo[clave] = valor
    platillo["updated_at"] = datetime.now().isoformat()
    return {"ok": True, "platillo": platillo}

# ─── Eliminar platillo ────────────────────────────────────────
def eliminar_platillo(lista_platillos, nombre):
    """Elimina un platillo de la lista por nombre. Retorna True si lo encontró."""
    for i, p in enumerate(lista_platillos):
        if p["name"].lower() == nombre.lower():
            lista_platillos.pop(i)
            return {"ok": True}
    return {"ok": False, "error": "Platillo no encontrado"}

# ─── Filtrar por categoría ────────────────────────────────────
def filtrar_por_categoria(lista_platillos, categoria):
    """Recorre la lista con for y retorna solo los de esa categoría."""
    resultado = []
    for platillo in lista_platillos:
        if platillo["category"].lower() == categoria.lower():
            resultado.append(platillo)
    return resultado

# ─── Promedio de precios ──────────────────────────────────────
def promedio_precios(lista_platillos):
    """Calcula el promedio de precios usando for y math."""
    if not lista_platillos:
        return 0
    total = 0
    for platillo in lista_platillos:
        total += platillo["price"]
    return round(math.fabs(total / len(lista_platillos)), 2)

# ─── Platillo más caro y más barato ──────────────────────────
def platillo_mas_caro(lista_platillos):
    """
    Retorna el platillo con el precio más alto, usando recursión.
    Caso base: lista de 0 o 1 platillo. Caso recursivo: comparamos el
    primer platillo contra el más caro del resto de la lista.
    """
    if not lista_platillos:
        return None
    if len(lista_platillos) == 1:
        return lista_platillos[0]

    primero = lista_platillos[0]
    mas_caro_del_resto = platillo_mas_caro(lista_platillos[1:])

    if primero["price"] > mas_caro_del_resto["price"]:
        return primero
    return mas_caro_del_resto

def platillo_mas_barato(lista_platillos):
    """
    Retorna el platillo con el precio más bajo, usando recursión.
    Mismo enfoque que platillo_mas_caro, pero comparando hacia abajo.
    """
    if not lista_platillos:
        return None
    if len(lista_platillos) == 1:
        return lista_platillos[0]

    primero = lista_platillos[0]
    mas_barato_del_resto = platillo_mas_barato(lista_platillos[1:])

    if primero["price"] < mas_barato_del_resto["price"]:
        return primero
    return mas_barato_del_resto

# ─── Platillo del día ─────────────────────────────────────────
def sugerir_platillo_del_dia(lista_platillos):
    """Elige un platillo disponible al azar usando random."""
    disponibles = []
    for platillo in lista_platillos:
        if platillo["is_available"]:
            disponibles.append(platillo)
    if not disponibles:
        return None
    return random.choice(disponibles)

# ─── Punto de entrada para pruebas en consola ─────────────────
if __name__ == "__main__":
    platillos = []

    # Probar agregar platillos
    resultado = agregar_platillo("Smash Burger", 48.0, "hamburguesas", "carne, cheddar, pepinillos")
    if resultado["ok"]:
        platillos.append(resultado["platillo"])

    resultado = agregar_platillo("Limonada Natural", 15.0, "bebidas", "limón, agua, azúcar")
    if resultado["ok"]:
        platillos.append(resultado["platillo"])

    resultado = agregar_platillo("Pasta Alfredo", 55.0, "platos fuertes", "pasta, crema, parmesano, pollo")
    if resultado["ok"]:
        platillos.append(resultado["platillo"])

    print("Platillos agregados:", len(platillos))
    print("Promedio de precios:", promedio_precios(platillos))
    print("Más caro:", platillo_mas_caro(platillos)["name"])
    print("Más barato:", platillo_mas_barato(platillos)["name"])
    print("Platillo del día:", sugerir_platillo_del_dia(platillos)["name"])
