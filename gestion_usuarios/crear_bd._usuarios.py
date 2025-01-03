import sqlite3

def crear_base_datos():
    # Conectar a la base de datos (se crea automáticamente si no existe)
    conexion = sqlite3.connect("gestion_usuarios/usuarios.db")
    cursor = conexion.cursor()

    # Crear la tabla de roles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL
        )
    """)

    # Crear la tabla de usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            ID TEXT PRIMARY KEY,  -- Documento de identidad como ID único
            nombre_usuario TEXT NOT NULL,
            apellido_usuario TEXT NOT NULL,
            contrasena_usuario TEXT NOT NULL,
            correo_usuario TEXT UNIQUE,  -- Correo electrónico (opcional)
            rol_id INTEGER NOT NULL,  -- Referencia a roles
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            grupo_usuario TEXT,               -- Solo para estudiantes
            ultimo_acceso TIMESTAMP,
            numero_usuario INTEGER NOT NULL,  -- Contador de usuarios
            codificacion_rostro BLOB,        -- Codificación facial del usuario en formato BLOB
            FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE CASCADE
        )
    """)

    # Insertar roles predeterminados
    roles = ["Administrador", "Profesor", "Estudiante"]
    for rol in roles:
        cursor.execute("INSERT OR IGNORE INTO roles (nombre) VALUES (?)", (rol,))

    # Guardar cambios y cerrar la conexión
    conexion.commit()
    conexion.close()
    print("Base de datos creada con roles iniciales correctamente.")

# Ejecutar la función para crear la base de datos
if __name__ == "__main__":
    crear_base_datos()
