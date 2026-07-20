import os
import ttkbootstrap as tb
import ui_libros as ul
import ui_prestamos as up

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  #__file__ llena automáticamente con la ruta del archivo actual
ICONO = os.path.join(BASE_DIR, "icono.ico")

#Iniciamos el programa
root = tb.Window(themename="darkly")
root.iconbitmap(ICONO)
ul.init(root)
up.init(root, ICONO)
ul.construir_ventana_libros()
root.mainloop()