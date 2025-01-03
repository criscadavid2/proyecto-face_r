import sqlite3

def mostrar_datos():
    conexion = sqlite3.connect('gestion_usuarios/usuarios.db')
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre_usuario, apellido_usuario, numero_usuario FROM usuarios")
    usuarios = cursor.fetchall()
    for usuario in usuarios:
        print(usuario)
    conexion.close()

mostrar_datos()
