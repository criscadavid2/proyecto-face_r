import tkinter as tk
from tkinter import messagebox, StringVar, OptionMenu, ttk
import cv2

from gestion_rostros.registros import registrar_rostro
from gestion_super_admin.super_admin import acceder_funciones_super_admin
from gestion_camaras.camaras import inicializar_camaras, verificar_camara_predeterminada, abrir_configuracion, probar_camara, nombres_camaras
from gestion_sesion.estado_sesion import actualizar_estado_sesion
from utils import mostrar_login, cerrar_sesion
from gestion_asistencia.asistencia import ver_asistencia
from gestion_interfaz.interfaz import crear_interfaz_principal
import config

# Inicializar las cámaras al inicio
inicializar_camaras()

if not nombres_camaras or nombres_camaras[0] == "No disponible":
    messagebox.showerror("Error", "No hay cámaras disponibles para el reconocimiento facial.")
    exit()


# Función para actualizar el estado de la sesión (callback)
def actualizar_estado_sesion_callback(usuario_id, nombre_usuario):
    """Actualiza el estado de la sesión y refleja los cambios en la interfaz."""
    config.usuario_logueado_id = usuario_id
    config.usuario_logueado_nombre = nombre_usuario
    
    actualizar_estado_sesion(
        config.usuario_logueado_id, 
        config.usuario_logueado_nombre, 
        estado_label, 
        boton_perfil, 
        login_logout_btn, 
        ventana_principal
    )
    print(f"[Debug actualizar_callback] Estado Sesion - usuario_logueado {config.usuario_logueado_id}, usuario_logueado_nombre {config.usuario_logueado_nombre}")

# Crear ventana principal
ventana_principal = tk.Tk()
ventana_principal.title("Sistema de Reconocimiento Facial")
ventana_principal.geometry("700x500")  # Tamaño de ventana más amplio

# Variable global para la cámara seleccionada
opcion_camara = StringVar(value="Cámara 0")  # Valor predeterminado

# Crear interfaz principal usando `crear_interfaz_principal`
estado_label, boton_perfil, login_logout_btn = crear_interfaz_principal(
    ventana_principal, actualizar_estado_sesion_callback, opcion_camara, acceder_funciones_super_admin
)

# Iniciar loop de la ventana
ventana_principal.mainloop()
