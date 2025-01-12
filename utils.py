#utils.py
import tkinter as tk
import sqlite3
from tkinter import messagebox
import pickle
from gestion_super_admin.super_admin import acceder_funciones_super_admin
import bcrypt
import config #Importa el archivo config.py
import cv2
from PIL import Image, ImageTk
import face_recognition

# Constantes de super administrador
SUPER_ADMIN_USUARIO = "admin"
SUPER_ADMIN_CONTRASENA = "admin"

#Funcion para conecta la base de datos usuarios
def conectar_bd_usuarios():
    try:
        conexion = sqlite3.connect("gestion_usuarios/usuarios.db")
        cursor = conexion.cursor()
        return conexion, cursor
    except sqlite3.Error as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos usuarios: {e}")
        return None, None
    
#Funcion para ejecutar consultas a la base de datos usuarios
def ejecutar_consulta_usuarios(query, parametros=()):
    conexion, cursor = conectar_bd_usuarios()
    if conexion is None:
        return None
    try:
        cursor.execute(query, parametros)
        resultados = cursor.fetchall()
        conexion.commit()
        return resultados
    except sqlite3.Error as e:
        messagebox.showerror("Error de base de datos usuarios", f"Error en la consulta: {e}")
        return None
    finally:
        conexion.close()


#Funcion para conectar la base de datos asistencia.db
def conectar_bd_asistencia():
    try:
        conexion = sqlite3.connect("gestion_asistencia/asistencia.db")
        cursor = conexion.cursor()
        return conexion, cursor
    except sqlite3.Error as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos asistencia: {e}")
        return None, None
    
#Funcion para ejecutar consultas a la base de asistencia.db
def ejecutar_consulta_asistencia(query, parametros=()):
    conexion, cursor = conectar_bd_asistencia()
    if conexion is None:
        return None
    try:
        cursor.execute(query, parametros)
        resultados = cursor.fetchall()
        conexion.commit()
        return resultados
    except sqlite3.Error as e:
        messagebox.showerror("Error de base de datos asistencia", f"Error en la consulta: {e}")
        return None
    finally:
        conexion.close()



def verificar_login(usuario_id, contrasena_usuario, actualizar_estado_sesion_callback, acceder_funciones_super_admin,ventana_principal, login_ventana):
    config.usuario_logueado_id, config.usuario_logueado_nombre
    """Verifica las credenciales de un usuario y actualiza el estado de sesión."""

    print(f"[Debug] Verificando credenciales: {usuario_id}, {contrasena_usuario}")

    # Verificar las credenciales del super administrador
    if usuario_id == SUPER_ADMIN_USUARIO and contrasena_usuario == SUPER_ADMIN_CONTRASENA:
        print("[Debug] Credenciales de Super Admin correctas")
        config.usuario_logueado_id = "Super Admin"
        config.usuario_logueado_nombre = "Super Admin"
        actualizar_estado_sesion_callback(config.usuario_logueado_id, config.usuario_logueado_nombre)
        print(f"[Debug] Inicio de sesión exitoso: {config.usuario_logueado_id}, {config.usuario_logueado_nombre}")
        login_ventana.destroy()
        acceder_funciones_super_admin()
        messagebox.showinfo("Inicio de sesión exitoso", "Bienvenido, Super Administrador")
        print(f"Valor de usuario_logueado_id: {config.usuario_logueado_id}, varlor de usuario_logueado_nombre: {config.usuario_logueado_nombre}")
        return True# Salir de la función aquí
    else:
        print("[Debug] Credenciales de Super Admin incorrectas")
            
    # Verificar credenciales en la base de datos
    conexion, cursor = conectar_bd_usuarios()  # Conectamos la BD
    if conexion is None:
        return False # Si no conecta la bd salimos de la función

    try:
        # Buscar al usuario en la base de datos
        query = "SELECT id, nombre_usuario, contrasena_usuario FROM usuarios WHERE id = ?"
        cursor.execute(query, (usuario_id,))
        usuario = cursor.fetchone()
        print("[Debug] Usuario obtenido de la bd:", usuario)

        if usuario:
            print(f"[Debug] Verificando contraseña para el usuario: {usuario[0]}") 
            if bcrypt.checkpw(contrasena_usuario.encode('utf-8'), usuario[2]):
                config.usuario_logueado_id = usuario[0]
                config.usuario_logueado_nombre = usuario[1]
            
                actualizar_estado_sesion_callback(config.usuario_logueado_id, config.usuario_logueado_nombre)
                print(f"[Debug] Inicio de sesión exitoso: {config.usuario_logueado_id}, {config.usuario_logueado_nombre}")
                login_ventana.destroy()
                return True #Retornar True si el login es exitoso
            else:
                print("[Debug] Contraseña incorrecta")
                messagebox.showerror("Error de inicio de sesión", "Número de usuario o contraseña incorrectos.")
                return False #Retornar False en caso de credenciales incorrectas
        else:
            print("[Debug] Usuario no encontrado en la base de datos")
            messagebox.showerror("Error de inicio de sesión", "Número de usuario o contraseña incorrectos.")    
        
        return False #Retornar False en caso de usuario no encontrado   
    except sqlite3.Error as e:
        messagebox.showerror("Error de base de datos", f"Error en la consulta: {e}")
        return False #Retornar False en caso de error de base de datos
    finally:
        conexion.close()

#------------------Login de usuarios
# Ejemplo de cómo crear y pasar login_ventana
def mostrar_login(ventana_principal, actualizar_estado_sesion, acceder_funciones_super_admin):

    """
    
    Maneja el inicio de sesión de un usuario, incluyendo validaciones y actualizaciones de estado.

    Args:
        ventana_principal: Referencia a la ventana principal de la aplicación.
        actualizar_estado_sesion: Función para actualizar el estado de la sesión.
        acceder_funciones_super_admin: Función para acceder a las funciones exclusivas del superadministrador.
    """
 
    # Ventana de inicio de sesión
    login_ventana = tk.Toplevel(ventana_principal)
    login_ventana.title("Iniciar sesión")
    login_ventana.geometry("300x200")

    #Campos de entrada
    usuario_label = tk.Label(login_ventana, text="Número de usuario:")
    usuario_label.pack(pady=5)
    usuario_entry = tk.Entry(login_ventana)
    usuario_entry.pack(pady=5)

    contrasena_label = tk.Label(login_ventana, text="Contraseña:")
    contrasena_label.pack(pady=5)
    contrasena_entry = tk.Entry(login_ventana, show="*")
    contrasena_entry.pack(pady=5)

    #Botón Iniciar Sesión
    def login():
        #Obtener Valores de entrada
        numero_usuario = usuario_entry.get().strip()
        contrasena_usuario = contrasena_entry.get().strip()
               
        #Verificar credenciales en la base de datos
        if verificar_login(numero_usuario, contrasena_usuario, actualizar_estado_sesion, acceder_funciones_super_admin, ventana_principal, login_ventana):
            print("[Debug] Login exitoso. cerrando ventana de login")
        else:
            print("[Debug] Error en el login")
        

    #Botón Iniciar sesión
    tk.Button(login_ventana, text="Iniciar sesión", command=login).pack(pady=20)


# Cerrar Sesion
def cerrar_sesion(estado_label, boton_perfil, login_logout_btn, ventana_principal, actualizar_estado_sesion):
    config.usuario_logueado_id, config.usuario_logueado_nombre
    config.usuario_logueado_id = None
    config.usuario_logueado_nombre = None
    """
    Cierra la sesión actual y actualiza el estado en la interfaz.

    Args:
        actualizar_estado_sesion: Función para actualizar el estado de la sesión.
    """
    
    #Actualizar el estado de la interfaz
    estado_label.config(text="Iniciar sesión")
    boton_perfil.config(state=tk.DISABLED)
    
    login_logout_btn.config(
        text="Iniciar sesión",
        command=lambda: mostrar_login(
            ventana_principal,
            actualizar_estado_sesion,
            acceder_funciones_super_admin
    )
)   

def actualizar_boton_login_logout(
        usuario_id, estado_label, boton_perfil, login_logout_btn, ventana_principal, actualizar_estado_sesion_callback):
        if usuario_id: #usuario está logueado
            login_logout_btn.config(
                text="Cerrar sesión",
                command=lambda: cerrar_sesion(
                    estado_label,
                    boton_perfil,
                    login_logout_btn,
                    ventana_principal,
                    actualizar_estado_sesion_callback)
        )


#----------------------- FIN BD ---------------

# Función para guardar la codificación de un rostro en la base de datos
def guardar_codificacion_rostro(id_usuario, codificacion):
    """Guarda o actualiza la codificación del rostro de un usuario en la base de datos."""
    try:
        conexion, cursor = conectar_bd_usuarios()
        if conexion is None:
            return False

        # Serializar la codificación para almacenarla como BLOB en la base de datos
        codificacion_serializada = pickle.dumps(codificacion)

        # Actualizar o insertar la codificación en la tabla de usuarios
        consulta = """
            UPDATE usuarios
            SET codificacion_rostro = ?
            WHERE id = ?
        """
        cursor.execute(consulta, (codificacion_serializada, id_usuario))
        conexion.commit()
        print(f"[Debug] Codificación del rostro para el usuario {id_usuario} guardada exitosamente.")
        return True
    except Exception as e:
        print(f"[Debug] Error al guardar la codificación: {e}")
        return False
    finally:
        if conexion:
            conexion.close()

def verificar_rostros(frame, etiqueta_posicion):
    """Verifica la cantidad de rostros detectados en un frame y actualiza la etiqueta."""
    try:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ubicaciones_rostros = face_recognition.face_locations(frame_rgb)

        #Dibujar cuadro verdes alrededor de los rostros detectados
        for (top, right, bottom, left) in ubicaciones_rostros:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)


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



def actualizar_frame(canvas, etiqueta_estado, verificar_rostros):
    try:
        ret, frame = config.captura.read()
        if not ret:
            if etiqueta_estado.winfo_exists():
                etiqueta_estado.config(text="Error al leer el frame de la cámara.", fg="red")
            return 
        
        #Verificar rostros  y dibujar cuadros verdes
        if callable(verificar_rostros):
            verificar_rostros(frame, etiqueta_estado)
        else:
            print("[Debug] verificar_rostros no es una función válida.")
        
        #Convertir el frame a RGB compatible con tkinter
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imagen = Image.fromarray(frame_rgb)
        config.imagen_tk = ImageTk.PhotoImage(image=imagen)

        canvas.create_image(0, 0, anchor=tk.NW, image=config.imagen_tk)
        canvas.image_tk = config.imagen_tk
    except Exception as e:
        if etiqueta_estado.winfo_exists():
            etiqueta_estado.config(text=f"Error al actualizar el frame: {e}", fg="red")
        print(f"[Debug] Error al actualizar el frame: {e}")
    finally:
        #Asegurar que el ciclo de actualización se detenga si ocurre un error crítico
        if etiqueta_estado.winfo_exists():
            canvas.after(10, lambda: actualizar_frame(canvas, etiqueta_estado, verificar_rostros))

