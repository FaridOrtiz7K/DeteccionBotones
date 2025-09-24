import json
import os
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.default_config = {
            "lote_inicial": 1,
            "lote_final": 1,
            "delay_time": 2,
            "current_lote": 1,
            "confianza_minima": 0.68,
            "max_intentos": 30,
            "username": "admin",
            "password": "123",
            "formato_texto": "LT"  # Nuevo campo para el formato de texto
        }
        self.config = self.default_config.copy()
        
    def load(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                    logger.info("Configuración cargada correctamente")
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            
    def save(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            logger.info("Configuración guardada correctamente")
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            
    def get(self, key, default=None):
        return self.config.get(key, default)
        
    def set(self, key, value):
        self.config[key] = value
        self.save()