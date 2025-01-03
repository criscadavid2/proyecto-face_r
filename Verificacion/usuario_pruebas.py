import sqlite3

# Función para insertar un usuario de prueba
def insertar_usuario_prueba(cedula, nombre, apellidos, contrasena, correo, rol_nombre):
    # Conectar a la base de datos
    conexion = sqlite3.connect("gestion_usuarios/usuarios.db")
    cursor = conexion.cursor()

    # Obtener el ID del rol (Administrador, Profesor, Estudiante)
    cursor.execute("SELECT id FROM roles WHERE nombre = ?", (rol_nombre,))
    rol_id = cursor.fetchone()

    if rol_id:
        rol_id = rol_id[0]
    else:
        print(f"Error: El rol '{rol_nombre}' no existe.")
        conexion.close()
        return

    # Validar si la cédula ya existe en la base de datos
    cursor.execute("SELECT * FROM usuarios WHERE cedula = ?", (cedula,))
    if cursor.fetchone():
        print(f"Error: Ya existe un usuario con la cédula '{cedula}'.")
        conexion.close()
        return

    # Insertar el usuario en la tabla usuarios
    cursor.execute("""
        INSERT INTO usuarios (cedula, nombre, apellidos, contrasena, correo_electronico, rol_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (cedula, nombre, apellidos, contrasena, correo, rol_id))

    # Guardar los cambios y cerrar la conexión
    conexion.commit()
    conexion.close()
    print(f"Usuario '{nombre}' con cédula '{cedula}' y rol '{rol_nombre}' insertado correctamente.")

# Crear usuarios de prueba
def crear_usuarios_de_prueba():
    # Insertar usuarios con sus roles respectivos
    # Administrador
    insertar_usuario_prueba("1234567890", "Admin", "Administrador", "admin123", "admin@correo.com", "Administrador")
    # Profesor
    insertar_usuario_prueba("2345678901", "John", "Doe", "profesor123", "profesor@correo.com", "Profesor")
    # Estudiante
    insertar_usuario_prueba("3456789012", "Jane", "Smith", "estudiante123", "estudiante@correo.com", "Estudiante")

# Ejecutar la función para insertar los usuarios de prueba
if __name__ == "__main__":
    crear_usuarios_de_prueba()
