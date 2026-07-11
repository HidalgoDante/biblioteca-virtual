from db import conn, cursor

def marcar_devuelto_db(id_prestamo):

    """Marca el préstamo con el id dado como devuelto."""

    cursor.execute("UPDATE prestamos SET devuelto=1 WHERE id=?", (id_prestamo,))
    conn.commit()

def guardar_prestamo_db(datos_prestamo):

    """datos_prestamo = (nombre, telefono, carrera, anio_cursada, libro, fecha_prestamo, fecha_devolucion)"""

    cursor.execute("""
        INSERT INTO prestamos (nombre, telefono, carrera, anio_cursada, libro, fecha_prestamo, fecha_devolucion)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, datos_prestamo)
    conn.commit()

def eliminar_prestamo_db(id_prestamo_eliminar):
    
    """Borra el prestamo con el id dado"""

    cursor.execute("DELETE FROM prestamos WHERE id=?", (id_prestamo_eliminar,))
    conn.commit()