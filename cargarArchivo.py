import pyautogui
import time
import pyperclip
import cv2
import numpy as np

def encontrar_ventana_archivo():
    """Busca la ventana de archivo usando template matching"""
    # Capturar pantalla completa
    screenshot = pyautogui.screenshot()
    pantalla = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # Cargar template de la ventana de archivo
    template = cv2.imread('cargarArchivo.png')
    if template is None:
        print("Error: No se pudo cargar la imagen 'cargarArchivo.png'")
        return None
    
    # Realizar template matching
    result = cv2.matchTemplate(pantalla, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    
    # Umbral de confianza
    confianza_minima = 0.8
    if max_val < confianza_minima:
        print(f"Ventana no encontrada. Mejor coincidencia: {max_val:.2f}")
        return None
    
    print(f"Ventana encontrada con confianza: {max_val:.2f}")
    return max_loc  # Devuelve las coordenadas (x, y) de la esquina superior izquierda

# Esperar inicial
time.sleep(1)

# Buscar la ventana de archivo
coordenadas_ventana = encontrar_ventana_archivo()

if coordenadas_ventana:
    x_ventana, y_ventana = coordenadas_ventana
    print(f"Coordenadas ventana: x={x_ventana}, y={y_ventana}")
    
    # Calcular coordenadas del campo de texto
    x_campo = x_ventana + 223
    y_campo = y_ventana + 405
    print(f"Coordenadas campo texto: x={x_campo}, y={y_campo}")
    
    # Hacer clic en el campo de texto
    pyautogui.click(x_campo, y_campo)
    time.sleep(1)
    
    nombre_archivo = "LT "
    for n in range(1, 2):
        texto_completo = f"{nombre_archivo}{n}.kml"
        print(f"Escribiendo: {texto_completo}")
        
        # Limpiar el campo primero (opcional pero recomendado)
        pyautogui.hotkey('ctrl', 'a')  # Seleccionar todo
        pyautogui.press('delete')      # Borrar
        time.sleep(0.5)
        
        # Usar portapapeles
        pyperclip.copy(texto_completo)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)
        
        # Verificar que se pegó correctamente
        texto_pegado = pyperclip.paste()
        if texto_pegado == texto_completo:
            print("Texto pegado correctamente")
        else:
            print(f"Error al pegar. Esperado: '{texto_completo}', Obtenido: '{texto_pegado}'")
        
        time.sleep(2)
        pyautogui.press('enter')
        time.sleep(2)
else:
    print("No se pudo encontrar la ventana de archivo. Verifica:")
    print("1. Que la ventana esté visible")
    print("2. Que la imagen 'cargarArchivo.png' esté en el directorio correcto")
    print("3. Que la ventana no esté minimizada o cubierta")