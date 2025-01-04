import cv2
import face_recognition
import pickle
import os
from datetime import datetime
import tkinter as tk
from tkinter import simpledialog, messagebox, Toplevel, Button, Canvas
from utils import conectar_bd_usuarios, ejecutar_consulta_usuarios, cargar_rostros_conocidos
from PIL import Image, ImageTk
import config
import gestion_camaras.camaras as camaras

# Función para actualizar el frame en el canvas con reconocimiento facial
def actualizar_frame_con_reconocimiento(canvas, ventana):
    ret, frame = config.captura.read()
    if ret:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #Realizar el reconocimiento facial
        ubicaciones_rostros = face_recognition.face_locations(frame_rgb)
        codificaciones_rostros = face_recognition.face_encodings(frame_rgb, ubicaciones_rostros)

        for (top, right, bottom, left), codificacion in zip(ubicaciones_rostros, codificaciones_rostros):
            coincidencias = face_recognition.compare_faces(config.codificaciones_conocidas, codificacion)
            distancias = face_recognition.face_distance(config.codificaciones_conocidas, codificacion)
            mejor_match = None

            if coincidencias:
                mejor_match = min(range(len(distancias)), key=distancias.__getitem__)
            
            if mejor_match is not None and coincidencias[mejor_match]:
                id_usuario = config.ids_conocidos_conocidos[mejor_match]

                #Consultar información adicional del estudiante
                consulta_estudiante = """
                    SELECT nombre_usuario, apellido_usuario, grupo_usuario
                    FROM usuarios
                    WHERE id = ? AND rol_id = '3'
                """ #Suponiendo que el rol_id 3 corresponde a estudiantes
                resultados = ejecutar_consulta_usuarios(consulta_estudiante, (id_usuario,))

                if resultados:
                    nombre_usuario, apellido_usuario, grupo = resultados[0]
                    etiqueta = f"{id_usuario} {nombre_usuario} {apellido_usuario} ({grupo})"
                else:
                    #Si no es estudiante, consultar nombre y apellido
                    consulta_general = """
                    SELECT nombre_usuario, apellido_usuario
                    FROM usuarios
                    WHERE id = ?
                """
                resultados_general = ejecutar_consulta_usuarios(consulta_general, (id_usuario,))

                if resultados_general:
                    nombre_usuario, apellido_usuario = resultados_general[0]
                    etiqueta = f"{id_usuario} {nombre_usuario} {apellido_usuario} - No es estudiante"
                else:
                    etiqueta = f"i{id_usuario} - Información no encontrada"
            else:
                etiqueta = "Desconocido" 

            # Dibujar rectángulo y nombre
            cv2.rectangle(frame_rgb, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame_rgb, etiqueta, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Mostrar frame en el canvas
        imagen = Image.fromarray(frame_rgb)
        config.imagen_tk = ImageTk.PhotoImage(image=imagen)
        canvas.create_image(0, 0, anchor=tk.NW, image=config.imagen_tk)

        ventana.after(10, lambda: actualizar_frame_con_reconocimiento(canvas, ventana))
        

# Función para manejar la ventana de la cámara
def iniciar_camara(indice_camara, ventana):
    captura = cv2.VideoCapture(indice_camara)
    if not captura.isOpened():
        messagebox.showerror("Error", "No se pudo acceder a la cámara.")
        ventana.destroy()
        return None
    return captura

# Función para cerrar la cámara y liberar recursos
def cerrar_camara(captura, ventana):
    if captura is not None:
        captura.release()
    cv2.destroyAllWindows()
    ventana.destroy()

# Función para guardar una nueva codificación en la base de datos
def guardar_codificacion_rostro(id_usuario, codificacion):
    try:
        conexion, cursor = conectar_bd_usuarios()
        if conexion is None:
            return

        codificacion_serializada = pickle.dumps(codificacion)

        consulta = '''
            UPDATE usuarios
            SET codificacion_rostro = ?
            WHERE id = ?
        '''
        cursor.execute(consulta, (codificacion_serializada, id_usuario))
        conexion.commit()
        conexion.close()

        print(f"Codificación del rostro para el usuario {id_usuario} guardada exitosamente.")
    except Exception as e:
        print(f"Error al guardar las codificaciones: {e}")

# Función principal para registrar un nuevo rostro
def registrar_rostro(ventana_principal, opcion_camara):
    ventana_rostro = Toplevel(ventana_principal)
    ventana_rostro.title("Registrar Rostro")
    ventana_rostro.geometry("800x600")

    indice_camara = int(opcion_camara.get().split()[-1])
    config.captura = iniciar_camara(indice_camara, ventana_rostro)
    if config.captura is None:
        return

    canvas = Canvas(ventana_rostro, width=640, height=480)
    canvas.pack()

    actualizar_frame_con_reconocimiento(canvas, ventana_rostro)

    def capturar():
        ret, frame = config.captura.read()
        if not ret:
            messagebox.showerror("Error", "No se pudo acceder a la cámara.")
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ubicaciones_rostros = face_recognition.face_locations(frame_rgb)
        codificaciones_rostros = face_recognition.face_encodings(frame_rgb, ubicaciones_rostros)

        if len(ubicaciones_rostros) == 0:
            messagebox.showwarning("Advertencia", "No se detectó ningún rostro. Intenta de nuevo.")
            return

        if len(ubicaciones_rostros) > 1:
            messagebox.showerror("Advertencia", "Se detectaron múltiples rostros. Por favor, asegúrate de que solo haya una persona visible.")
            return

        # Tomar la primera codificación (debe haber solo un rostro en este punto)
        codificacion = codificaciones_rostros[0]
        id_usuario = simpledialog.askstring("ID Único", "Ingrese el ID del usuario registrado:")

        if id_usuario:
            consulta = "SELECT id FROM usuarios WHERE id = ?"
            resultados = ejecutar_consulta_usuarios(consulta, (id_usuario,))

            if resultados:
                guardar_codificacion_rostro(id_usuario, codificacion)
                messagebox.showinfo("Éxito", f"Rostro del usuario {id_usuario} registrado con éxito.")
            else:
                messagebox.showerror("Error", f"No se encontró un usuario con ID {id_usuario}.")

    def seleccionar_camara():
        camaras.abrir_configuracion(ventana_rostro, opcion_camara)

    botones_frame = tk.Frame(ventana_rostro)
    botones_frame.pack(side=tk.BOTTOM, pady=10)

    btn_capturar = Button(botones_frame, text="Capturar", command=capturar)
    btn_capturar.pack(side=tk.LEFT, padx=10)

    btn_camara = Button(botones_frame, text="Seleccionar Cámara", command=seleccionar_camara)
    btn_camara.pack(side=tk.LEFT, padx=10)

    btn_salir = Button(botones_frame, text="Salir", command=lambda: cerrar_camara(config.captura, ventana_rostro))
    btn_salir.pack(side=tk.LEFT, padx=10)

# Función para eliminar un rostro existente
def eliminar_rostro():
    id_a_eliminar = simpledialog.askstring("Eliminar Rostro", "Ingresa el ID único del rostro a eliminar:")

    if not id_a_eliminar:
        messagebox.showwarning("Cancelado", "La eliminación fue cancelada.")
        return

    try:
        conexion, cursor = conectar_bd_usuarios()
        if conexion is None:
            return

        consulta = "SELECT codificacion_rostro FROM usuarios WHERE id = ?"
        cursor.execute(consulta, (id_a_eliminar,))
        resultado = cursor.fetchone()

        if resultado and resultado[0] is not None:
            consulta_update = """
                UPDATE usuarios
                SET codificacion_rostro = NULL
                WHERE id = ?
            """
            cursor.execute(consulta_update, (id_a_eliminar,))
            conexion.commit()
            messagebox.showinfo("Éxito", f"El rostro del usuario {id_a_eliminar} fue eliminado correctamente.")
        else:
            messagebox.showerror("Error", f"No se encontró un rostro registrado para el usuario {id_a_eliminar}.")

        conexion.close()
    except Exception as e:
        print(f"Error al eliminar el rostro: {e}")

# Cargar codificaciones al inicio
config.codificaciones_conocidas, config.ids_conocidos_conocidos = cargar_rostros_conocidos()
