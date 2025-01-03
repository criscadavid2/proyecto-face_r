import cv2
import numpy as np
import face_recognition
import threading
from datetime import datetime
from gestion_rostros.registros import cargar_rostros_conocidos
from gestion_asistencia.asistencia import registrar_asistencia
from gestion_camaras.camaras import inicializar_camaras


#Variables globales
capturando = False
codificaciones_conocidas = []
nombres_conocidos = []

def cargar_datos_rostros():
    """Carga las codificaciones y nombres de rostros conocidos."""
    global codificaciones_conocidas, nombres_conocidos
    codificaciones_conocidas, nombres_conocidos = cargar_rostros_conocidos()
    
    if not codificaciones_conocidas:
        print("No se encontraron rostros conocidos en la BD.")


def iniciar_reconocimiento(indice_camara):
    """Inicia el reconocimiento facial en tiempo real."""
    global capturando
    capturando = True
    nombre = "Desconocido" #Valor por defecto
    id_unico = "N/A" #Valor por defecto
    

    captura = cv2.VideoCapture(indice_camara)
    if not captura.isOpened():
        print(f"Error: No se pudo abrir la cámara con índice {indice_camara}.")
        return

    while capturando:
        ret, frame = captura.read()
        if not ret:
            print("Error: No se pudo leer el frame.")
            break

        # Procesamiento del frame para el reconocimiento facial
        frame_pequeno = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        frame_rgb = cv2.cvtColor(frame_pequeno, cv2.COLOR_BGR2RGB)

        # Detectar rostros y codificaciones
        ubicaciones_rostros = face_recognition.face_locations(frame_rgb)
        codificaciones_rostros = face_recognition.face_encodings(frame_rgb, ubicaciones_rostros)

        for codificacion, ubicacion in zip(codificaciones_rostros, ubicaciones_rostros):
            coincidencias = face_recognition.compare_faces(codificaciones_conocidas, codificacion)
            distancias = face_recognition.face_distance(codificaciones_conocidas, codificacion)

            mejor_match = None
            if (distancias):
                mejor_match = min(range(len(distancias)), key=lambda i: distancias[i])
                
            # Verificar si hay coincidencias
            if mejor_match is not None and coincidencias[mejor_match]:
                nombre_completo = nombres_conocidos[mejor_match]
                nombre, id_unico = nombre_completo.split("|")
                registrar_asistencia(nombre) #Registrar asistencia en la BD
                
            #Mostrar información en el frame
            top, right, bottom, left = ubicacion
            cv2.rectangle(frame, (left * 4, top * 4), (right * 4, bottom *4), (0, 255, 0), 2)
            cv2.putText(frame, f"Nombre: {nombre}", (left * 4, bottom * 4 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(frame, f"ID: {id_unico}", (left * 4, bottom * 4 + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
        cv2.imshow("Reconocimiento Facial", frame)

        # Salir si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    captura.release() # Liberar la cámara
    cv2.destroyAllWindows() # Cerrar todas las ventanas
        

def iniciar_hilo_reconocimiento(indice_camara):

    """Inicia el reconocimiento facial en un hilo separado"""
    cargar_datos_rostros() #Cargar rostros conocidos antes de iniciar
    hilo = threading.Thread(target=iniciar_reconocimiento, args=(indice_camara,)) #Inicia el hilo
    hilo.start()

def detener_reconocimiento():
    """Detiene el reconocimiento facial"""
    global capturando
    capturando = False



