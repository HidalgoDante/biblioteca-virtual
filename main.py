import os
import sys
import ttkbootstrap as tb
import ui_libros as ul
import ui_prestamos as up
from tkinter import messagebox

def ruta_recurso(nombre_archivo):
    """Devuelve la ruta correcta al recurso, tanto si el programa corre como script
    como si corre empaquetado con PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, nombre_archivo)

ICONO = ruta_recurso("icono.ico")

#Iniciamos el programa
root = tb.Window(themename="darkly")
messagebox.showinfo("Debug", f"Buscando ícono en:\n{ICONO}\n¿Existe? {os.path.exists(ICONO)}")
root.iconbitmap(ICONO)
ul.init(root)
up.init(root, ICONO)
ul.construir_ventana_libros()
root.mainloop()