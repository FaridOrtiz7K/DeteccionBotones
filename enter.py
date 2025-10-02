import pyautogui
print("Presionando Enter una vez")
pyautogui.press('enter')
print("Presionando Enter dos veces")
pyautogui.press('enter', presses=2, interval=0.5)