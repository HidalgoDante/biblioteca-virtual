import csv
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

def importar_csv_libros_db(ruta):
    """Lee un CSV de libros desde 'ruta' e inserta las filas válidas en la tabla libros.
    Levanta una excepción si el archivo no se puede leer.
    Devuelve (insertados, errores)."""
    columnas_esperadas = ["n_inv", "mfn", "fecha", "titulo", "autor", "editorial", "proc", "observaciones"]
    insertados = 0
    errores = 0

    with open(ruta, newline="", encoding="utf-8-sig") as f:
        muestra = f.read(2048)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(muestra)
        except Exception:
            dialect = csv.excel
        lector = csv.reader(f, dialect)
        filas = list(lector)

    if not filas:
        return (0, 0)
    
    primera = [c.strip().lower() for c in filas[0]]
    tiene_encabezado = any(c in columnas_esperadas for c in primera)
    inicio = 1 if tiene_encabezado else 0

    if tiene_encabezado:
        indices = []
        for col in columnas_esperadas:
            indices.append(primera.index(col) if col in primera else None)
    else:
        indices = list(range(min(8, len(filas[0]))))
        indices += [None] * (8 - len(indices))
    
    for fila in filas[inicio:]:
        if not fila or all(not c.strip() for c in fila):
            continue
        try:
            valores = []
            for idx in indices:
                if idx is not None and idx < len(fila):
                    valores.append(fila[idx].strip())
                else:
                    valores.append("")
            if not valores[3]:  # título obligatorio
                errores += 1
                continue
            cursor.execute("""INSERT INTO libros (n_inv, mfn, fecha, titulo, autor, editorial, proc, observaciones) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, valores)
            insertados += 1
        except Exception:
            errores += 1

    conn.commit()
    return (insertados, errores)

def exportar_csv_libros_db(ruta):
    """Exporta todos los libros de la base a un archivo CSV en 'ruta'.
    Devuelve la cantidad de libros exportados."""
    cursor.execute("SELECT n_inv, mfn, fecha, titulo, autor, editorial, proc, observaciones FROM libros")
    regs = cursor.fetchall()

    columnas = ["n_inv", "mfn", "fecha", "titulo", "autor", "editorial", "proc", "observaciones"]
    with open(ruta, "w", newline="", encoding="utf-8") as f:  #Abre el archivo
        escritor = csv.writer(f)    #Se le da formato csv
        escritor.writerow(columnas)  #Escribe solamente una fila
        escritor.writerows(regs)     #Escribe muchas filas de una (todos los libros de regs)
    return len(regs) #Devuelve cuantos libros se exportaron