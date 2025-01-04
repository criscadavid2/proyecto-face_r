import tkinter as tk
from tkinter import ttk
from gestion_camaras.camaras import abrir_configuracion, probar_camara
from gestion_rostros.registros import registrar_rostro
from gestion_asistencia.asistencia import ver_asistencia
from reconocimiento import iniciar_hilo_reconocimiento, detener_reconocimiento
from utils import mostrar_login
from gestion_sesion.sesion import abrir_ventana_registro
import config
from gestion_usuarios.usuarios import registrar_nuevo_usuario


def configurar_estilo():
    """Configura el estilo de la interfaz."""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure('TButton', font=('Arial', 12), padding=10)
    style.configure('TLabel', font=('Arial', 12))

def crear_botones_sesion(ventana_principal, actualizar_estado_sesion_callback, acceder_funciones_super_admin):
    """"Crea y organiza los botones relacionados con la sesion."""
    estado_label = tk.Label(ventana_principal, text="Iniciar sesión", font=('Arial', 12))
    estado_label.pack(side="top", anchor="e", padx=20, pady=10)

    boton_perfil = ttk.Button(ventana_principal, text="Perfil", state=tk.DISABLED)
    boton_perfil.pack(side="top", anchor="e", padx=(0, 20), pady=10)

    #Botón de login/logout
    login_logout_btn = ttk.Button(
        ventana_principal,
        text="Iniciar sesión", #Texto inicial 
        command=lambda: (
            print("[Debug] Se hizo click en el boton de login/logout"),
            mostrar_login(
            ventana_principal,
            actualizar_estado_sesion_callback,
            acceder_funciones_super_admin
            ) 
        )
    )
    
    login_logout_btn.pack(side="top", anchor="e", padx=(0, 20), pady=10)

    return estado_label, boton_perfil, login_logout_btn



def agregar_pestanas(notebook, opcion_camara, ventana_principal):
    """"Crear y organiza las pestañas principales de la interfaz."""
    #Pestaña de reconocimiento
    frame_reconocimiento = ttk.Frame(notebook)
    notebook.add(frame_reconocimiento, text="Reconocimiento")

    ttk.Button(
        frame_reconocimiento,
        text="Iniciar Reconocimiento",
        command=lambda: iniciar_hilo_reconocimiento(int(opcion_camara.get().split()[-1]))
    ).grid(row=0, column=0, padx=20, pady=10)

    ttk.Button(
        frame_reconocimiento,
        text="Detener Reconocimiento",
        command=detener_reconocimiento
    ).grid(row=1, column=0, padx=20, pady=10)

    #Pestaña de registro
    frame_registro = ttk.Frame(notebook)
    notebook.add(frame_registro, text="Registro")

    ttk.Button(
        frame_registro,
        text="Registrar Nuevo Rostro",
        command=lambda: registrar_rostro(ventana_principal, opcion_camara)
    ).grid(row=0, column=0, padx=20, pady=10)

    ttk.Button(
        frame_registro,
        text="Registrar Nuevo Usuario",
        command=lambda: (
            print(f"[Debug] usuario_logueado_id: {config.usuario_logueado_id} al intentar abrir ventana de registro"),
            print(f"[Debug] usuario_logueado_nombre: {config.usuario_logueado_nombre} al intentar abrir ventana de registro"),
            abrir_ventana_registro(ventana_principal, config.usuario_logueado_id, config.usuario_logueado_nombre)
            if config.usuario_logueado_id and config.usuario_logueado_nombre else print("[Debug] Acceso denegado No hay usuario logueado")
        ),
            
    ).grid(row=1, column=0, padx=20, pady=10)
    
    #Pestaña de usuarios
    frame_usuarios = ttk.Frame(notebook)
    notebook.add(frame_usuarios, text="Usuarios")

    ttk.Button(
        frame_usuarios,
        text="ver usuarios",
        command=lambda: registrar_nuevo_usuario(ventana_principal)
    ).grid(row=0, column=0, padx=20, pady=10)


    #Pestaña de configuración
    frame_configuracion = ttk.Frame(notebook)
    notebook.add(frame_configuracion, text="Configuración")

    ttk.Button(
        frame_configuracion,
        text="Abrir Configuración",
        command=lambda: abrir_configuracion(ventana_principal, opcion_camara)
    ).grid(row=0, column=0, padx=20, pady=10)

    ttk.Button(
        frame_configuracion,
        text="Probar Cámara",
        command=lambda: probar_camara(int(opcion_camara.get().split()[-1]))
    ).grid(row=1, column=0, padx=20, pady=10)

    #Pestaña de asistencia
    frame_asistencia = ttk.Frame(notebook)
    notebook.add(frame_asistencia, text="Asistencia")

    ttk.Button(
        frame_asistencia,
        text="Ver Asistencia",
        command=ver_asistencia
    ).grid(row=0, column=0, padx=20, pady=10)


def crear_interfaz_principal(
    ventana_principal, actualizar_estado_sesion_callback, opcion_camara, acceder_funciones_super_admin):
    """Crea la interfaz principal de la aplicación."""
    configurar_estilo()

    #Crear botones de sesión
    estado_label, boton_perfil, login_logout_btn = crear_botones_sesion(
        ventana_principal, actualizar_estado_sesion_callback, acceder_funciones_super_admin
    )

    #Crear pestañas principales
    notebook = ttk.Notebook(ventana_principal)
    notebook.pack(expand=True, fill="both")
    agregar_pestanas(notebook, opcion_camara, ventana_principal)

    #Botón salir
    ttk.Button(
        ventana_principal,
        text="Salir",
        command=ventana_principal.quit
    ).pack(pady=10)

    return estado_label, boton_perfil, login_logout_btn