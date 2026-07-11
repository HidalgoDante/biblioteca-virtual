from db import conn, cursor

def eliminar_libro_db(id_libro):

    """Borra el libro con el id dado."""

    cursor.execute("DELETE FROM libros WHERE id=?", (id_libro,))
    conn.commit()

def insertar_libro_db(datos):
    """datos = (n_inv, mfn, fecha, titulo, autor, editorial, proc, observaciones)"""
    cursor.execute("""
        INSERT INTO libros (n_inv, mfn, fecha, titulo, autor, editorial, proc, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, datos)
    conn.commit()

def buscar_libro_db(filtro_inv, filtro_fecha):
    
    """Busca libros filtrando por N° de inventario y/o fecha (parciales, tipo LIKE).
    Devuelve una lista de tuplas con todas las columnas de la tabla libros."""

    q = "SELECT * FROM libros WHERE 1=1"
    params = []
    if filtro_inv:
        q += " AND n_inv LIKE ?"
        params.append("%" + filtro_inv + "%")
    if filtro_fecha:
        q += " AND fecha LIKE ?"
        params.append("%" + filtro_fecha + "%")
    cursor.execute(q, params)
    return cursor.fetchall()  #se retorna el valor para la ui


def mostrar_todos_libros_db(orden):

    """Trae todos los libros según el criterio de orden elegido en el combo.
    orden: "Más reciente" , "Más viejo" , "Alfabético (Título)" , cualquier otro (sin orden)."""

    if orden == "Más reciente":
        q = "SELECT * FROM libros ORDER BY id DESC"
    elif orden == "Más viejo":
        q = "SELECT * FROM libros ORDER BY id ASC"
    elif orden == "Alfabético (Título)":
        q = "SELECT * FROM libros ORDER BY titulo ASC"
    else:
        q = "SELECT * FROM libros"
    cursor.execute(q)
    return cursor.fetchall() #se retorna el valor para la ui


def actualizar_lista_libros_combo_db():
    """Actualiza la lista de libros"""
    cursor.execute("SELECT titulo FROM libros ORDER BY titulo ASC")
    return [r[0] for r in cursor.fetchall()]