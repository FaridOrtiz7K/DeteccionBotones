import pyautogui
import cv2
import numpy as np
import time

def click_button(imagen, clicks=1, confianza_minima=0.6):
    """
    Busca un botón en pantalla y hace clic en él
    
    Args:
        imagen (str): Ruta de la imagen del botón a buscar
        clicks (int): Número de clics a realizar
        confianza_minima (float): Umbral de confianza para la detección (0-1)
    
    Returns:
        bool: True si encontró el botón, False en caso contrario
    """
    # Obtener dimensiones de la pantalla
    ancho_pantalla, alto_pantalla = pyautogui.size()
    vm_region = (0, 0, ancho_pantalla, alto_pantalla)

    # Capturar pantalla
    screenshot = pyautogui.screenshot(region=vm_region)
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Cargar template
    template = cv2.imread(imagen)
    if template is None:
        raise ValueError(f"No se pudo cargar la imagen '{imagen}'. Verifica la ruta y el formato.")

    h, w = template.shape[:2]

    # Buscar el botón
    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val > confianza_minima:
        # Calcular centro del botón
        center_x = vm_region[0] + max_loc[0] + w//2
        center_y = vm_region[1] + max_loc[1] + h//2
        
        # Realizar clic
        pyautogui.moveTo(center_x, center_y)
        pyautogui.click(clicks=clicks)
        
        print(f"Botón encontrado en ({center_x}, {center_y}) - Confianza: {max_val:.2f}")
        return True
    else:
        print(f"Botón no encontrado. Mejor coincidencia: {max_val:.2f}")
        return False

# Ejemplo de uso:
if __name__ == "__main__":
    click_button("img/b1.png", clicks=2, confianza_minima=0.7) #la confianza minima debe de rondar de 0.6-0.8 en procesamiento de imagenes  
    time.sleep(2) #Espera de 2 segundos 
    click_button("img/b2.png", clicks=1, confianza_minima=0.7)
    time.sleep(2) #Espera de 2 segundos 
    click_button("img/b3.png", clicks=1, confianza_minima=0.7)
    time.sleep(2) #Espera de 2 segundos 
    click_button("img/b4.png", clicks=2, confianza_minima=0.7)
    time.sleep(2) #Espera de 2 segundos 
    click_button("img/b5.png", clicks=1, confianza_minima=0.7)
    time.sleep(2) #Espera de 2 segundos 
    click_button("img/b6.png", clicks=1, confianza_minima=0.7)