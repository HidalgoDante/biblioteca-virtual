"""
ui_prestamos.py
Ventana de préstamos: widgets, callbacks de botones, y todo lo relacionado a la interfaz de préstamos.
"""
import ttkbootstrap as tb
from tkinter import messagebox
from datetime import datetime, timedelta
import logica_prestamos as lp
import logica_libros as ll

# Referencia a la ventana principal, la completa main.py al arrancar
root = None
icono = None

def init(ventana_root, ruta_icono = None):
    """Main.py llama a esto una vez, al iniciar, para darle a este módulo la ventana principal."""
    global root, icono
    root = ventana_root
    icono = ruta_icono

# Variables globales de esta ventana (se completan cuando se abre)
prestamos_win = None
combo_libros = None
tree_prestamos = None
entry_nombre = entry_tel = entry_carrera = entry_anio = entry_fecha_prestamo = entry_fecha_devolucion = None
id_prestamo_editar = None

# -------------------------
# Funciones - Préstamos (ventana secundaria)
# -------------------------

def abrir_ventana_prestamos():
    """Abre (o trae al frente) la ventana de préstamos."""
    global prestamos_win, combo_libros, icono
    if prestamos_win is not None and prestamos_win.winfo_exists():
        prestamos_win.lift()
        return

    prestamos_win = tb.Toplevel(root)
    prestamos_win.iconbitmap(icono)
    prestamos_win.title("Sistema de Préstamos")
    prestamos_win.geometry("1100x600")
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
    combo_libros = tb.Combobox(frame, values=ll.actualizar_lista_libros_combo_db(), width=55)
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
    btn_frame_prestamos = tb.Frame(frame)
    btn_frame_prestamos.grid(row=4, column=0, columnspan=4, pady=8)
    tb.Button(btn_frame_prestamos, text="Registrar préstamo", command=guardar_prestamo, bootstyle="success-outline").pack(side="left", padx=4)
    tb.Button(btn_frame_prestamos, text="Editar préstamo", command=editar_prestamo, bootstyle="info-outline").pack(side="left", padx=4)
    tb.Button(btn_frame_prestamos, text="Guardar cambios", command=guardar_cambios_prestamo, bootstyle="secondary-outline").pack(side="left", padx=4)
    tb.Button(btn_frame_prestamos, text="Eliminar préstamo", command=eliminar_prestamo, bootstyle="danger-outline").pack(side="left", padx=4)
    tb.Button(btn_frame_prestamos, text="Marcar devuelto", command=marcar_devueltos, bootstyle="warning-outline").pack(side="left", padx=4)
    tb.Button(btn_frame_prestamos, text="Limpiar", command=limpiar_prestamo, bootstyle="secondary-outline").pack(side="left", padx=4)
    tb.Button(btn_frame_prestamos, text="Actualizar lista libros", command=lambda: combo_libros.configure(values=ll.actualizar_lista_libros_combo_db()), bootstyle="info-outline").pack(side="left", padx=4)
    tb.Button(btn_frame_prestamos, text="Ver historial", command=ver_historial_prestamos, bootstyle="info-outline").pack(side="left", padx=4)
    tb.Button(btn_frame_prestamos, text="Ver caducados", command=ver_prestamos_caducados, bootstyle="danger-outline").pack(side="left", padx=4)

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
    prestamos_win.protocol("WM_DELETE_WINDOW", setattr_globals_on_close)    


def setattr_globals_on_close():
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
    lp.guardar_prestamo_db(datos)
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
    
    regs = lp.prestamos_activos_db()

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
    lp.marcar_devuelto_db(vals[0]) #llamo a el primer item, osea id
    mostrar_prestamos()
    messagebox.showinfo("Devolución", "Préstamo marcado como devuelto.")

def editar_prestamo():
    """Carga el préstamo seleccionado en el formulario para poder editarlo."""
    global id_prestamo_editar
    sel = tree_prestamos.selection()
    if not sel:
        messagebox.showinfo("Atención", "Seleccioná un préstamo para editar.")
        return
    vals = tree_prestamos.item(sel, "values")
    # vals: id, nombre, telefono, carrera, anio, libro, fecha_prestamo, fecha_devolucion
    entry_nombre.delete(0, "end"); entry_nombre.insert(0, vals[1])
    entry_tel.delete(0, "end"); entry_tel.insert(0, vals[2])
    entry_carrera.delete(0, "end"); entry_carrera.insert(0, vals[3])
    entry_anio.delete(0, "end"); entry_anio.insert(0, vals[4])
    combo_libros.set(vals[5])
    try:
        entry_fecha_prestamo.set_date(datetime.strptime(vals[6], "%Y-%m-%d").date())
        entry_fecha_devolucion.set_date(datetime.strptime(vals[7], "%Y-%m-%d").date())
    except Exception:
        pass
    id_prestamo_editar = vals[0]   #la funcion completa es todo ui, no toca la base de datos

def guardar_cambios_prestamo():

    """Guarda los cambios hechos sobre un préstamo cargado con 'Editar préstamo'."""
    
    global id_prestamo_editar
    if not id_prestamo_editar:
        messagebox.showwarning("Atención", "Primero seleccioná un préstamo y presioná 'Editar préstamo'.")
        return
    try:
        fecha_p = entry_fecha_prestamo.get_date().strftime("%Y-%m-%d")
        fecha_d = entry_fecha_devolucion.get_date().strftime("%Y-%m-%d")
    except Exception:
        fecha_p = entry_fecha_prestamo.get()
        fecha_d = entry_fecha_devolucion.get()

    datos = (
        entry_nombre.get().strip(),
        entry_tel.get().strip(),
        entry_carrera.get().strip(),
        entry_anio.get().strip(),
        combo_libros.get().strip(),
        fecha_p,
        fecha_d,
        id_prestamo_editar
    )
    if not all(datos[:-1]):
        messagebox.showwarning("Atención", "Complete todos los campos del préstamo.")
        return
    lp.guardar_cambios_prestamo_db(datos) 
    id_prestamo_editar = None
    limpiar_prestamo()
    mostrar_prestamos()
    messagebox.showinfo("Actualizado", "Préstamo actualizado correctamente.")

def eliminar_prestamo():
    """Elimina el préstamo seleccionado."""
    global id_prestamo_editar
    sel = tree_prestamos.selection()
    if not sel:
        messagebox.showwarning("Atención", "Seleccioná un préstamo para eliminar.")
        return
    vals = tree_prestamos.item(sel, "values")
    if messagebox.askyesno("Confirmar", f"¿Eliminar el préstamo de '{vals[1]}' ({vals[5]})?"):
        lp.eliminar_prestamo_db(vals[0])
        id_prestamo_editar = None
        mostrar_prestamos()
        limpiar_prestamo()

def _abrir_ventana_lista_prestamos(titulo, regs):
    """Abre una ventana genérica de solo lectura con una lista de préstamos ya traída (regs)."""
    global icono
    win = tb.Toplevel(root)
    win.iconbitmap(icono)
    win.title(titulo)
    win.geometry("820x420")
    win.transient(root)

    frame = tb.Frame(win, padding=8)
    frame.pack(fill="both", expand=True)

    cols = ("id", "nombre", "telefono", "carrera", "anio", "libro", "fecha_prestamo", "fecha_devolucion", "estado")
    tree = tb.Treeview(frame, columns=cols, show="headings", height=16)
    tree.pack(fill="both", expand=True)
    headers = ["ID", "Nombre", "Teléfono", "Carrera", "Año", "Libro", "F. Préstamo", "F. Devolución", "Estado"]
    widths = [40, 120, 100, 110, 50, 200, 90, 90, 90]
    for c, h, w in zip(cols, headers, widths):
        tree.heading(c, text=h)
        tree.column(c, width=w)
    tree.tag_configure("oddrow", background="#2a343d")
    tree.tag_configure("evenrow", background="#38444d")

    hoy = datetime.now().date()
    for i, r in enumerate(regs):
        estado = "Devuelto" if r[8] == 1 else "Activo"
        try:
            fd = datetime.strptime(r[7], "%Y-%m-%d").date()
            if r[8] == 0 and fd < hoy:
                estado = "Vencido"
        except Exception:
            pass
        tag = "evenrow" if i % 2 == 0 else "oddrow"
        tree.insert("", "end", values=(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], estado), tags=(tag,))

    if not regs:
        tb.Label(frame, text="No hay registros para mostrar.").pack(pady=10)

def refrescar_combo_libros():
    global prestamos_win, combo_libros
    if prestamos_win is not None and combo_libros is not None:
        combo_libros['values'] = ll.actualizar_lista_libros_combo_db()


def ver_historial_prestamos():
    regs = lp.historial_prestamos_db()
    _abrir_ventana_lista_prestamos("Historial de préstamos", regs)

def ver_prestamos_caducados():
    regs = lp.prestamos_caducados_db()
    _abrir_ventana_lista_prestamos("Préstamos caducados", regs)