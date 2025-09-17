import threading
import time
import pyautogui
import cv2
import numpy as np
from PIL import Image
import os
import logging
from utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class ImageSearchModel:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.config_manager.load()
        
        self.is_running = False
        self.is_paused = False
        self.pause_event = threading.Event()
        self.pause_condition = threading.Condition()
        self.observers = []
        self.alt_n_used = False
        
        # Secuencia predefinida de imágenes
        self.image_sequence = [
            ("img/b1.png", 1, self.config_manager.get("confianza_minima", 0.68)),
            ("img/b2.png", 1, self.config_manager.get("confianza_minima", 0.68)),
            ("img/b3.png", 1, self.config_manager.get("confianza_minima", 0.68)),
            ("img/b4.png", 1, self.config_manager.get("confianza_minima", 0.68)),
            ("img/b1.png", 1, self.config_manager.get("confianza_minima", 0.68)),
            ("img/b6.png", 1, self.config_manager.get("confianza_minima", 0.68)),
            ("img/b7.png", 1, self.config_manager.get("confianza_minima", 0.68)),
            ("img/b8.png", 1, self.config_manager.get("confianza_minima", 0.68))
        ]
    
    def add_observer(self, observer):
        self.observers.append(observer)
    
    def notify_observers(self, event, data=None):
        for observer in self.observers:
            observer.update(event, data)
    
    def set_configurable(self, key, value):
        """Método genérico para establecer valores configurables"""
        old_value = self.config_manager.get(key)
        if old_value != value:
            self.config_manager.set(key, value)
            self.notify_observers(f"{key}_changed", value)
    
    def set_running(self, running):
        self.is_running = running
        self.notify_observers("running_changed", running)
    
    def set_paused(self, paused):
        self.is_paused = paused
        self.notify_observers("paused_changed", paused)
    
    # Propiedades para acceso directo a configuraciones comunes
    @property
    def lote_inicial(self):
        return self.config_manager.get("lote_inicial", 1)
    
    @lote_inicial.setter
    def lote_inicial(self, value):
        self.set_configurable("lote_inicial", value)
    
    @property
    def lote_final(self):
        return self.config_manager.get("lote_final", 1)
    
    @lote_final.setter
    def lote_final(self, value):
        self.set_configurable("lote_final", value)
    
    @property
    def distrito(self):
        return self.config_manager.get("distrito", "")
    
    @distrito.setter
    def distrito(self, value):
        self.set_configurable("distrito", value)
    
    @property
    def delay_time(self):
        return self.config_manager.get("delay_time", 2)
    
    @delay_time.setter
    def delay_time(self, value):
        self.set_configurable("delay_time", value)
    
    @property
    def current_lote(self):
        return self.config_manager.get("current_lote", 1)
    
    @current_lote.setter
    def current_lote(self, value):
        self.set_configurable("current_lote", value)
    
    @property
    def no_distrito(self):
        return self.config_manager.get("no_distrito", False)
    
    @no_distrito.setter
    def no_distrito(self, value):
        self.set_configurable("no_distrito", value)
    
    
    @property
    def confianza_minima(self):
        return self.config_manager.get("confianza_minima", 0.68)
    
    def click_button(self, imagen, clicks=1, confianza_minima=None):
        """
        Busca un botón en pantalla y hace clic en él
        
        Args:
            imagen (str): Ruta de la imagen del botón a buscar
            clicks (int): Número de clics a realizar
            confianza_minima (float): Umbral de confianza para la detección (0-1)
        
        Returns:
            bool: True si encontró el botón, False en caso contrario
        """
        if confianza_minima is None:
            confianza_minima = self.confianza_minima
            
        intentos = 1
        tiempo_entre_intentos = 1
        tiempo_entre_lotes = 10
        
        while self.is_running:
            # Verificar si está pausado
            if self.is_paused:
                with self.pause_condition:
                    while self.is_paused and self.is_running:
                        self.pause_condition.wait()
                if not self.is_running:
                    return False
            
            # Obtener dimensiones de la pantalla
            ancho_pantalla, alto_pantalla = pyautogui.size()
            vm_region = (0, 0, ancho_pantalla, alto_pantalla)

            # Capturar pantalla
            screenshot = pyautogui.screenshot(region=vm_region)
            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            # Cargar template
            template = cv2.imread(imagen)
            if template is None:
                self.notify_observers("error", f"No se pudo cargar la imagen '{imagen}'. Verifica la ruta y el formato.")
                return False

            h, w = template.shape[:2]

            # Buscar el botón
            result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val > confianza_minima:
                # Calcular centro del botón
                center_x = vm_region[0] + max_loc[0] + w//2
                center_y = vm_region[1] + max_loc[1] + h//2
                
                # Esperar 2.5 segundos antes de hacer clic
                time.sleep(2.5)
                
                # Realizar clic
                pyautogui.moveTo(center_x, center_y)
                pyautogui.click(clicks=clicks)
                
                self.notify_observers("image_found", {
                    "image": imagen,
                    "x": center_x,
                    "y": center_y,
                    "confidence": max_val
                })
                return True
            else:
                if intentos % 10 == 0:
                    logger.info(f"Intento {intentos}: Mejor coincidencia: {max_val:.2f}")
                    time.sleep(tiempo_entre_lotes)
                else:
                    time.sleep(tiempo_entre_intentos)
                    
                intentos += 1
                self.notify_observers("image_not_found", {
                    "image": imagen,
                    "confidence": max_val,
                    "intento": intentos
                })
        
        return False