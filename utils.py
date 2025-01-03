import tkinter as tk
import sqlite3
from tkinter import messagebox
import pickle
from gestion_super_admin.super_admin import acceder_funciones_super_admin
import bcrypt
import config #Importa el archivo config.py

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



def verificar_login(numero_usuario, contrasena_usuario, actualizar_estado_sesion_callback, acceder_funciones_super_admin,ventana_principal, login_ventana):
    config.usuario_logueado_id, config.usuario_logueado_nombre
    """Verifica las credenciales de un usuario y actualiza el estado de sesión.

    Args:
        numero_usuario (str): Número de usuario ingresado.
        contrasena_usuario (str): Contraseña ingresada.
        actualizar_estado_sesion_callback (function): Función para actualizar el estado de la sesión.
        ventana_principal (tk.Tk): Ventana principal de la aplicación.
        login_ventana (tk.Toplevel): Ventana de login.

    Returns:
        bool: True si el login es exitoso, False en caso contrario."""
    
    

    print(f"[Debug] Verificando credenciales: {numero_usuario}, {contrasena_usuario}")

    # Verificar las credenciales del super administrador
    if numero_usuario == SUPER_ADMIN_USUARIO and contrasena_usuario == SUPER_ADMIN_CONTRASENA:
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
        return  # Si no conecta la bd salimos de la función

    try:
        # Buscar al usuario en la base de datos
        query = "SELECT id, nombre, contrasena FROM usuarios WHERE numero_usuario = ?"
        cursor.execute(query, (numero_usuario,))
        usuario = cursor.fetchone()
        if usuario and bcrypt.checkpw(contrasena_usuario.encode('utf-8'), usuario[2]):
            config.usuario_logueado_id = usuario[0]
            config.usuario_logueado_nombre = usuario[1]
            
            actualizar_estado_sesion_callback(config.usuario_logueado_id, config.usuario_logueado_nombre)
            print(f"[Debug] Inicio de sesión exitoso: {config.usuario_logueado_id}, {config.usuario_logueado_nombre}")
            login_ventana.destroy()
            return True #Retornar True si el login es exitoso
        else:
            messagebox.showerror("Error de inicio de sesión", "Número de usuario o contraseña incorrectos.")
            return False #Retornar False en caso de credenciales incorrectas
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


#Función para cargar codificaciones de rostros conocidas
def cargar_rostros_conocidos():
    """Carga todas las codificaciones de rostros y sus IDs desde la base de datos."""
    codificaciones = []
    ids = []
    try:
        conexion, cursor = conectar_bd_usuarios()
        if conexion is None:
            return [], []
        
        #Consultar los rostros y sus IDs/nombres
        consulta = "SELECT id, codificacion_rostro FROM usuarios WHERE codificacion_rostro IS NOT NULL"
        cursor.execute(consulta)
        resultados = cursor.fetchall()

        for fila in resultados:
            id_usuario = fila[0]
            codificacion_rostro = pickle.loads(fila[1]) # Convertir el BLOB de nuevo a la codificacion
            codificaciones.append(codificacion_rostro)
            ids.append(id_usuario) 

        conexion.close()
        return codificaciones, ids
    except Exception as e:
        print(f"Error al cargar los rostros desde la base de datos: {e}")
        return [], []

#----------------------- FIN BD ---------------

#print(f"Valor de usuario_logueado_id: {usuario_logueado_id}, varlor de usuario_logueado_nombre: {usuario_logueado_nombre}")

