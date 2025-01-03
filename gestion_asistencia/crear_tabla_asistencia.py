import sqlite3

def crear_tabla_asistencia():
    # Conectar a la base de datos
    conexion = sqlite3.connect('asistencia/asistencia.db')
    cursor = conexion.cursor()

    # Crear la tabla de asistencia
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS asistencia (
        id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Identificador único para cada registro de asistencia
        usuario_id INTEGER,                    -- ID del usuario que se refiere a la tabla 'usuarios'
        grupo TEXT,                             -- Grupo al que pertenece el usuario en ese momento
        fecha DATETIME,                         -- Fecha y hora de la asistencia
        estado TEXT,                            -- Estado de la asistencia (Presente, Ausente, etc.)
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)  -- Referencia a la tabla usuarios
    );
    ''')

    # Confirmar los cambios y cerrar la conexión
    conexion.commit()
    conexion.close()

# Llamar a la función para crear la tabla
crear_tabla_asistencia()
