# menu_logic.py - Lógica de negocio pura de AutoMenu AI
# Contiene todas las funciones de manejo de platillos
# Importado por app.py para las rutas del dashboard

from datetime import datetime
import random
import math

# ─── Agregar platillo ─────────────────────────────────────────
def agregar_platillo(nombre, precio, categoria, ingredientes, imagen_url="", etiquetas=[]):
    """Crea un diccionario con la info del platillo y lo valida."""
    # Condicionales de validación
    if not nombre or nombre.strip() == "":
        return {"ok": False, "error": "El nombre no puede estar vacío"}
    if precio <= 0:
        return {"ok": False, "error": "El precio debe ser mayor a 0"}
    categorias_validas = ["entradas", "platos fuertes", "hamburguesas", "tacos", "bebidas", "postres", "combos"]
    if categoria.lower() not in categorias_validas:
        return {"ok": False, "error": f"Categoría inválida. Opciones: {categorias_validas}"}

    # Diccionario del platillo
    platillo = {
        "nombre": nombre.strip(),          # str
        "precio": float(precio),           # float
        "categoria": categoria.lower(),    # str
        "ingredientes": ingredientes,      # str
        "imagen_url": imagen_url,          # str
        "etiquetas": etiquetas,            # lista
        "disponible": True,                # bool
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
        if p["nombre"].lower() == nombre.lower():
            lista_platillos.pop(i)
            return {"ok": True}
    return {"ok": False, "error": "Platillo no encontrado"}

# ─── Filtrar por categoría ────────────────────────────────────
def filtrar_por_categoria(lista_platillos, categoria):
    """Recorre la lista con for y retorna solo los de esa categoría."""
    resultado = []
    for platillo in lista_platillos:
        if platillo["categoria"] == categoria.lower():
            resultado.append(platillo)
    return resultado

# ─── Promedio de precios ──────────────────────────────────────
def promedio_precios(lista_platillos):
    """Calcula el promedio de precios usando for y math."""
    if not lista_platillos:
        return 0
    total = 0
    for platillo in lista_platillos:
        total += platillo["precio"]
    return round(math.fabs(total / len(lista_platillos)), 2)

# ─── Platillo más caro y más barato ──────────────────────────
def platillo_mas_caro(lista_platillos):
    """Retorna el platillo con el precio más alto."""
    if not lista_platillos:
        return None
    mas_caro = lista_platillos[0]
    for platillo in lista_platillos:
        if platillo["precio"] > mas_caro["precio"]:
            mas_caro = platillo
    return mas_caro

def platillo_mas_barato(lista_platillos):
    """Retorna el platillo con el precio más bajo."""
    if not lista_platillos:
        return None
    mas_barato = lista_platillos[0]
    for platillo in lista_platillos:
        if platillo["precio"] < mas_barato["precio"]:
            mas_barato = platillo
    return mas_barato

# ─── Platillo del día ─────────────────────────────────────────
def sugerir_platillo_del_dia(lista_platillos):
    """Elige un platillo disponible al azar usando random."""
    disponibles = []
    for platillo in lista_platillos:
        if platillo["disponible"]:
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
    print("Más caro:", platillo_mas_caro(platillos)["nombre"])
    print("Más barato:", platillo_mas_barato(platillos)["nombre"])
    print("Platillo del día:", sugerir_platillo_del_dia(platillos)["nombre"])