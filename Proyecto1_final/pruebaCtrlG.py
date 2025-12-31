# Ejemplo de uso
import time
from utils.ahk_ctrlG import CtrlGAHKManager

ahk_manager = CtrlGAHKManager()
ahk_manager.start_ahk()

time.sleep(2)  # Esperar a que AHK inicie

# Presionar Ctrl+G 52 veces
ahk_manager.presionar_ctrl_g(2)
print("Se presionó Ctrl+G 2 veces")

# Cuando termines
ahk_manager.stop_ahk()