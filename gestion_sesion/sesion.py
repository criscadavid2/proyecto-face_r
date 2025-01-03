import tkinter as tk
from tkinter import messagebox, ttk
import bcrypt

from gestion_usuarios.roles import es_administrador
from gestion_usuarios.usuarios import registrar_nuevo_usuario
import config


# Llamar a mostrar_login desde tu código principal
# mostrar_login(ventana, actualizar_estado_sesion_callback)

#Funcion para abrir ventana de registro - solo admins
def abrir_ventana_registro(ventana_principal, usuario_id, nombre_usuario):
    
    """
    Abre la ventana de registro de usuarios.
    
    """
    #Debugging de los valores recibidos
    print(f"[Debug] Usuario logueado ID al intentar abrir ventana de registro: {usuario_id}")
    print(f"[Debug] Usuario logueado Nombre al intentar abrir ventana de registro: {nombre_usuario}")
    
    """Verificar si hay un usuario logueado."""
    if not usuario_id or not nombre_usuario:
        print("[Debug] Acceso denegado No hay usuario logueado")
        messagebox.showerror("Acceso denegado", "Inicie sesión para registrar nuevos usuarios.")
        return
        
    if usuario_id == "Super Admin" or es_administrador(usuario_id):
        print(f"[Debug] valor usuario_logueado_id {usuario_id}")
        print("[Debug] Acceso permitido a la ventana de registro")
        registrar_nuevo_usuario(ventana_principal) #Aqui llamamos a la funcion registrar_nuevo_usuario 
    else:
        print("[Debug] Acceso denegado el usuario no es administrador")
        messagebox.showerror("Acceso denegado", "Solo los administradores pueden registrar nuevos usuarios.")
    