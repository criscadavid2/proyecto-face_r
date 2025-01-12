import sqlite3
from datetime import datetime

# Conectar a la base de datos
conexion = sqlite3.connect('gestion_asistencia/asistencia.db')
cursor = conexion.cursor()

# Verificar si la columna 'ultima_asistencia' ya existe
cursor.execute("PRAGMA table_info(asistencia)")
columnas = [columna[1] for columna in cursor.fetchall()]

if 'ultima_asistencia' not in columnas:
    # Agregar la columna 'ultima_asistencia' a la tabla 'asistencias'
    cursor.execute("ALTER TABLE asistencia ADD COLUMN ultima_asistencia DATETIME")

    # Opcional: Inicializar la columna con la fecha y hora actual
    fecha_actual = datetime.now().isoformat()
    cursor.execute("UPDATE asistencia SET ultima_asistencia = ?", (fecha_actual,))

    print("Columna 'ultima_asistencia' agregada y inicializada correctamente.")
else:
    print("La columna 'ultima_asistencia' ya existe en la tabla 'asistencias'.")

# Confirmar los cambios y cerrar la conexión
conexion.commit()
conexion.close()
