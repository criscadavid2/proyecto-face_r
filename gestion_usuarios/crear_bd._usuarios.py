import sqlite3

def crear_base_datos():
    # Conectar a la base de datos (se crea automáticamente si no existe)
    conexion = sqlite3.connect("gestion_asistencia/asistencia_analisis.db")
    cursor = conexion.cursor()

    # Crear la tabla de análisis de asistencias
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analisis_asistencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            ultima_asistencia DATETIME,
            asistencia_consecutiva INTEGER DEFAULT 0,
            dias_sin_llegar_tarde INTEGER DEFAULT 0,
            llegadas_tarde INTEGER DEFAULT 0,
            inasistencias INTEGER DEFAULT 0,
            inasistencias_consecutivas INTEGER DEFAULT 0,
            motivo_ausencia TEXT,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(ID)
        )
    """)

    # Guardar cambios y cerrar la conexión
    conexion.commit()
    conexion.close()
    print("Tabla de análisis de asistencias creada correctamente.")

# Ejecutar la función para crear la base de datos
if __name__ == "__main__":
    crear_base_datos()
