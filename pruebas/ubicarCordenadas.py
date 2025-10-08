import pyautogui
import time

print("Mueve el mouse al campo de texto y espera 3 segundos...")
time.sleep(3)
x, y = pyautogui.position()
print(f"Coordenadas: x={x}, y={y}")