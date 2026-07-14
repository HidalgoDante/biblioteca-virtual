import db
import logica_libros as ll

def test_insertar_y_buscar_libro(monkeypatch):
    # 1. Conexión de prueba en memoria, con las tablas creadas
    conn_test, cursor_test = db.conectar(":memory:")
    db.crear_tablas(cursor_test, conn_test)

    # 2. Le decimos a logica_libros que, por esta vez, use la conexión de prueba
    monkeypatch.setattr(ll, "conn", conn_test)
    monkeypatch.setattr(ll, "cursor", cursor_test)

    # 3. Ahora sí, probamos la función real, contra la base de prueba
    datos = ("001", "", "2024-01-01", "El Aleph", "Borges", "Emecé", "Compra", "")
    ll.insertar_libro_db(datos)

    resultado = ll.buscar_libro_db("001", "")

    # 4. Verificamos que lo que insertamos es lo que aparece
    assert len(resultado) == 1
    assert resultado[0][4] == "El Aleph"  # columna 'titulo'

def test_eliminar_libro_db(monkeypatch):
    conn_test, cursor_test = db.conectar(":memory:")
    db.crear_tablas(cursor_test, conn_test)
    monkeypatch.setattr(ll, "conn", conn_test)
    monkeypatch.setattr(ll, "cursor", cursor_test)

    datos = ("001", "", "2024-01-01", "El Aleph", "Borges", "Emecé", "Compra", "")
    ll.insertar_libro_db(datos)

    encontrado = ll.buscar_libro_db("001", "")
    id_real = encontrado[0][0]  # primera fila, primera columna = id

    ll.eliminar_libro_db(id_real)
    resultado = ll.buscar_libro_db("001", "")
    assert len(resultado) == 0

    # ACÁ: eliminar usando id_real, volver a buscar, y el assert final