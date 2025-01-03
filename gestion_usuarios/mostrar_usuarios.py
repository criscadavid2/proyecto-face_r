import sqlite3

#Verifica los usuarios agregados en la BD

def mostrar_usuarios():
    # Conectar a la base de datos
    conexion = sqlite3.connect("gestion_usuarios/usuarios.db")
    cursor = conexion.cursor()

    # Consultar todos los usuarios y sus roles
    cursor.execute("""
        SELECT usuarios.nombre, roles.nombre
        FROM usuarios
        JOIN roles ON usuarios.rol_id = roles.id
    """)
    usuarios = cursor.fetchall()

    # Mostrar usuarios
    for usuario in usuarios:
        print(f"Usuario: {usuario[0]}, Rol: {usuario[1]}")

    # Cerrar la conexión
    conexion.close()

# Llamar a la función para mostrar los usuarios
mostrar_usuarios()
