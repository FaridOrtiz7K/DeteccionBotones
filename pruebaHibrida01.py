import cv2
import numpy as np
import pyautogui
import time
import subprocess
import os

def encontrar_ventana_archivo():
    """Busca la ventana de archivo usando template matching"""
    # Capturar pantalla completa
    screenshot = pyautogui.screenshot()
    pantalla = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # Cargar template de la ventana de archivo
    template = cv2.imread('img/cargarArchivo.png')
    if template is None:
        print("Error: No se pudo cargar la imagen 'cargarArchivo.png'")
        return None
    
    # Realizar template matching
    result = cv2.matchTemplate(pantalla, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    # Umbral de confianza
    confianza_minima = 0.6
    if max_val < confianza_minima:
        print(f"Ventana no encontrada. Mejor coincidencia: {max_val:.2f}")
        return None
    
    print(f"Ventana encontrada con confianza: {max_val:.2f}")
    return max_loc  # Devuelve las coordenadas (x, y) de la esquina superior izquierda

def ejecutar_acciones_ahk(x_campo, y_campo, nombre_archivo):
    """Envía comandos a AutoHotkey mediante archivo temporal"""
    # Crear archivo de comandos para AHK
    comando = f"{x_campo},{y_campo},{nombre_archivo}"
    
    with open("ahk_command.txt", "w") as f:
        f.write(comando)
    
    print(f"Comando enviado a AHK: {comando}")

def crear_script_ahk():
    """Crea automáticamente el script de AutoHotkey"""
    ahk_script = """
#Persistent
#SingleInstance force

; Script de AutoHotkey para manejar acciones de UI
Loop {
    ; Esperar comandos de Python
    FileRead, comando, ahk_command.txt
    if (ErrorLevel = 0) {
        FileDelete, ahk_command.txt
        
        ; Parsear comando: x,y,filename
        Array := StrSplit(comando, ",")
        x_campo := Array[1]
        y_campo := Array[2]
        nombre_archivo := Array[3]
        
        ; Ejecutar acciones
        Click, %x_campo% %y_campo%
        Sleep, 300
        
        ; Limpiar campo
        Send, ^a
        Sleep, 100
        Send, {Delete}
        Sleep, 100
        
        ; Escribir nombre de archivo (método confiable)
        SendInput, %nombre_archivo%
        Sleep, 300
        
        ; Presionar Enter
        Send, {Enter}
        Sleep, 1000
        
        ; Confirmación para Python
        FileAppend, done, ahk_done.txt
        FileDelete, ahk_done.txt
    }
    Sleep, 500  ; Revisar cada medio segundo
}
"""
    with open("ahk_script.ahk", "w", encoding="utf-8") as f:
        f.write(ahk_script)
    print("Script de AutoHotkey creado automáticamente")

# Esperar inicial
time.sleep(2)

# Buscar la ventana de archivo
coordenadas_ventana = encontrar_ventana_archivo()

if coordenadas_ventana:
    x_ventana, y_ventana = coordenadas_ventana
    print(f"Coordenadas ventana: x={x_ventana}, y={y_ventana}")
    
    # Calcular coordenadas del campo de texto
    x_campo = x_ventana + 294
    y_campo = y_ventana + 448
    print(f"Coordenadas campo texto: x={x_campo}, y={y_campo}")
    
    # Ejecutar AutoHotkey si no está corriendo
    if not os.path.exists("ahk_script.ahk"):
        crear_script_ahk()  # Crear el script automáticamente
    
    # Iniciar AHK si no está corriendo
    try:
        subprocess.Popen(['AutoHotkey.exe', 'ahk_script.ahk'])
        time.sleep(2)
    except:
        print("AutoHotkey no encontrado, asegúrate de tenerlo instalado")
    
    # Enviar comandos a AHK
    for n in range(1, 2):
        nombre_archivo = f"LT {n}.kml"
        ejecutar_acciones_ahk(x_campo, y_campo, nombre_archivo)
        time.sleep(3)  # Esperar a que AHK complete la acción
        
else:
    print("No se pudo encontrar la ventana de archivo.")

