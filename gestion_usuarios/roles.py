from utils import ejecutar_consulta_usuarios, conectar_bd_usuarios
from tkinter import messagebox
import config
import sqlite3

# Función para obtener el rol del usuario
def obtener_rol_usuario(usuario_id):
    """Obtiene el rol del usuario según su ID."""
    query = """
        SELECT roles.nombre
        FROM usuarios
        JOIN roles ON usuarios.rol_id = roles.id
        WHERE usuarios.id = ?
    """
    resultado = ejecutar_consulta_usuarios(query, (usuario_id,))
    return resultado[0][0] if resultado else None

# Funciones para verificar permisos

#Función para verificar si un usuario es administrador
def es_administrador(usuario_id):
# Manejar el caso del Super Admin por defecto
    if usuario_id == "Super Admin":
        return True  # El Super Admin siempre tiene permisos
    
    # Verificar en la base de datos para otros usuarios
    try:
        conexion, cursor = conectar_bd_usuarios()
        if conexion is None:
            messagebox.showerror("Error de conexión", "No se pudo verificar el rol del usuario.")
            return False

    
        # Consulta el rol del usuario
        cursor.execute("""
            SELECT roles.nombre
            FROM usuarios
            JOIN roles ON usuarios.rol_id = roles.id
            WHERE usuarios.id = ?
        resultado = cursor.fetchone()
        """, (usuario_id,))
        resultado = cursor.fetchone()

        # Verificar Si el rol es  "Administrador"
        return resultado and resultado[0] == 'Administrador'
    except sqlite3.Error as e:
        messagebox.showerror("Error en la consulta de base de datos", f"Error al verificar el rol del usuario: {e}")
        return False
    finally:
        if conexion:
            conexion.close()
           
def es_profesor(usuario_id):
    """Verifica si el usuario es profesor."""
    return obtener_rol_usuario(usuario_id) == "Profesor"

def es_estudiante(usuario_id):
    # Función para verificar si un usuario es estudiante
    return obtener_rol_usuario(usuario_id) == "Estudiante"

# Función para obtener el rol del usuario logueado
def verificar_rol_usuario(usuario_id):
    """Devuelve el nombre del rol del usuario."""
    if es_administrador(usuario_id):
        return "Administrador"
    elif es_profesor(usuario_id):
        return "Profesor"
    elif es_estudiante(usuario_id):
        return "Estudiante"
    else:
        return "Rol desconocido"


# Verificación del rol
rol_usuario = verificar_rol_usuario(config.usuario_logueado_id)
print(f"El usuario logueado tiene el rol de: {rol_usuario}")
