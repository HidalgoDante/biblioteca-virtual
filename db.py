import sqlite3

def conectar(ruta="biblioteca.db"):
    """Crea una conexión y un cursor apuntando a la base indicada (por defecto, la real)."""
    conn = sqlite3.connect(ruta)
    cursor = conn.cursor()
    return conn, cursor

def crear_tablas(cursor, conn):
    """Crea las tablas si no existen, sobre la conexión dada."""
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS libros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        n_inv TEXT,
        mfn TEXT,
        fecha TEXT,
        titulo TEXT,
        autor TEXT,
        editorial TEXT,
        proc TEXT,
        observaciones TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prestamos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        telefono TEXT,
        carrera TEXT,
        anio_cursada TEXT,
        libro TEXT,
        fecha_prestamo TEXT,
        fecha_devolucion TEXT,
        devuelto INTEGER DEFAULT 0
    )
    """)
    conn.commit()

# Conexión por defecto que usa toda la app real
conn, cursor = conectar()
crear_tablas(cursor, conn)