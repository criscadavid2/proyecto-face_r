import cv2
import face_recognition
import pickle
import os
from datetime import datetime
from tkinter import simpledialog, messagebox
import sqlite3
from utils import conectar_bd_usuarios, ejecutar_consulta_usuarios, conectar_bd_asistencia, ejecutar_consulta_asistencia
from utils import cargar_rostros_conocidos


#Cargar codificaciones al inicio
codificaciones_conocidas, ids_conocidos_conocidos = cargar_rostros_conocidos()


#Función para guardar una nueva codificacion en la base de datos
def guardar_codificacion_rostro(id_usuario, codificacion):
    '''Guarda o actualiza la codificacion de un rostro en la base de datos'''
    try:
        conexion, cursor = conectar_bd_usuarios()
        if conexion is None:
            return
        
        #Convertir la codificacion a un formato serializado
        codificacion_serializada = pickle.dumps(codificacion)

        #Actualizar la columna codificacion_rostro
        consulta = '''
            UPDATE usuarios
            SET codificacion_rostro = ?
            WHERE id = ?
        '''
        cursor.execute(consulta, (codificacion_serializada, id_usuario))
        # Confirmar los cambios y cerrar la conexión
        conexion.commit()
        conexion.close()

        print(f"Codificacion del rostro para el usuario {id_usuario} guardada exitosamente.")
    except Exception as e:
        print(f"Error al guardar las codificaciones: {e}")

# Función para registrar un nuevo rostro
def registrar_rostro(indice_camara):
    '''Registra un nuevo rostro asociado a un ID existente en la base de datos'''
    captura = cv2.VideoCapture(indice_camara)
    messagebox.showinfo("Registrar Rostro", "Por favor, mantén tu rostro frente a la cámara.")
    
    if not captura.isOpened():
        messagebox.showerror("Error", "No se pudo acceder a la cámara. Verifica la conexión.")
        return
    
    while True:
        ret, frame = captura.read()
        if not ret:
            messagebox.showerror("Error", "No se pudo acceder a la cámara.")
            break

        cv2.imshow("Registrar Rostro", frame)

        #Presionar 's' para capturar
        if cv2.waitKey(1) & 0xFF == ord('s'):  # Presionar 's' para capturar
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ubicaciones_rostros = face_recognition.face_locations(frame_rgb)
            
            if len(ubicaciones_rostros) == 0:
                messagebox.showwarning("Advertencia", "No se detectó ningún rostro. Intenta de nuevo.")
                continue

            if len(ubicaciones_rostros) > 1:
                messagebox.showerror("Advertencia", "Se detectaron multiples rostros. Por favor asegurate de que solo haya una persona visible.")
                continue

            #Codificar rostro
            codificacion = face_recognition.face_encodings(frame_rgb, ubicaciones_rostros)[0]

            #Solicitar el ID del usuario
            id_usuario = simpledialog.askstring("ID Único", "Ingrese el ID usuario registrado:")

            if id_usuario:
                #Verificar si el ID existe en la Base de datos
                consulta = "SELECT id FROM usuarios WHERE id = ?"
                resultados = ejecutar_consulta_usuarios(consulta, (id_usuario))
            
                if resultados: #Si el ID existe
                    guardar_codificacion_rostro(id_usuario, codificacion)
                    messagebox.showinfo("Éxito", f"Rostro del usuario {id_usuario} registrado con éxito.")                    
                else:
                    messagebox.showerror("Error", f"No se encontró un usuario con ID {id_usuario}.")
            break
                    
                    # Aquí puedes agregar la función para abrir el formulario de registro de un nuevo usuario
                    # Puedes llamar a un formulario en Tkinter o a otro tipo de interfaz
                    # Por ejemplo: open_registration_form(nuevo_id, codificacion)  

        #Presionar 'q' para salir
        if cv2.waitKey(1) & 0xFF == ord('q'):
            messagebox.showinfo("Salir", "Cerrando la cámara.")
            break    

    captura.release()
    cv2.destroyAllWindows()

# Función para eliminar un rostro existente 
def eliminar_rostro():
    """Elimina la codificación de un rostro asociado a un usuario. """
    id_a_eliminar = simpledialog.askstring("Eliminar Rostro", "Ingresa el ID único del rostro a eliminar:")
    
    if not id_a_eliminar:
        messagebox.showwarning("Cancelado", "La eliminación fue cancelada.")
        return

    try:
        conexion, cursor = conectar_bd_usuarios()
        if conexion is None:
            return

        #Verificar si el ID existe
        consulta = "SELECT codificacion_rostro FROM usuarios WHERE id = ?"
        cursor.execute(consulta, (id_a_eliminar,))
        resultado = cursor.fetchone()
        
        if resultado and resultado[0] is not None: #Si existe una codificación
            #Eliminar codificación
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