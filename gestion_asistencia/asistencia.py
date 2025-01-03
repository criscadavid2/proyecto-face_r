import sqlite3
from datetime import datetime
from tkinter import messagebox
from utils import conectar_bd_asistencia, conectar_bd_usuarios, ejecutar_consulta_asistencia, ejecutar_consulta_usuarios




#Empiezan funciones de asistencia
#Funcion para registrar la asistencia en la BD de SQlite
def registrar_asistencia(id_usuario):
    from gestion_rostros.registros import registrar_rostro
    """
    Registra la asistencia de un usuario identificado por su ID único.

    Parámetros:
        id_usuario (str): El ID único del usuario.
    """

    global ids_asistencia

    #Obtener la fecha y hora actuales
    
    ahora = datetime.now()
    fecha = ahora.strftime("%Y-%m-%d")
    hora = ahora.strftime("%H-%M-%S")

    #Verificar si el usuario ya tiene asistencia en esta sesion
    if id_usuario in ids_asistencia:
        print(f"Asistencia ya registrada en esta sesion para el usuario con ID {id_usuario}.")
        return
    
    #Conectar a la base de datos
    conexion, cursor = conectar_bd_asistencia()
    if conexion is None:
        return
    
    try:
        #verificar si ya existe un registro de asistencia para el usuario en la fecha actual

        cursor.execute('''SELECT *FROM asistencia WHERE usuario_id = ? AND fecha = ?,''', (id_usuario, fecha))
        asistencia_existente = cursor.fetchone()

        if asistencia_existente:
            print(f"Asistencia ya registrada para el usuario con ID {id_usuario} en la fecha {fecha}.")
            ids_asistencia.add(id_usuario)
            return
        
        #Consultar el grupo del usuario desde la tabla "usuarios"
        cursor.execute('''SELECT grupo FROM usuarios WHERE id = ?''', (id_usuario))
        resultado = cursor.fetchone()

        if resultado is None:
            print(f"No se encontró informacion del usuario con ID {id_usuario}")
            return

        grupo = resultado[0] # Asumimos que grupo está definido en usuarios

        #Registrar la asistencia
        cursor.execute('''INSERT INTO asistencia (usuario_id, grupo, fecha, estado)
                          VALUES (?. ?. ?. ?);''', (id_usuario, grupo, fecha, "Presente"))
        
        #Confirmar los cambios
        conexion.commit()
        print(f"Asistencia registrada para el usuario con ID {id_usuario} en la fecha {fecha}.")

        #Agregar el ID a la lista de IDs ya registrados en esta sesion
        ids_asistencia.add(id_usuario )

    except sqlite3.Error as e:
        print(f"Error al registrar la asistencia: {e}")

    finally:
        #cerrar la conexion
        conexion.close()

def ver_asistencia():
    pass
    #archivo_asistencia = "C:/Users/Chris/Documents/proyecto-face_r/asistencia/asistencia.csv"
    #if os.path.exists(archivo_asistencia):
        #os.startfile(archivo_asistencia)
    #else:
        #messagebox.showerror("Error", "El archivo de asistencia no existe.")
