import sqlite3

#conexión db

conn = sqlite3.connect("biblioteca.db")
cursor = conn.cursor()

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