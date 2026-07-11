"""
ui_libros.py
Ventana principal de gestión de libros: widgets, callbacks de botones e interfaz.
"""
import ttkbootstrap as tb
from tkinter import messagebox, filedialog
from tkinter import font as tkFont
from datetime import datetime
import logica_libros as ll
import logica_prestamos as lp
import ui_prestamos as up

root = None

def init(ventana_root):
    """Main.py llama a esto una vez, al iniciar, para darle a este módulo la ventana principal."""
    global root
    root = ventana_root

# -------------------------
# Funciones - Libros
# -------------------------


def mostrar_todos_libros():
    for row in tree_libros.get_children():
        tree_libros.delete(row)
        
    orden = combo_orden.get()
    regs = ll.mostrar_todos_libros_db(orden)
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
    ll.insertar_libro_db(datos)       #llama a logica_libros para agregar libro
    limpiar_campos_libro()
    mostrar_todos_libros()
    up.refrescar_combo_libros()

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
    
    regs = ll.buscar_libro_db(filtro_inv, filtro_fecha)
    
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
    if messagebox.askyesno("Confirmar", f"¿Eliminar '{vals[4]}'?"): #aca llamo a logica_libros para eliminar el libro
        ll.eliminar_libro_db(idb)
        mostrar_todos_libros()
        up.refrescar_combo_libros()
        limpiar_campos_libro()

def importar_csv_libros():
    """Importa libros desde un archivo .CSV a la base de datos."""
    ruta = filedialog.askopenfilename(
        title="Seleccionar archivo CSV",
        filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
    )
    if not ruta:
        return
#aca la ui es la encargada de mostrar el error si el archivo no se puede leer
    try:
        insertados, errores = ll.importar_csv_libros_db(ruta)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")
        return

    mostrar_todos_libros()
    up.refrescar_combo_libros()
    messagebox.showinfo("Importación finalizada", f"Libros importados: {insertados}\nFilas con error/omitidas: {errores}")

# -------------------------
# Verificaciones / Notificaciones
# -------------------------
def verificar_vencimientos_al_iniciar():
    # revisa préstamos no devueltos y muestra advertencias si corresponde
    regs = lp.verificar_vencimientos_db() 
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

def construir_ventana_libros():
    """Arma todos los widgets de la ventana principal de libros. Se llama una vez desde main.py."""
    global entry_inv, entry_mfn, entry_fecha, entry_titulo, entry_autor, entry_editorial, entry_proc, entry_obs, tree_libros, combo_orden, entry_buscar_inv, entry_buscar_fecha, id_seleccionado
    root.title("Sistema de Biblioteca - Libros")
    root.geometry("1280x720")
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
    tb.Button(btn_frame, text="Abrir préstamos", command=up.abrir_ventana_prestamos, bootstyle="info-outline").pack(side="left", padx=6)
    tb.Button(btn_frame, text="Ver historial", command=up.ver_historial_prestamos, bootstyle="info-outline").pack(side="left", padx=6)
    tb.Button(btn_frame, text="Ver préstamos caducados", command=up.ver_prestamos_caducados, bootstyle="danger-outline").pack(side="left", padx=6)
    tb.Button(btn_frame, text="Importar base de datos .CSV", command=importar_csv_libros, bootstyle="warning-outline").pack(side="left", padx=6)

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

    # -------------------------
    # Inicio
    # -------------------------
    id_seleccionado = None
    mostrar_todos_libros()
    # Abrir la ventana de préstamos no por defecto; la abre la bibliotecaria con el botón.
    # Pero comprobamos vencimientos al iniciar:
    verificar_vencimientos_al_iniciar()

