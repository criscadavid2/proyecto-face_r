import tkinter as tk
import cv2
from tkinter import messagebox, StringVar, ttk, Toplevel

# Variables globales para la cámara
nombres_camaras = [] #lista de nombres de camaras disponibles

# Función para verificar si la cámara en índice 0 está disponible
def verificar_camara_predeterminada():
    """Verifica si la cámara en el índice 0 está disponible.
    
    Returns:
        bool: True si la cámara está disponible, False en caso contrario.
    """
    cap = cv2.VideoCapture(0) # Índice predeterminado 0
    disponible = cap.isOpened()  # Se guarda el resultado en una variable
    cap.release()
    return disponible  # Retornamos directamente el valor booleano

# Función para inicializar cámaras disponibles
def inicializar_camaras():
    """Inicializa las cámaras disponibles y guarda los nombres en la lista global.
    """
    global nombres_camaras
    nombres_camaras.clear()  # Limpiamos la lista antes de agregar nombres
    indices_camaras = list(range(10))  # Puedes ajustar este rango según tus necesidades
    

    for i in indices_camaras:
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            nombres_camaras.append(f"Cámara {i}")
        cap.release()

    if not nombres_camaras:
        nombres_camaras.append("No disponible")
        
#Actualizar la lista inicial de cámaras
inicializar_camaras() 

# Función para abrir configuración de cámaras
def abrir_configuracion(ventana, opcion_camara):
    """Abre la ventana de configurar la camara seleccionada.
    Args:
        ventana (tk.Tk): Ventana principal de la aplicación.
        opcion_camara (StringVar): Variable para la cámara seleccionada.
    
    """
    #Crear ventana de configuración
    configuracion_ventana = tk.Toplevel(ventana)
    configuracion_ventana.title("Configuración de Cámara")
    configuracion_ventana.geometry("400x300")

    ttk.Label(configuracion_ventana, text="Selecciona una cámara:").pack(pady=10)

    seleccion_camara = StringVar(configuracion_ventana)
    seleccion_camara.set("Cámara 0")  # Cámara predeterminada al inicio

    # Crear menu de camaras
    menu_camaras = tk.OptionMenu(configuracion_ventana, seleccion_camara, *nombres_camaras)
    menu_camaras.pack(pady=10)

#Funcion para guardar la configuración seleccionada
    def guardar_configuracion():
        opcion_camara.set(seleccion_camara.get())
        messagebox.showinfo("Configuración guardada", f"{seleccion_camara.get()} seleccionada.")
        configuracion_ventana.destroy()

    ttk.Button(configuracion_ventana, text="Guardar", command=guardar_configuracion).pack(pady=10)
    
# Función para probar la cámara seleccionada
def probar_camara(opcion_camara):
    """Prueba si la camara seleccionada funciona correctamente.
    Args:
        opcion_camara (StringVar): Variable para la cámara seleccionada.
    """
    camara_seleccionada = opcion_camara.get()
    indice_camara = int(camara_seleccionada.split()[-1])  # Extraer índice de la cámara
    
    cap = cv2.VideoCapture(indice_camara)
    if not cap.isOpened():
        messagebox.showerror("Error", "No se pudo abrir la cámara seleccionada.")
        return

    messagebox.showinfo("Prueba", f"La cámara {camara_seleccionada} funciona correctamente.")
    cap.release()



        

    


