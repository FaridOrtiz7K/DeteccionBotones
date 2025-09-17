import tkinter as tk
import logging
from controllers.image_search_controller import ImageSearchController

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("automation.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    root = tk.Tk()
    
    # Intentar cargar el icono
    try:
        root.iconbitmap("icon.ico")
    except:
        logger.warning("No se pudo cargar el icono de la aplicación")
        
    app = ImageSearchController(root)
    root.mainloop()