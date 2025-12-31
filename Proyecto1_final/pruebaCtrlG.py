# Ejemplo de uso
import time
from Proyecto1_final.utils.ahk_ctrlS import CtrlSAHKManager

ahk_manager = CtrlSAHKManager()
ahk_manager.start_ahk()

time.sleep(2)  # Esperar a que AHK inicie

# Presionar Ctrl+G 52 veces
ahk_manager.presionar_ctrl_s(2)
print("Se presionó Ctrl+G 2 veces")

# Cuando termines
ahk_manager.stop_ahk()