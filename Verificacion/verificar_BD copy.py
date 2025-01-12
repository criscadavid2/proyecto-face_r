import sqlite3

def verificar_estructura():
    # Conectar a la base de datos
    conexion = sqlite3.connect("gestion_asistencia/asistencia.db")
    cursor = conexion.cursor()

    # Obtener la estructura de la tabla usuarios
    cursor.execute("PRAGMA table_info(asistencia);")
    columnas = cursor.fetchall()

    for columna in columnas:
        print(columna)

    conexion.close()

# Ejecutar la función para verificar la estructura
if __name__ == "__main__":
    verificar_estructura()
