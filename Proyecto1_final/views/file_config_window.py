import tkinter as tk
from tkinter import ttk, messagebox
import logging

logger = logging.getLogger(__name__)

class FileConfigWindow(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.title("Configuración de Nombres de Archivo")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Centrar la ventana
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        # Hacer la ventana modal
        self.transient(parent)
        self.grab_set()
        
        # Variables
        self.prefijo_var = tk.StringVar(value=self.controller.model.config_manager.get("archivo_prefix", "LT"))
        self.formato_var = tk.StringVar(value=self.controller.model.config_manager.get("archivo_formato", "{prefix} {lote}.kml"))
        
        self.create_widgets()
        
        # Enfocar la ventana
        self.after(100, lambda: self.focus_force())
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        ttk.Label(main_frame, text="Configuración de Nombres de Archivo", 
                 font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Información
        info_text = "Configure el formato del nombre de archivo para los lotes.\nEl sistema usará este formato para generar los nombres automáticamente."
        ttk.Label(main_frame, text=info_text, justify=tk.LEFT).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Configuración del prefijo
        ttk.Label(main_frame, text="Prefijo:").grid(row=2, column=0, sticky=tk.W, pady=10)
        prefijo_entry = ttk.Entry(main_frame, textvariable=self.prefijo_var, width=20)
        prefijo_entry.grid(row=2, column=1, padx=10, pady=10, sticky=tk.W)
        ttk.Label(main_frame, text="Ejemplo: LT, Lote, Parcela, etc.").grid(row=3, column=1, sticky=tk.W, padx=10)
        
        # Configuración del formato
        ttk.Label(main_frame, text="Formato del archivo:").grid(row=4, column=0, sticky=tk.W, pady=10)
        formato_entry = ttk.Entry(main_frame, textvariable=self.formato_var, width=30)
        formato_entry.grid(row=4, column=1, padx=10, pady=10, sticky=tk.W)
        
        # Variables disponibles
        vars_frame = ttk.LabelFrame(main_frame, text="Variables Disponibles", padding="5")
        vars_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        vars_text = """• {prefix} - Será reemplazado por el prefijo configurado
• {lote} - Será reemplazado por el número de lote actual
• {lote_inicial} - Número de lote inicial
• {lote_final} - Número de lote final"""
        
        ttk.Label(vars_frame, text=vars_text, justify=tk.LEFT).grid(row=0, column=0, sticky=tk.W)
        
        # Ejemplo en tiempo real
        ejemplo_frame = ttk.LabelFrame(main_frame, text="Ejemplo Actual", padding="5")
        ejemplo_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.ejemplo_var = tk.StringVar()
        self.actualizar_ejemplo()
        ttk.Label(ejemplo_frame, textvariable=self.ejemplo_var, font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W)
        
        # Track changes para actualizar ejemplo en tiempo real
        self.prefijo_var.trace('w', lambda *args: self.actualizar_ejemplo())
        self.formato_var.trace('w', lambda *args: self.actualizar_ejemplo())
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Guardar", command=self.guardar_configuracion).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Restablecer por Defecto", command=self.restablecer_default).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.destroy).grid(row=0, column=2, padx=5)
        
        # Configurar expansión
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def actualizar_ejemplo(self):
        """Actualiza el ejemplo en tiempo real"""
        try:
            formato = self.formato_var.get()
            prefijo = self.prefijo_var.get()
            
            # Reemplazar variables en el formato
            ejemplo = formato.replace("{prefix}", prefijo)
            ejemplo = ejemplo.replace("{lote}", "5")
            ejemplo = ejemplo.replace("{lote_inicial}", "1")
            ejemplo = ejemplo.replace("{lote_final}", "10")
            
            self.ejemplo_var.set(f"Lote 5: {ejemplo}")
        except:
            self.ejemplo_var.set("Error en el formato")
    
    def guardar_configuracion(self):
        """Guarda la configuración del nombre de archivo"""
        try:
            prefijo = self.prefijo_var.get().strip()
            formato = self.formato_var.get().strip()
            
            if not prefijo:
                messagebox.showerror("Error", "El prefijo no puede estar vacío")
                return
            
            if not formato:
                messagebox.showerror("Error", "El formato no puede estar vacío")
                return
            
            # Validar que el formato contenga las variables necesarias
            if "{prefix}" not in formato or "{lote}" not in formato:
                messagebox.showerror("Error", "El formato debe contener {prefix} y {lote}")
                return
            
            # Guardar en la configuración
            self.controller.model.config_manager.set("archivo_prefix", prefijo)
            self.controller.model.config_manager.set("archivo_formato", formato)
            
            messagebox.showinfo("Éxito", "Configuración guardada correctamente")
            self.destroy()
            
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            messagebox.showerror("Error", f"No se pudo guardar la configuración: {str(e)}")
    
    def restablecer_default(self):
        """Restablece los valores por defecto"""
        self.prefijo_var.set("LT")
        self.formato_var.set("{prefix} {lote}.kml")