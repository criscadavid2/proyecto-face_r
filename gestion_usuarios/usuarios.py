import tkinter as tk
from tkinter import messagebox, ttk
import bcrypt
import re  # Validación de correo electrónico
from utils import conectar_bd_usuarios
import datetime
import sqlite3
from utils import conectar_bd_usuarios, ejecutar_consulta_usuarios

#Validaiones para el registro de usuarios
def validar_correo(correo):
    """Función simple para validar formato de correo."""
    return "@" in correo and "." in correo

def validar_usuario(cedula):
    # Validar que la cédula sea solo números
    return cedula.isdigit()

def validar_contrasena(contrasena):
    """Valida que la contraseña tenga al menos 8 caracteres."""
    return len(contrasena) >= 8


#---------------------------------

def registrar_nuevo_usuario(ventana_principal):  # Abrir ventana de registro
    print("[Debug] Abriendo ventana de registrar_nuevo_usuario")
    """Abre la ventana de registro de un nuevo usuario."""
    #Crea ventana de registro
    registro_ventana = tk.Toplevel(ventana_principal)
    registro_ventana.title("Registrar Nuevo Usuario")
    registro_ventana.geometry("400x400")

    # Crear etiquetas y campos de entrada
    tk.Label(registro_ventana, text="ID (Cédula):").grid(row=0, column=0, padx=10, pady=10)
    tk.Label(registro_ventana, text="Nombres:").grid(row=1, column=0, padx=10, pady=10)
    tk.Label(registro_ventana, text="Apellidos:").grid(row=2, column=0, padx=10, pady=10)
    tk.Label(registro_ventana, text="Contraseña:").grid(row=3, column=0, padx=10, pady=10)
    tk.Label(registro_ventana, text="Correo electrónico:").grid(row=4, column=0, padx=10, pady=10)
    tk.Label(registro_ventana, text="Rol:").grid(row=5, column=0, padx=10, pady=10)
    tk.Label(registro_ventana, text="Grupo (solo estudiantes):").grid(row=6, column=0, padx=10, pady=10)

    entry_id = tk.Entry(registro_ventana)
    entry_id.grid(row=0, column=1, padx=10, pady=10)

    entry_nombre = tk.Entry(registro_ventana)
    entry_nombre.grid(row=1, column=1, padx=10, pady=10)

    entry_apellidos = tk.Entry(registro_ventana)
    entry_apellidos.grid(row=2, column=1, padx=10, pady=10)

    entry_contrasena = tk.Entry(registro_ventana, show="*")
    entry_contrasena.grid(row=3, column=1, padx=10, pady=10)

    entry_correo = tk.Entry(registro_ventana)
    entry_correo.grid(row=4, column=1, padx=10, pady=10)

    combo_rol = ttk.Combobox(registro_ventana, values=["Administrador", "Profesor", "Estudiante"])
    combo_rol.grid(row=5, column=1, padx=10, pady=10)

    entry_grupo = tk.Entry(registro_ventana)  # Solo para estudiantes
    entry_grupo.grid(row=6, column=1, padx=10, pady=10)

    #Funcion para guardar usuarios en la base de datos
    def guardar_usuario():
        """Valida y guarda un nuevo usuario en la base de datos"""
        id_usuario = entry_id.get().strip()
        nombre = entry_nombre.get().strip()
        apellidos = entry_apellidos.get().strip()
        contrasena = entry_contrasena.get().strip()
        correo = entry_correo.get().strip()
        grupo = entry_grupo.get()  # Para estudiantes
        rol = combo_rol.get()

    #---Validacioones--------
       
        # Validación de cédula
        if not id_usuario.isdigit():
            messagebox.showerror("Error", "La cédula debe contener solo números.")
            return

        # Validación de contraseña
        if len(contrasena) < 8:
            messagebox.showerror("Error", "La contraseña debe tener al menos 8 caracteres.")
            return
        
        #validacion de correo
        if not validar_correo(correo):
            messagebox.showerror("Error", "Formato de correo electronico invalido.")
            return
        
        #Validacion de nombre y apellido
        if not nombre or not apellidos or not contrasena:
            messagebox.showerror("Error", "Por favor, complete todos los campos obligatorios.")
            return
        
        if rol == "Estudiante" and not grupo:
            messagebox.showerror("Error", "Debe ingresar el grado del estudiante.")
            return
        
        #Conectar la BD para verificar que la cedula ya existe 
        conexion, cursor = conectar_bd_usuarios() # Usamos la función para conectar y obtener el cursor
        if conexion is None:
            return
        
        #Realiza las operaciones de la base de datos aqui
        try:
            #Obtener el último numero_usuario
            try:
                cursor.execute("SELECT MAX(numero_usuario) FROM usuarios")
                resultado = cursor.fetchone()
                nuevo_numero = 1 if resultado is None or resultado[0] is None else resultado[0] + 1
                print(f"[Debug] Nuevo número de usuario: {nuevo_numero}")
            except sqlite3.Error as e:
                messagebox.showerror("Error al consultar la base de datos", f"Error: {e}")
                return


            # Verificar si el ID ( la cédula) ya existe en la BD
            query ="SELECT * FROM usuarios WHERE id = ?"
            cursor.execute (query, (id_usuario,))
            resultado = cursor.fetchone()
            if resultado:
                messagebox.showerror("Error", "Ya existe un usuario con esta cédula.")
                return 

            # Obtener el rol_id basado en el nombre del rol
            cursor.execute("SELECT id FROM roles WHERE nombre = ?", (rol,))
            rol_id_tuple = cursor.fetchone() #se guarda el resutlado en una variable

            if rol_id_tuple is None: #Se verifica si rol id es None
                messagebox.showerror("Error", "Rol no válido.")
                return
            rol_id = rol_id_tuple[0] #extraer el id de la tupla
            
            
            # Hash de la contraseña ANTES de guardarla
            hashed_password = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())

            #Obtener la fecha y hora actual en formato ISO 8601
            fecha_registro = datetime.datetime.now().isoformat()

            # Insertar nuevo usuario en la base de datos            

            cursor.execute("""
                INSERT INTO usuarios (
                    id,
                    nombre_usuario,
                    apellido_usuario,
                    contrasena_usuario,
                    correo_usuario,
                    rol_id,
                    fecha_registro,
                    grupo_usuario,
                    numero_usuario,
                    ultimo_acceso,
                    codificacion_rostro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,  
            (
                id_usuario, nombre, apellidos, hashed_password, correo, rol_id, fecha_registro, grupo if rol == "Estudiante" else None, nuevo_numero, None ,None)
            )
            conexion.commit()
            messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
            registro_ventana.destroy()

        except sqlite3.Error as e:
            messagebox.showerror("Error de base de datos usuarios", f"Error al registrar usuario: {e}")
            print(f"Error de base de datos usuarios: {e}")
            conexion.rollback() #Rollback  en caso de error
        finally:
            conexion.close()  # Aseguramos de cerrar la conexión en caso de error


# Botón para registrar el nuevo usuario
    registrar_btn = ttk.Button(registro_ventana, text="Registrar", command=guardar_usuario)
    registrar_btn.grid(row=7, column=1, padx=10, pady=10)



