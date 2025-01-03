import sqlite3

def renombrar_columna():
    try:
        # Conectar a la base de datos
        conexion = sqlite3.connect("gestion_usuarios/usuarios.db")
        cursor = conexion.cursor()

        # Crear una nueva tabla con el nombre de columna modificado
        cursor.execute('''
            CREATE TABLE usuarios_nueva (
                id INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                grupo TEXT,  -- Nuevo nombre de la columna
                codificacion_rostro BLOB
            );
        ''')

        # Copiar los datos de la tabla original a la nueva tabla
        cursor.execute('''
            INSERT INTO usuarios_nueva (id, nombre, grupo, codificacion_rostro)
            SELECT id, nombre, grado, codificacion_rostro
            FROM usuarios;
        ''')

        # Eliminar la tabla original
        cursor.execute('DROP TABLE usuarios;')

        # Renombrar la nueva tabla para que tenga el nombre original
        cursor.execute('ALTER TABLE usuarios_nueva RENAME TO usuarios;')

        # Confirmar los cambios
        conexion.commit()
        print("El campo 'grado' se renombró exitosamente a 'grupo'.")

    except sqlite3.Error as e:
        print(f"Error al renombrar la columna: {e}")

    finally:
        # Cerrar la conexión
        if conexion:
            conexion.close()

# Llamar a la función
renombrar_columna()
