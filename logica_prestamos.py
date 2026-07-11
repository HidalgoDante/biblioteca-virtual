from datetime import datetime
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

def guardar_cambios_prestamo_db(datos_cambios_prestamo):
    """Guarda el prestamo editado en la db"""
    cursor.execute("""
        UPDATE prestamos
        SET nombre=?, telefono=?, carrera=?, anio_cursada=?, libro=?, fecha_prestamo=?, fecha_devolucion=?
        WHERE id=?
    """, datos_cambios_prestamo)
    conn.commit()

def historial_prestamos_db():
    """Devuelve todos los préstamos (activos y devueltos), del más nuevo al más viejo."""
    cursor.execute("SELECT * FROM prestamos ORDER BY id DESC")
    return cursor.fetchall()

def prestamos_caducados_db():
    """Devuelve los préstamos vencidos (no devueltos y con fecha de devolución pasada)."""
    hoy = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT * FROM prestamos WHERE devuelto=0 AND fecha_devolucion < ? ORDER BY fecha_devolucion ASC",
        (hoy,))
    return cursor.fetchall()

def prestamos_activos_db():
    """Devuelve solamente los prestamos activos"""
    cursor.execute("SELECT * FROM prestamos WHERE devuelto = 0")
    return cursor.fetchall()

def verificar_vencimientos_db():
    """Devuelve los préstamos activos (no devueltos), para que la UI calcule cuáles están vencidos o por vencer."""
    cursor.execute("SELECT nombre, telefono, libro, fecha_devolucion FROM prestamos WHERE devuelto=0")
    return cursor.fetchall()