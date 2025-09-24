import tkinter as tk
from tkinter import ttk, messagebox
import logging

logger = logging.getLogger(__name__)

class ConfigWindow(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.title("Configuración de Texto")
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Centrar la ventana
        self.transient(parent)
        self.grab_set()
        
        # Variable para el patrón de texto
        self.patron_texto_var = tk.StringVar(value=self.controller.model.patron_texto)
        
        self.create_widgets()
        self.load_current_settings()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuración de grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        ttk.Label(main_frame, text="Configuración del Formato para el Texto", 
                 font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Campo para el patrón de texto
        ttk.Label(main_frame, text="Patrón de texto:").grid(row=1, column=0, sticky=tk.W, pady=5)
        patron_entry = ttk.Entry(main_frame, textvariable=self.patron_texto_var, width=30)
        patron_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Texto de ayuda
        help_text = "Este texto se usará para generar los nombres de archivo KML.\nEjemplos: 'LT', 'ALM', 'Zona'"
        ttk.Label(main_frame, text=help_text, font=('Arial', 9), 
                 foreground='gray').grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Frame para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Botones
        ttk.Button(button_frame, text="Guardar", 
                  command=self.guardar_configuracion).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Restablecer", 
                  command=self.restablecer_predeterminado).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def load_current_settings(self):
        """Carga la configuración actual del modelo"""
        self.patron_texto_var.set(self.controller.model.patron_texto)
    
    def guardar_configuracion(self):
        """Guarda la configuración"""
        try:
            nuevo_patron = self.patron_texto_var.get().strip()
            
            if not nuevo_patron:
                messagebox.showerror("Error", "El formato para el texto no puede estar vacío")
                return
            
            # Actualizar el modelo
            self.controller.update_patron_texto(nuevo_patron)
            
            messagebox.showinfo("Éxito", "Configuración guardada correctamente")
            self.destroy()
            
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            messagebox.showerror("Error", f"No se pudo guardar la configuración: {e}")
    
    def restablecer_predeterminado(self):
        """Restablece los valores predeterminados"""
        self.patron_texto_var.set("LT")
        messagebox.showinfo("Información", "Valores restablecidos a 'LT'")