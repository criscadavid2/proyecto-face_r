import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Función para mostrar los datos de la base de datos
def mostrar_usuarios():
    try:
        # Conectar a la base de datos usuarios.db
        conn = sqlite3.connect('gestion_usuarios/usuarios.db')
        cursor = conn.cursor()

        # Ejecutar la consulta para obtener todos los usuarios
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()

        # Crear ventana para mostrar los resultados
        ventana_resultados = tk.Tk()
        ventana_resultados.title("Datos de Usuarios")
        ventana_resultados.geometry("900x400")  # Ajusta el tamaño de la ventana

        # Crear un Treeview para mostrar los datos en una tabla
        treeview = ttk.Treeview(
            ventana_resultados,
            columns=("ID", "Nombre Usuario", "Apellido Usuario", "Contraseña", "Correo", "Rol ID", "Fecha Registro", "Grupo Usuario", "Último Acceso", "Número Usuario", "Codificación Rostro"),
            show="headings"
        )
        
        # Definir las columnas
        treeview.heading("ID", text="ID")
        treeview.heading("Nombre Usuario", text="Nombre Usuario")
        treeview.heading("Apellido Usuario", text="Apellido Usuario")
        treeview.heading("Contraseña", text="Contraseña")
        treeview.heading("Correo", text="Correo")
        treeview.heading("Rol ID", text="Rol ID")
        treeview.heading("Fecha Registro", text="Fecha Registro")
        treeview.heading("Grupo Usuario", text="Grupo Usuario")
        treeview.heading("Último Acceso", text="Último Acceso")
        treeview.heading("Número Usuario", text="Número Usuario")
        treeview.heading("Codificación Rostro", text="Codificación Rostro")
        
        # Insertar los datos de los usuarios en el Treeview
        for usuario in usuarios:
            treeview.insert("", "end", values=usuario)

        # Mostrar el Treeview en la ventana
        treeview.pack(expand=True, fill="both")

        # Botón para cerrar la ventana
        boton_cerrar = tk.Button(ventana_resultados, text="Cerrar", command=ventana_resultados.quit)
        boton_cerrar.pack()

        # Iniciar el loop de la ventana
        ventana_resultados.mainloop()

    except sqlite3.Error as e:
        messagebox.showerror("Error de base de datos", f"Error al conectar con la base de datos: {e}")
    finally:
        if conn:
            conn.close()

# Llamar a la función para mostrar los usuarios
mostrar_usuarios()
