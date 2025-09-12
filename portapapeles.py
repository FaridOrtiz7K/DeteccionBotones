import pyautogui
import time
import pyperclip

time.sleep(3)

nombre_archivo = "LT "
for n in range(1, 2):
    # Crear el texto completo
    texto_completo = f"{nombre_archivo}{n}.kml"
    print(f"Intentando escribir: {texto_completo}")
    
    # Copiar al portapapeles
    pyperclip.copy(texto_completo)
    
    # Verificar que se copió correctamente
    texto_copiado = pyperclip.paste()
    if texto_copiado == texto_completo:
        print("Texto copiado al portapapeles correctamente")
    else:
        print(f"Error: Se copió '{texto_copiado}' en lugar de '{texto_completo}'")
    
    # Pegar usando Ctrl+V
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1)  # Esperar a que se pegue
    
    time.sleep(3)
    pyautogui.press('enter')
    time.sleep(3)