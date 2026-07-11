# biblioteca_con_prestamos_ventanas.py
import sqlite3
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from tkinter import font as tkFont
from datetime import datetime, timedelta

# -------------------------
# Conexión DB
# -------------------------
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

# -------------------------
# Funciones - Libros
# -------------------------

def actualizar_lista_libros_combo():
    """Devuelve lista de títulos actuales (usado por la ventana de préstamos)."""
    cursor.execute("SELECT titulo FROM libros ORDER BY titulo ASC")
    return [r[0] for r in cursor.fetchall()]

def actualizar_combo_libros_en_ventana_prestamos():
    """Actualiza el combobox de la ventana de préstamos si está abierto."""
    global prestamos_win, combo_libros
    if prestamos_win is not None and combo_libros is not None:
        combo_libros['values'] = actualizar_lista_libros_combo()

def mostrar_todos_libros():
    for row in tree_libros.get_children():
        tree_libros.delete(row)
    orden = combo_orden.get()
    if orden == "Más reciente":
        q = "SELECT * FROM libros ORDER BY id DESC"
    elif orden == "Más viejo":
        q = "SELECT * FROM libros ORDER BY id ASC"
    elif orden == "Alfabético (Título)":
        q = "SELECT * FROM libros ORDER BY titulo ASC"
    else:
        q = "SELECT * FROM libros"
    cursor.execute(q)
    regs = cursor.fetchall()
    for i, r in enumerate(regs):
        tag = "evenrow" if i % 2 == 0 else "oddrow"
        tree_libros.insert("", "end", values=r, tags=(tag,))

def guardar_libro():
    datos = (
        entry_inv.get(),
        entry_mfn.get(),
        entry_fecha.get_date().strftime("%Y-%m-%d") if hasattr(entry_fecha, "get_date") else entry_fecha.get(),
        entry_titulo.get(),
        entry_autor.get(),
        entry_editorial.get(),
        entry_proc.get(),
        entry_obs.get("1.0", "end").strip()
    )
    if not entry_titulo.get().strip():
        messagebox.showwarning("Atención", "El título es obligatorio.")
        return
    cursor.execute("""
        INSERT INTO libros (n_inv, mfn, fecha, titulo, autor, editorial, proc, observaciones)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, datos)
    conn.commit()
    limpiar_campos_libro()
    mostrar_todos_libros()
    # Actualiza combo en la ventana de préstamos si está abierta
    actualizar_combo_libros_en_ventana_prestamos()

def limpiar_campos_libro():
    entry_inv.delete(0, "end")
    entry_mfn.delete(0, "end")
    # si entry_fecha es DateEntry, seteamos a hoy
    try:
        entry_fecha.set_date(datetime.now().date())
    except Exception:
        entry_fecha.delete(0, "end")
    entry_titulo.delete(0, "end")
    entry_autor.delete(0, "end")
    entry_editorial.delete(0, "end")
    entry_proc.delete(0, "end")
    entry_obs.delete("1.0", "end")

def buscar_libros():
    for row in tree_libros.get_children():
        tree_libros.delete(row)
    filtro_inv = entry_buscar_inv.get().strip()
    filtro_fecha = entry_buscar_fecha.get().strip()
    q = "SELECT * FROM libros WHERE 1=1"
    params = []
    if filtro_inv:
        q += " AND n_inv LIKE ?"
        params.append("%" + filtro_inv + "%")
    if filtro_fecha:
        q += " AND fecha LIKE ?"
        params.append("%" + filtro_fecha + "%")
    cursor.execute(q, params)
    regs = cursor.fetchall()
    for i, r in enumerate(regs):
        tag = "evenrow" if i % 2 == 0 else "oddrow"
        tree_libros.insert("", "end", values=r, tags=(tag,))

def cargar_a_formulario_libro(event):
    sel = tree_libros.selection()
    if not sel:
        return
    vals = tree_libros.item(sel, "values")
    limpiar_campos_libro()
    # indices: 0=id,1=n_inv,2=mfn,3=fecha,4=titulo,...
    entry_inv.insert(0, vals[1])
    entry_mfn.insert(0, vals[2])
    # set fecha si DateEntry
    try:
        entry_fecha.set_date(datetime.strptime(vals[3], "%Y-%m-%d").date())
    except Exception:
        entry_fecha.delete(0, "end")
        entry_fecha.insert(0, vals[3])
    entry_titulo.insert(0, vals[4])
    entry_autor.insert(0, vals[5])
    entry_editorial.insert(0, vals[6])
    entry_proc.insert(0, vals[7])
    entry_obs.insert("1.0", vals[8])
    global id_seleccionado
    id_seleccionado = vals[0]

def eliminar_libro():
    sel = tree_libros.selection()
    if not sel:
        messagebox.showwarning("Atención", "Seleccioná un libro para eliminar.")
        return
    vals = tree_libros.item(sel, "values")
    idb = vals[0]
    if messagebox.askyesno("Confirmar", f"¿Eliminar '{vals[4]}'?"):
        cursor.execute("DELETE FROM libros WHERE id=?", (idb,))
        conn.commit()
        mostrar_todos_libros()
        actualizar_combo_libros_en_ventana_prestamos()
        limpiar_campos_libro()

# -------------------------
# Funciones - Préstamos (ventana secundaria)
# -------------------------

def abrir_ventana_prestamos():
    """Abre (o trae al frente) la ventana de préstamos."""
    global prestamos_win, combo_libros
    if prestamos_win is not None and prestamos_win.winfo_exists():
        prestamos_win.lift()
        return

    prestamos_win = tb.Toplevel(root)
    prestamos_win.title("Sistema de Préstamos")
    prestamos_win.geometry("900x600")
    prestamos_win.transient(root)

    # Layout del frame
    frame = tb.Frame(prestamos_win, padding=8)
    frame.pack(fill="both", expand=True)

    # Formulario
    tb.Label(frame, text="Nombre:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
    tb.Label(frame, text="Teléfono:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
    tb.Label(frame, text="Carrera:").grid(row=0, column=2, sticky="w", padx=4, pady=4)
    tb.Label(frame, text="Año:").grid(row=1, column=2, sticky="w", padx=4, pady=4)
    tb.Label(frame, text="Libro:").grid(row=2, column=0, sticky="w", padx=4, pady=4)
    tb.Label(frame, text="F. Préstamo:").grid(row=2, column=2, sticky="w", padx=4, pady=4)
    tb.Label(frame, text="F. Devolución:").grid(row=3, column=0, sticky="w", padx=4, pady=4)

    # Entradas
    global entry_nombre, entry_tel, entry_carrera, entry_anio, entry_fecha_prestamo, entry_fecha_devolucion, combo_libros
    entry_nombre = tb.Entry(frame, width=30)
    entry_tel = tb.Entry(frame, width=20)
    entry_carrera = tb.Entry(frame, width=30)
    entry_anio = tb.Entry(frame, width=10)

    entry_nombre.grid(row=0, column=1, padx=4, pady=4)
    entry_tel.grid(row=1, column=1, padx=4, pady=4)
    entry_carrera.grid(row=0, column=3, padx=4, pady=4)
    entry_anio.grid(row=1, column=3, padx=4, pady=4)

    # Combo libros (actualiza con la DB)
    combo_libros = tb.Combobox(frame, values=actualizar_lista_libros_combo(), width=55)
    combo_libros.grid(row=2, column=1, columnspan=1, padx=4, pady=4, sticky="w")

    # DateEntry para fechas
    entry_fecha_prestamo = tb.DateEntry(frame, dateformat="%Y-%m-%d")
    entry_fecha_devolucion = tb.DateEntry(frame, dateformat="%Y-%m-%d")
    entry_fecha_prestamo.grid(row=2, column=3, padx=4, pady=4)
    entry_fecha_devolucion.grid(row=3, column=1, padx=4, pady=4)

    # Inicializar fechas: préstamo hoy, devolución +7 días
    try:
        entry_fecha_prestamo.set_date(datetime.now().date())
        entry_fecha_devolucion.set_date((datetime.now() + timedelta(days=7)).date())
    except Exception:
        pass

    # Botones
    tb.Button(frame, text="Registrar préstamo", command=guardar_prestamo, bootstyle="success-outline").grid(row=4, column=0, padx=6, pady=8)
    tb.Button(frame, text="Marcar devuelto", command=marcar_devueltos, bootstyle="warning-outline").grid(row=4, column=1, padx=6, pady=8)
    tb.Button(frame, text="Limpiar", command=limpiar_prestamo, bootstyle="secondary-outline").grid(row=4, column=2, padx=6, pady=8)
    tb.Button(frame, text="Actualizar lista libros", command=lambda: combo_libros.configure(values=actualizar_lista_libros_combo()), bootstyle="info-outline").grid(row=4, column=3, padx=6, pady=8)

    # Tabla de préstamos activos
    tree_frame = tb.Frame(frame)
    tree_frame.grid(row=5, column=0, columnspan=4, sticky="nsew", pady=6)
    prestamos_win.rowconfigure(0, weight=1)
    prestamos_win.columnconfigure(0, weight=1)
    tree_frame.rowconfigure(0, weight=1)
    tree_frame.columnconfigure(0, weight=1)

    global tree_prestamos
    tree_prestamos = tb.Treeview(tree_frame, columns=("id","nombre","telefono","carrera","anio","libro","fecha_prestamo","fecha_devolucion"), show="headings", height=12)
    tree_prestamos.pack(fill="both", expand=True)
    headers = ["ID","Nombre","Teléfono","Carrera","Año","Libro","F. Préstamo","F. Devolución"]
    widths = [40,120,100,120,60,220,100,100]
    for c, h, w in zip(tree_prestamos["columns"], headers, widths):
        tree_prestamos.heading(c, text=h)
        tree_prestamos.column(c, width=w)
    tree_prestamos.tag_configure("oddrow", background="#2a343d")
    tree_prestamos.tag_configure("evenrow", background="#38444d")

    mostrar_prestamos()

    # Cuando cierran la ventana secundaria, limpiamos la referencia
    def on_close():
        global prestamos_win, combo_libros
        prestamos_win = None
        combo_libros = None
        prestamos_win_destroy()
    prestamos_win.protocol("WM_DELETE_WINDOW", lambda: (setattr_globals_on_close()))

def set_attr_when_close():
    # placeholder if needed
    pass

def setattr_globals_on_close():
    global prestamos_win, combo_libros
    try:
        prestamos_win.destroy()
    except Exception:
        pass
    prestamos_win = None
    combo_libros = None

def prestamos_win_destroy():
    global prestamos_win, combo_libros
    try:
        prestamos_win.destroy()
    except Exception:
        pass
    prestamos_win = None
    combo_libros = None

def guardar_prestamo():
    try:
        fecha_p = entry_fecha_prestamo.get_date().strftime("%Y-%m-%d")
        fecha_d = entry_fecha_devolucion.get_date().strftime("%Y-%m-%d")
    except Exception:
        # en caso de que no sea DateEntry por alguna razón
        fecha_p = entry_fecha_prestamo.get()
        fecha_d = entry_fecha_devolucion.get()

    datos = (
        entry_nombre.get().strip(),
        entry_tel.get().strip(),
        entry_carrera.get().strip(),
        entry_anio.get().strip(),
        combo_libros.get().strip(),
        fecha_p,
        fecha_d
    )
    if not all(datos):
        messagebox.showwarning("Atención", "Complete todos los campos del préstamo.")
        return
    cursor.execute("""
        INSERT INTO prestamos (nombre, telefono, carrera, anio_cursada, libro, fecha_prestamo, fecha_devolucion)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, datos)
    conn.commit()
    limpiar_prestamo()
    mostrar_prestamos()
    messagebox.showinfo("Registrado", "Préstamo registrado correctamente.")

def limpiar_prestamo():
    try:
        entry_nombre.delete(0, "end")
        entry_tel.delete(0, "end")
        entry_carrera.delete(0, "end")
        entry_anio.delete(0, "end")
        combo_libros.set("")
        entry_fecha_prestamo.set_date(datetime.now().date())
        entry_fecha_devolucion.set_date((datetime.now() + timedelta(days=7)).date())
    except Exception:
        pass

def mostrar_prestamos():
    # muestra solo no devueltos
    try:
        for r in tree_prestamos.get_children():
            tree_prestamos.delete(r)
    except Exception:
        pass
    cursor.execute("SELECT * FROM prestamos WHERE devuelto = 0")
    regs = cursor.fetchall()
    for i, r in enumerate(regs):
        tag = "evenrow" if i % 2 == 0 else "oddrow"
        try:
            tree_prestamos.insert("", "end", values=r, tags=(tag,))
        except Exception:
            pass

def marcar_devueltos():
    sel = tree_prestamos.selection()
    if not sel:
        messagebox.showinfo("Atención", "Seleccioná un préstamo para marcar como devuelto.")
        return
    vals = tree_prestamos.item(sel, "values")
    cursor.execute("UPDATE prestamos SET devuelto=1 WHERE id=?", (vals[0],))
    conn.commit()
    mostrar_prestamos()
    messagebox.showinfo("Devolución", "Préstamo marcado como devuelto.")

# -------------------------
# Verificaciones / Notificaciones
# -------------------------
def verificar_vencimientos_al_iniciar():
    # revisa préstamos no devueltos y muestra advertencias si corresponde
    cursor.execute("SELECT nombre, telefono, libro, fecha_devolucion FROM prestamos WHERE devuelto=0")
    regs = cursor.fetchall()
    avisos = []
    hoy = datetime.now().date()
    for r in regs:
        try:
            fd = datetime.strptime(r[3], "%Y-%m-%d").date()
        except Exception:
            # si formato distinto, ignoramos ese registro
            continue
        if fd < hoy:
            avisos.append(f"VENCIDO: {r[0]} - '{r[2]}' (venció {fd}) Tel: {r[1]}")
        elif (fd - hoy).days <= 2:
            avisos.append(f"Por vencer en {(fd-hoy).days} días: {r[0]} - '{r[2]}' (venc. {fd}) Tel: {r[1]}")
    if avisos:
        messagebox.showwarning("Préstamos a revisar", "\n".join(avisos))

# -------------------------
# Interfaz principal (libros) - ventana principal
# -------------------------
root = tb.Window(themename="superhero")
root.title("Sistema de Biblioteca - Libros")
root.geometry("1100x700")
root.resizable(True, True)

label_font = tkFont.Font(family="Helvetica", size=9)
entry_font = tkFont.Font(family="Helvetica", size=9)

main = tb.Frame(root, padding=8)
main.pack(fill="both", expand=True)
main.columnconfigure(0, weight=1)
main.columnconfigure(1, weight=0)

# Left frame: formulario y tabla de libros
frame_libros = tb.Labelframe(main, text="Gestión de Libros", padding=10, bootstyle="info")
frame_libros.grid(row=0, column=0, sticky="nsew", padx=(0,8), pady=6)

# Formulario de libro (grid)
tb.Label(frame_libros, text="N° Inv:").grid(row=0, column=0, sticky="w")
tb.Label(frame_libros, text="MFN:").grid(row=1, column=0, sticky="w")
tb.Label(frame_libros, text="Fecha (alta):").grid(row=2, column=0, sticky="w")
tb.Label(frame_libros, text="Título:").grid(row=3, column=0, sticky="w")
tb.Label(frame_libros, text="Autor:").grid(row=4, column=0, sticky="w")
tb.Label(frame_libros, text="Editorial:").grid(row=5, column=0, sticky="w")
tb.Label(frame_libros, text="Proc:").grid(row=6, column=0, sticky="w")
tb.Label(frame_libros, text="Observaciones:").grid(row=7, column=0, sticky="nw")

entry_inv = tb.Entry(frame_libros, font=entry_font)
entry_mfn = tb.Entry(frame_libros, font=entry_font)
# DateEntry para fecha de alta del libro
entry_fecha = tb.DateEntry(frame_libros, dateformat="%Y-%m-%d")
entry_titulo = tb.Entry(frame_libros, font=entry_font)
entry_autor = tb.Entry(frame_libros, font=entry_font)
entry_editorial = tb.Entry(frame_libros, font=entry_font)
entry_proc = tb.Entry(frame_libros, font=entry_font)
entry_obs = tb.Text(frame_libros, height=3, font=entry_font)

entry_inv.grid(row=0, column=1, sticky="ew", padx=6, pady=2)
entry_mfn.grid(row=1, column=1, sticky="ew", padx=6, pady=2)
entry_fecha.grid(row=2, column=1, sticky="ew", padx=6, pady=2)
entry_titulo.grid(row=3, column=1, sticky="ew", padx=6, pady=2)
entry_autor.grid(row=4, column=1, sticky="ew", padx=6, pady=2)
entry_editorial.grid(row=5, column=1, sticky="ew", padx=6, pady=2)
entry_proc.grid(row=6, column=1, sticky="ew", padx=6, pady=2)
entry_obs.grid(row=7, column=1, sticky="ew", padx=6, pady=2)

# Botones
btn_frame = tb.Frame(frame_libros)
btn_frame.grid(row=8, column=0, columnspan=2, pady=6)
tb.Button(btn_frame, text="Guardar libro", command=guardar_libro, bootstyle="success-outline").pack(side="left", padx=6)
tb.Button(btn_frame, text="Limpiar", command=limpiar_campos_libro, bootstyle="secondary-outline").pack(side="left", padx=6)
tb.Button(btn_frame, text="Eliminar libro", command=eliminar_libro, bootstyle="danger-outline").pack(side="left", padx=6)
tb.Button(btn_frame, text="Abrir préstamos", command=abrir_ventana_prestamos, bootstyle="info-outline").pack(side="left", padx=6)

# Buscador y orden
search_frame = tb.Frame(frame_libros)
search_frame.grid(row=9, column=0, columnspan=2, sticky="ew", pady=6)
tb.Label(search_frame, text="N° Inv:").grid(row=0, column=0)
entry_buscar_inv = tb.Entry(search_frame, width=12)
entry_buscar_inv.grid(row=0, column=1, padx=4)
tb.Label(search_frame, text="Fecha:").grid(row=0, column=2)
entry_buscar_fecha = tb.Entry(search_frame, width=12)
entry_buscar_fecha.grid(row=0, column=3, padx=4)
tb.Button(search_frame, text="Buscar", command=buscar_libros, bootstyle="info-outline").grid(row=0, column=4, padx=6)
tb.Label(search_frame, text="Orden:").grid(row=0, column=5)
combo_orden = tb.Combobox(search_frame, values=["Más reciente","Más viejo","Alfabético (Título)"], width=17)
combo_orden.grid(row=0, column=6, padx=4)
combo_orden.current(0)
tb.Button(search_frame, text="Aplicar", command=mostrar_todos_libros, bootstyle="secondary-outline").grid(row=0, column=7, padx=6)

# Tabla de libros
tree_libros = tb.Treeview(frame_libros, columns=("id","inv","mfn","fecha","titulo","autor","editorial","proc","obs"), show="headings", height=16)
tree_libros.grid(row=10, column=0, columnspan=2, sticky="nsew", pady=6)
frame_libros.rowconfigure(10, weight=1)
headers = ["ID","N°Inv","MFN","Fecha","Título","Autor","Editorial","Proc","Obs"]
widths = [40,70,70,90,220,140,120,80,160]
for c,h,w in zip(tree_libros["columns"], headers, widths):
    tree_libros.heading(c, text=h)
    tree_libros.column(c, width=w)
tree_libros.tag_configure("oddrow", background="#2a343d")
tree_libros.tag_configure("evenrow", background="#38444d")
tree_libros.bind("<<TreeviewSelect>>", cargar_a_formulario_libro)

# Right frame: breve info / ayuda
frame_info = tb.Labelframe(main, text="Accesos rápidos", padding=10, bootstyle="dark")
frame_info.grid(row=0, column=1, sticky="nsew", padx=(8,0), pady=6)
tb.Label(frame_info, text="• Botón 'Abrir préstamos'").pack(anchor="w", pady=2)
tb.Label(frame_info, text="• Use calendario para seleccionar fechas").pack(anchor="w", pady=2)
tb.Label(frame_info, text="• Fecha guardada en formato AAAA-MM-DD").pack(anchor="w", pady=2)

# Variables globales para la ventana de préstamos
prestamos_win = None
combo_libros = None
tree_prestamos = None
entry_nombre = entry_tel = entry_carrera = entry_anio = entry_fecha_prestamo = entry_fecha_devolucion = None

# -------------------------
# Inicio
# -------------------------
id_seleccionado = None
mostrar_todos_libros()
# Abrir la ventana de préstamos no por defecto; la abre la bibliotecaria con el botón.
# Pero comprobamos vencimientos al iniciar:
verificar_vencimientos_al_iniciar()

root.mainloop()