import cv2
import face_recognition
import os
import threading
from datetime import datetime
import tkinter as tk
from tkinter import Toplevel, Button, Canvas, Label
from PIL import Image, ImageTk
import time
from utils import guardar_codificacion_rostro
import config

TIEMPO_ESPERA = 6  # Tiempo total de cuenta regresiva (segundos)


# Clase para reproducir el sonido en un hilo separado
class AudioThread(threading.Thread):
    def __init__(self, ruta_audio):
        super().__init__()
        self.ruta_audio = ruta_audio
        self.finalizado = threading.Event()

    def run(self):
        try:
            import simpleaudio as sa
            wave_obj = sa.WaveObject.from_wave_file(self.ruta_audio)
            play_obj = wave_obj.play()
            play_obj.wait_done()
        except Exception as e:
            print(f"[Debug] Error al reproducir el sonido: {e}")
        finally:
            self.finalizado.set()  # Marcar que el audio ha terminado


# Clase para manejar la cámara
class Camara:
    def __init__(self, indice_camara):
        self.captura = None
        self.iniciar(indice_camara)

    def iniciar(self, indice_camara):
        try:
            self.captura = cv2.VideoCapture(indice_camara)
            if not self.captura.isOpened():
                raise RuntimeError("No se pudo acceder a la cámara.")
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


# Función para capturar fotos con el flujo completo
def capturar_fotos(id_usuario, ruta_carpeta_usuario, posiciones, etiqueta_posicion, etiqueta_conteo, ventana_principal, callback):
    fotos_tomadas = []
    codificaciones = []
    contador_posicion = 0
    contador_segundos = TIEMPO_ESPERA  # Contador para los segundos de espera

    def capturar_foto():
        nonlocal contador_posicion, contador_segundos

        if contador_posicion >= len(posiciones):
            etiqueta_posicion.config(text="Captura de fotos completada.", fg="green")
            etiqueta_conteo.config(text="")
            callback(fotos_tomadas, codificaciones)  # Llamar al callback cuando se completen todas las fotos
            return

        # Mostrar posición actual
        posicion = posiciones[contador_posicion]
        etiqueta_posicion.config(text=f"Coloque su rostro en la posición: {posicion}", fg="blue")
        ventana_principal.update_idletasks()

        # Actualizar el conteo regresivo
        etiqueta_conteo.config(text=f"Tiempo restante: {contador_segundos} segundos", fg="orange")
        if contador_segundos > 0:
            contador_segundos -= 1
            ventana_principal.after(1000, capturar_foto)
        else:
            # Capturar la foto
            ret, frame = config.captura.read()
            if not ret:
                etiqueta_posicion.config(text="Error: No se pudo leer el frame de la cámara", fg='red')
                ventana_principal.after(1000, capturar_foto)  # Reintentar la captura
                return

            # Procesar el frame y verificar rostros
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ubicaciones_rostros = face_recognition.face_locations(frame_rgb)

            if len(ubicaciones_rostros) != 1:
                etiqueta_posicion.config(text="Error: Debe haber exactamente un rostro visible", fg='red')
                ventana_principal.after(2000, capturar_foto)
                return

            # Guardar la imagen
            fecha_hora_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            nombre_archivo = f"{id_usuario}_{fecha_hora_actual}_{posicion}.jpg"
            ruta_archivo = os.path.join(ruta_carpeta_usuario, nombre_archivo)

            try:
                cv2.imwrite(ruta_archivo, frame)
                fotos_tomadas.append(ruta_archivo)

                # Codificar el rostro
                codificacion = face_recognition.face_encodings(frame_rgb, ubicaciones_rostros)[0]
                codificaciones.append(codificacion)

                etiqueta_posicion.config(text=f"Foto {posicion} guardada exitosamente", fg="green")
                contador_posicion += 1  # Pasar a la siguiente posición
                contador_segundos = TIEMPO_ESPERA
                ventana_principal.after(2000, capturar_foto)
            except Exception as e:
                etiqueta_posicion.config(text=f"Error: no se pudo guardar la foto: {e}", fg='red')
                ventana_principal.after(2000, capturar_foto)

    capturar_foto()


# Función para capturar foto con lentes con conteo regresivo
def capturar_foto_con_lentes(id_usuario, ruta_carpeta_usuario, etiqueta_posicion, etiqueta_conteo, ventana_principal, callback):
    etiqueta_posicion.config(text="Coloque sus lentes y mire a la cámara", fg="blue")
    ventana_principal.update_idletasks()

    contador_segundos = TIEMPO_ESPERA  # Contador de 6 segundos

    def realizar_conteo():
        nonlocal contador_segundos

        if contador_segundos > 0:
            etiqueta_conteo.config(text=f"Tiempo restante: {contador_segundos} segundos", fg="orange")
            contador_segundos -= 1
            ventana_principal.after(1000, realizar_conteo)
        else:
            # Capturar la foto
            ret, frame = config.captura.read()
            if not ret:
                etiqueta_posicion.config(text="Error: No se pudo leer el frame de la cámara", fg='red')
                return

            # Verificar rostro
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ubicaciones_rostros = face_recognition.face_locations(frame_rgb)

            if len(ubicaciones_rostros) != 1:
                etiqueta_posicion.config(text="Error: Debe haber exactamente un rostro visible", fg='red')
                return

            # Guardar la imagen
            fecha_hora_actual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            nombre_archivo = f"{id_usuario}_{fecha_hora_actual}_con_lentes.jpg"
            ruta_archivo = os.path.join(ruta_carpeta_usuario, nombre_archivo)

            try:
                cv2.imwrite(ruta_archivo, frame)
                foto_lentes = ruta_archivo

                # Codificar rostro
                codificacion = face_recognition.face_encodings(frame_rgb, ubicaciones_rostros)[0]
                callback(foto_lentes, [codificacion])
            except Exception as e:
                etiqueta_posicion.config(text=f"Error al guardar foto: {e}", fg="red")

    realizar_conteo()


# Ventana modal para preguntar si usa lentes
def preguntar_usa_lentes(ventana_principal, id_usuario, ruta_carpeta_usuario, fotos_tomadas, codificaciones, etiqueta_posicion, etiqueta_conteo, callback_lentes, callback_no_lentes):
    modal = Toplevel(ventana_principal)
    modal.title("¿Usa lentes?")
    modal.geometry("400x200")
    modal.grab_set()

    Label(modal, text="¿Usa lentes?", font=("Arial", 14), pady=20).pack()
    botones_frame = tk.Frame(modal)
    botones_frame.pack(pady=20)

    Button(botones_frame, text="Sí", command=lambda: [modal.destroy(), callback_lentes(id_usuario, ruta_carpeta_usuario, fotos_tomadas, codificaciones, etiqueta_posicion, etiqueta_conteo)], width=10, bg="green", fg="white").pack(side=tk.LEFT, padx=5)
    Button(botones_frame, text="No", command=lambda: [modal.destroy(), callback_no_lentes(fotos_tomadas, codificaciones, etiqueta_posicion)], width=10, bg="red", fg="white").pack(side=tk.RIGHT, padx=5)


# Función principal para capturar fotos
def capturar(id_usuario, ruta_carpeta_usuario, etiqueta_posicion, etiqueta_conteo, ventana_principal):
    posiciones = ["frontal", "lateral izquierdo", "lateral derecho", "mirando arriba", "mirando abajo"]

    def procesar_resultado(fotos_tomadas, codificaciones):
        if not fotos_tomadas or not codificaciones:
            etiqueta_posicion.config(text="Error: No se pudieron capturar todas las fotos.", fg="red")
            return

        preguntar_usa_lentes(ventana_principal, id_usuario, ruta_carpeta_usuario, fotos_tomadas, codificaciones, etiqueta_posicion, etiqueta_conteo, guardar_lentes_wrapper, guardar_en_bd_wrapper)
    #Esto hay que arreglo
    def guardar_lentes_wrapper(fotos_tomadas, codificaciones, lentes_fotos, lentes_codificaciones, etiqueta_posicion, etiqueta_conteo):
        fotos_tomadas.extend(lentes_fotos)
        codificaciones.extend(lentes_codificaciones)
        guardar_en_bd(fotos_tomadas, codificaciones, etiqueta_posicion)

    def guardar_en_bd_wrapper(fotos_tomadas, codificaciones, etiqueta_posicion):
        guardar_en_bd(fotos_tomadas, codificaciones, etiqueta_posicion)

    capturar_fotos(id_usuario, ruta_carpeta_usuario, posiciones, etiqueta_posicion, etiqueta_conteo, ventana_principal, procesar_resultado)


# Guardar en la base de datos
def guardar_en_bd(fotos_tomadas, codificaciones, etiqueta_posicion):
    if codificaciones:
        promedio_codificacion = [
            sum(cod[i] for cod in codificaciones) / len(codificaciones)
            for i in range(len(codificaciones[0]))
        ]
        guardar_codificacion_rostro(promedio_codificacion)
        etiqueta_posicion.config(text="Rostro registrado exitosamente.", fg="green")
