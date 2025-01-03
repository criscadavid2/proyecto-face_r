# gestion_sesion/estado_sesion.py
import tkinter as tk
from utils import mostrar_login, cerrar_sesion, verificar_login
from gestion_super_admin.super_admin import acceder_funciones_super_admin
import config #Importa el archivo config.py

#Estado sesion
def actualizar_estado_sesion(usuario_id, nombre_usuario, estado_label, boton_perfil, login_logout_btn, ventana_principal):  
    
    config.usuario_logueado_id = usuario_id
    config.usuario_logueado_nombre = nombre_usuario

    print(f"[Debug] Actualizando estado de sesión: {config.usuario_logueado_id}, {config.usuario_logueado_nombre}")
    
    #Verifica permisos y abre la ventana de registro
    
    if usuario_id:  # Si hay un usuario logueado
        estado_label.config(text=f"Usuario: {nombre_usuario}")
        boton_perfil.config(state=tk.NORMAL)  # Habilita el botón de perfil
        login_logout_btn.config(
            text="Cerrar sesión",
            command=lambda: cerrar_sesion(estado_label, boton_perfil, login_logout_btn, ventana_principal, actualizar_estado_sesion)
        )
        print(f"[Debug] Estado sesion actualizado: {estado_label.cget('text')}")
    else:  # Si no hay usuario logueado
        estado_label.config(text="Iniciar sesión")
        boton_perfil.config(state=tk.DISABLED)  # Deshabilita el botón si no hay usuario
        login_logout_btn.config(
            text="Iniciar sesión",
            command=lambda: mostrar_login(
                ventana_principal,
                actualizar_estado_sesion,
                acceder_funciones_super_admin
            )
        )
"""--------------------------------------------------------------------------------"""
