import ttkbootstrap as tb
import ui_libros as ul
import ui_prestamos as up

#Iniciamos el programa
root = tb.Window(themename="darkly")
ul.init(root)
up.init(root)
ul.construir_ventana_libros()
root.mainloop()