import sqlite3
import bcrypt

def verificar_usuario_con_hash(db_path, usuario_id, contrasena_proporcionada):
    try:
        # Conectar a la base de datos
        conexion = sqlite3.connect(db_path)
        cursor = conexion.cursor()

        # Consultar el hash de la contraseña para el usuario dado
        query = "SELECT contrasena_usuario FROM usuarios WHERE id = ?"
        cursor.execute(query, (usuario_id,))
        resultado = cursor.fetchone()

        if not resultado:
            print("[Debug] Usuario no encontrado.")
            return False

        # Obtener el hash almacenado
        contrasena_hash_almacenada = resultado[0]

        # Verificar la contraseña proporcionada
        if bcrypt.checkpw(contrasena_proporcionada.encode('utf-8'), contrasena_hash_almacenada):
            print("[Debug] Contraseña verificada correctamente.")
            return True
        else:
            print("[Debug] Contraseña incorrecta.")
            return False

    except sqlite3.Error as e:
        print(f"[Debug] Error al acceder a la base de datos: {e}")
        return False

    finally:
        if conexion:
            conexion.close()

# Ejemplo de uso
db_path = "gestion_usuarios/usuarios.db"
usuario_id = "1020443670"
contrasena_proporcionada = "12345678"

if verificar_usuario_con_hash(db_path, usuario_id, contrasena_proporcionada):
    print("Inicio de sesión exitoso.")
else:
    print("Error en el inicio de sesión.")
