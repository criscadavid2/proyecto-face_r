import cv2
import face_recognition
import os
from datetime import datetime
import tkinter as tk
from tkinter import Toplevel, Button, Canvas, Label
from PIL import Image, ImageTk
import config
from utils import guardar_codificacion_rostro

TIEMPO_ESPERA = 6  # Tiempo total de cuenta regresiva (segundos)

# Clase para manejar la cámara
class Camara:
    def __init__(self, indice_camara):
        self.captura = None
        self.iniciar(indice_camara)

    def iniciar(self, indice_camara):
        try:
            self.captura = cv2.VideoCapture(indice_camara)
            if not self.captura.isOpened():
                raise RuntimeError(f"No se pudo acceder a la cámara en el índice {indice_camara}.")
        except Exception as e:
            print(f"[Debug] Error al iniciar la cámara: {e}")
            self.captura = None

    def detener(self):
        try:
            if self.captura is not None:
                self.captura.release()
                print("[Debug] Cámara liberada correctamente.")
            self.captura = None
        except Exception as e:
            print(f"[Debug] Error al liberar la cámara: {e}")

def verificar_rostros(frame, etiqueta_posicion):
    """Verifica la cantidad de rostros detectados en un frame y actualiza la etiqueta."""
    try:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ubicaciones_rostros = face_recognition.face_locations(frame_rgb)

        if len(ubicaciones_rostros) == 0:
            etiqueta_posicion.config(text="No se detectó ningún rostro. Intente de nuevo.", fg="red")
        elif len(ubicaciones_rostros) > 1:
            etiqueta_posicion.config(text="Se detectaron múltiples rostros. Asegúrese de estar solo en el cuadro.", fg="red")
        else:
            etiqueta_posicion.config(text="Rostro detectado correctamente.", fg="green")
        
        return ubicaciones_rostros
    except Exception as e:
        if etiqueta_posicion.winfo_exists():
            etiqueta_posicion.config(text=f"Error al detectar rostros: {e}", fg="red")
        print(f"[Debug] Error en verificar_rostros: {e}")
        return []

# Función genérica para manejar la captura de una foto
def capturar_y_procesar_foto(ruta_carpeta_usuario, id_usuario, posicion, etiqueta_posicion, etiqueta_conteo, ventana_principal, callback, boton_capturar, boton_reiniciar, tiempo_espera=TIEMPO_ESPERA):
    contador_segundos = tiempo_espera
    captura_activa = True #Variable para controlar si la captura está activa

    def realizar_conteo():
        nonlocal contador_segundos, captura_activa

        if not captura_activa:
            etiqueta_conteo.config(text="")
            return

        etiqueta_posicion.config(text=f"Preparando captura para posición {posicion}", fg="blue")
        ventana_principal.update_idletasks()

        if contador_segundos > 0:
            etiqueta_conteo.config(text=f"Tiempo restante: {contador_segundos} segundos", fg="orange")
            contador_segundos -= 1
            ventana_principal.after(1000, realizar_conteo)
        else:
            ret, frame = config.captura.read()
            if not ret:
                etiqueta_posicion.config(text="Error: No se pudo leer el frame de la cámara", fg="red")
                #Habilitar solo en caso de emergencia
                boton_capturar.config(state=tk.NORMAL, text="Capturar")
                return

            ubicaciones_rostros = verificar_rostros(frame, etiqueta_posicion)
            if len(ubicaciones_rostros) != 1:
                ventana_principal.after(2000, realizar_conteo)
                return

            fecha_hora_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"{id_usuario}_{posicion}_{fecha_hora_actual}.jpg"
            ruta_archivo = os.path.join(ruta_carpeta_usuario, nombre_archivo)

            try:
                cv2.imwrite(ruta_archivo, frame)
                etiqueta_posicion.config(text=f"Foto {posicion} guardada exitosamente.", fg="green")
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                codificacion = face_recognition.face_encodings(frame_rgb, ubicaciones_rostros)[0]
                ventana_principal.after(2000, lambda: callback(ruta_archivo, codificacion))
                
            except Exception as e:
                etiqueta_posicion.config(text=f"Error al guardar la foto: {e}", fg="red")
                boton_capturar.config(state=tk.NORMAL, text="Capturar")
                
    def reiniciar_captura():
        nonlocal captura_activa
        captura_activa = False
        etiqueta_posicion.config(text="Captura de fotos cancelada. Presione capturar para iniciar de nuevo ", fg="blue")
        etiqueta_conteo.config(text="")
        boton_capturar.config(state=tk.NORMAL, text="Capturar")
        realizar_conteo()


    boton_reiniciar.config(command=reiniciar_captura)
    realizar_conteo()

# Funciones auxiliares
def capturar_fotos(id_usuario, ruta_carpeta_usuario, posiciones, etiqueta_posicion, etiqueta_conteo, ventana_principal, callback, boton_capturar, boton_reiniciar):
    fotos_tomadas = []
    codificaciones = []

    def procesar_foto(ruta_archivo, codificacion):
        fotos_tomadas.append(ruta_archivo)
        codificaciones.append(codificacion)

        if len(fotos_tomadas) < len(posiciones):
            siguiente_posicion = posiciones[len(fotos_tomadas)]
            capturar_y_procesar_foto(
                ruta_carpeta_usuario,
                id_usuario,
                siguiente_posicion,
                etiqueta_posicion,
                etiqueta_conteo,
                ventana_principal,
                procesar_foto,
                boton_capturar,
                boton_reiniciar)
        else:
            etiqueta_posicion.config(text="Captura de fotos completada.", fg="green")
            etiqueta_conteo.config(text="")
            
            # Llamar a la pregunta de si usa lentes
            preguntar_usa_lentes(
                ventana_principal,
                id_usuario,
                ruta_carpeta_usuario,
                fotos_tomadas,
                codificaciones,
                etiqueta_posicion,
                etiqueta_conteo,
                callback_final,
                boton_capturar,
                boton_reiniciar)

    def callback_final(fotos_tomadas, codificaciones_finales):
        """Callback que se ejecuta al finalizar la captura de fotos incluyendo lentes."""
        etiqueta_posicion.config(text="Proceso de captura finalizado.", fg="blue")
        boton_capturar.config(state=tk.NORMAL, text="Capturar")
        callback(fotos_tomadas, codificaciones_finales)
        

    capturar_y_procesar_foto(
        ruta_carpeta_usuario,
        id_usuario,
        posiciones[0],
        etiqueta_posicion,
        etiqueta_conteo,
        ventana_principal,
        procesar_foto,
        boton_capturar,
        boton_reiniciar
    )

#Ventana modal para preguuntar si usa lentes
def preguntar_usa_lentes(
        ventana_principal,
        id_usuario,
        ruta_carpeta_usuario,
        fotos_tomadas,
        codificaciones,
        etiqueta_posicion,
        etiqueta_conteo,
        callback,
        boton_capturar,
        boton_reiniciar
    ):
    
    ventana_lentes = Toplevel(ventana_principal)
    ventana_lentes.title("Uso de lentes")
    ventana_lentes.geometry("400x200")
    ventana_lentes.grab_set()

    Label(ventana_lentes, text="¿Usa lentes?", font=("Arial", 14), pady=20).pack()
    botones_frame = tk.Frame(ventana_lentes)
    botones_frame.pack(pady=20)

    def capturar_con_lentes():
        ventana_lentes.destroy()
        capturar_y_procesar_foto(
            ruta_carpeta_usuario,
            id_usuario,
            "con lentes",
            etiqueta_posicion,
            etiqueta_conteo,
            ventana_principal,
            lambda ruta, cod: callback(fotos_tomadas + [ruta], codificaciones + [cod]),
            boton_capturar,
            boton_reiniciar,
        )

    
    def finalizar_sin_lentes():
        ventana_lentes.destroy()
        boton_capturar.config(state=tk.NORMAL, text="Capturar")
        callback(fotos_tomadas, codificaciones)

    Button(botones_frame, text="si", command=capturar_con_lentes, width=10, bg="green", fg="white").pack(side=tk.LEFT, padx=5)
    Button(botones_frame, text="no", command=finalizar_sin_lentes, width=10, bg="red", fg="white").pack(side=tk.RIGHT, padx=5)

# Guardar en base de datos
def guardar_en_bd(fotos_tomadas, codificaciones, etiqueta_posicion):
    if codificaciones:
        promedio_codificacion = [
            sum(cod[i] for cod in codificaciones) / len(codificaciones)
            for i in range(len(codificaciones[0]))
        ]
        guardar_codificacion_rostro(promedio_codificacion)
        etiqueta_posicion.config(text="Rostro registrado exitosamente.", fg="green")
