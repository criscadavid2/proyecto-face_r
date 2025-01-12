import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, Label, Canvas, Button
from gestion_camaras.camaras import abrir_configuracion, probar_camara
from gestion_rostros.registros import Camara, capturar_fotos
from gestion_asistencia.asistencia import ver_asistencia
from reconocimiento import iniciar_hilo_reconocimiento, detener_reconocimiento
from utils import mostrar_login, actualizar_frame, verificar_rostros
from gestion_sesion.sesion import abrir_ventana_registro
import config
from gestion_usuarios.usuarios import ventana_ver_usuarios
import os
import cv2
from PIL import Image, ImageTk

def configurar_estilo():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure('TButton', font=('Arial', 12), padding=10)
    style.configure('TLabel', font=('Arial', 12))

def crear_botones_sesion(ventana_principal, actualizar_estado_sesion_callback, acceder_funciones_super_admin):
    estado_label = tk.Label(ventana_principal, text="Iniciar sesión", font=('Arial', 12))
    estado_label.pack(side="top", anchor="e", padx=20, pady=10)

    boton_perfil = ttk.Button(ventana_principal, text="Perfil", state=tk.DISABLED)
    boton_perfil.pack(side="top", anchor="e", padx=(0, 20), pady=10)

    login_logout_btn = ttk.Button(
        ventana_principal,
        text="Iniciar sesión",
        command=lambda: mostrar_login(
            ventana_principal,
            actualizar_estado_sesion_callback,
            acceder_funciones_super_admin
        )
    )
    login_logout_btn.pack(side="top", anchor="e", padx=(0, 20), pady=10)

    return estado_label, boton_perfil, login_logout_btn

def ventana_registrar_rostro(ventana_principal, opcion_camara, id_usuario, ruta_carpeta_usuario):
    ventana_registrar_rostro = tk.Toplevel(ventana_principal)
    ventana_registrar_rostro.title("Registrar Rostro")

    # Establecer el tamaño mínimo de la ventana
    ventana_registrar_rostro.minsize(800, 600)
    
    # Configurar un diseño dinámico con `grid`
    ventana_registrar_rostro.rowconfigure(0, weight=1)  # Fila para etiqueta de estado
    ventana_registrar_rostro.rowconfigure(1, weight=10)  # Fila para canvas
    ventana_registrar_rostro.rowconfigure(2, weight=2)  # Fila para etiqueta de posición
    ventana_registrar_rostro.rowconfigure(3, weight=2)  # Fila para etiqueta de conteo
    ventana_registrar_rostro.rowconfigure(4, weight=1)  # Fila para botones
    ventana_registrar_rostro.columnconfigure(0, weight=1)  # Única columna, ocupa todo el ancho

    # Etiqueta de estado
    etiqueta_estado = Label(
        ventana_registrar_rostro,
        text="Estado: Preparando cámara...",
        font=("Arial", 12),
        fg="green"
    )
    etiqueta_estado.grid(row=0, column=0, pady=5, sticky="ew")  # Ocupa todo el ancho

    # Configuración de la cámara
    config.captura = Camara(int(opcion_camara.get().split()[-1])).captura
    if config.captura is None:
        ventana_registrar_rostro.destroy()
        return

    # Crear carpeta del usuario si no existe
    os.makedirs(ruta_carpeta_usuario, exist_ok=True)

    # Canvas para la cámara
    canvas = Canvas(ventana_registrar_rostro, width=640, height=480, bg="black")
    canvas.grid(row=1, column=0, padx=10, pady=10, sticky="n")

    # Frame para la etiqueta de posición
    frame_posicion = tk.Frame(ventana_registrar_rostro)
    frame_posicion.grid(row=2, column=0, sticky="ew", pady=5)

    frame_posicion.columnconfigure(0, weight=1)  # Asegurar que se ajuste al ancho completo

    etiqueta_posicion = Label(
        frame_posicion,
        text="Preparando captura...",
        font=("Arial", 12),
        fg="blue"
    )
    etiqueta_posicion.grid(row=0, column=0, padx=10, pady=5, sticky="ew")  # Coloca la etiqueta completa en el frame

    # Frame para la etiqueta de conteo
    frame_conteo = tk.Frame(ventana_registrar_rostro)
    frame_conteo.grid(row=3, column=0, sticky="ew", pady=5)

    frame_conteo.columnconfigure(0, weight=1)  # Ajuste dinámico del ancho

    etiqueta_conteo = Label(
        frame_conteo,
        text="",
        font=("Arial", 10),
        fg="orange"
    )
    etiqueta_conteo.grid(row=0, column=0, padx=10, pady=5, sticky="ew")  # Etiqueta centrada en el frame de conteo

    # Frame para los botones
    botones_frame = tk.Frame(ventana_registrar_rostro)
    botones_frame.grid(row=4, column=0, pady=10, sticky="ew")
    botones_frame.columnconfigure([0, 1, 2], weight=1)  # 3 columnas, una para cada botón

    # Función para reiniciar captura
    def reiniciar():
        etiqueta_posicion.config(text="Preparando captura...", fg="blue")
        etiqueta_conteo.config(text="")
        btn_capturar_fotos.config(state=tk.NORMAL, text="Capturar")

    # Botones
    btn_reiniciar = Button(botones_frame, text="Reiniciar", command=reiniciar)
    btn_reiniciar.grid(row=0, column=0, padx=5, sticky="ew")

    btn_capturar_fotos = Button(
        botones_frame,
        text="Capturar",
        state=tk.NORMAL,
        command=lambda: [
            btn_capturar_fotos.config(state=tk.DISABLED, text="Capturando..."),
            capturar_fotos(
                id_usuario,
                ruta_carpeta_usuario,
                ["frontal", "lateral izquierdo", "lateral derecho", "mirando arriba", "mirando abajo"],
                etiqueta_posicion,
                etiqueta_conteo,
                ventana_principal,
                lambda fotos, codificaciones: print("[Debug] Captura completada."),
                btn_capturar_fotos,
                btn_reiniciar
            )
        ]
    )
    btn_capturar_fotos.grid(row=0, column=1, padx=5, sticky="ew")

    def finalizar():
        if config.captura is not None:
            config.captura.release()
            config.captura = None
            print("[Debug] Cámara liberada.")
        ventana_registrar_rostro.destroy()

    btn_salir = Button(botones_frame, text="Salir", command=finalizar)
    btn_salir.grid(row=0, column=2, padx=5, sticky="ew")

    # Actualiza el frame con la cámara desde utils.py
    actualizar_frame(canvas, etiqueta_estado, verificar_rostros)

    # Asegurar que todo se redimensione correctamente
    ventana_registrar_rostro.update_idletasks()

def agregar_pestanas(notebook, opcion_camara, ventana_principal):
    def solicitar_id_y_capturar(ventana_principal, opcion_camara):
        id_usuario = simpledialog.askstring("ID del usuario", "Ingrese el ID del usuario a registrar")
        if not id_usuario:
            messagebox.showerror("Cancelado", "No se ingresó un ID de usuario.")
            return

        ruta_carpeta_usuario = os.path.join(
            "C:\\Users\\Chris\\Documents\\proyecto-face_r\\entrenamiento\\dataset",
            id_usuario,
            "registro_inicial"
        )
        os.makedirs(ruta_carpeta_usuario, exist_ok=True)

        ventana_registrar_rostro(
            ventana_principal,
            opcion_camara,
            id_usuario,
            ruta_carpeta_usuario
        )

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

    frame_registro = ttk.Frame(notebook)
    notebook.add(frame_registro, text="Registro")

    ttk.Button(
        frame_registro,
        text="Registrar Nuevo Rostro",
        command=lambda: solicitar_id_y_capturar(ventana_principal, opcion_camara)
    ).grid(row=0, column=0, padx=20, pady=10)

    ttk.Button(
        frame_registro,
        text="Registrar Nuevo Usuario",
        command=lambda: abrir_ventana_registro(ventana_principal, config.usuario_logueado_id, config.usuario_logueado_nombre)
        if config.usuario_logueado_id and config.usuario_logueado_nombre else print("[Debug] Acceso denegado No hay usuario logueado")
    ).grid(row=1, column=0, padx=20, pady=10)

    frame_usuarios = ttk.Frame(notebook)
    notebook.add(frame_usuarios, text="Usuarios")

    ttk.Button(
        frame_usuarios,
        text="Ver Usuarios",
        command=lambda: ventana_ver_usuarios(ventana_principal)
    ).grid(row=0, column=0, padx=20, pady=10)

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

    frame_asistencia = ttk.Frame(notebook)
    notebook.add(frame_asistencia, text="Asistencia")

    ttk.Button(
        frame_asistencia,
        text="Ver Asistencia",
        command=ver_asistencia
    ).grid(row=0, column=0, padx=20, pady=10)

def crear_interfaz_principal(ventana_principal, actualizar_estado_sesion_callback, opcion_camara, acceder_funciones_super_admin):
    configurar_estilo()

    estado_label, boton_perfil, login_logout_btn = crear_botones_sesion(
        ventana_principal, actualizar_estado_sesion_callback, acceder_funciones_super_admin
    )

    notebook = ttk.Notebook(ventana_principal)
    notebook.pack(expand=True, fill="both")
    agregar_pestanas(notebook, opcion_camara, ventana_principal)

    ttk.Button(
        ventana_principal,
        text="Salir",
        command=ventana_principal.quit
    ).pack(pady=10)

    return estado_label, boton_perfil, login_logout_btn
