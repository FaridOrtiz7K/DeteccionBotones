# Ejemplo de uso
from utils.ahk_ctrlG import CtrlGAHKManager

ahk_manager = CtrlGAHKManager()
ahk_manager.start_ahk()

# Presionar Ctrl+G 5 veces
ahk_manager.presionar_ctrl_g(2)

# Cuando termines
ahk_manager.stop_ahk()