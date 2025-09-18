import tkinter as tk
from tkinter import ttk
import logging

logger = logging.getLogger(__name__)

class PauseWindow(tk.Toplevel):
    def __init__(self, parent, controller, current_lote, total_lotes):
        super().__init__(parent)
        self.controller = controller
        self.title("Proceso en Pausa")
        self.geometry("300x200")
        self.resizable(False, False)
        
        # Hacer la ventana modal
        self.transient(parent)
        self.grab_set()
        
        # Centrar la ventana
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        #hacer que la ventana esté siempre encima
        self.attributes("-topmost", True)
        
        # Configurar el protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Variables
        self.countdown = 5
        self.countdown_running = False
        
        # Crear widgets
        self.create_widgets(current_lote, total_lotes)
    
    def create_widgets(self, current_lote, total_lotes):
        # Frame principal
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Información de progreso
        lotes_faltantes = total_lotes - current_lote + 1
        ttk.Label(main_frame, text=f"Lote actual: {current_lote}").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text=f"Lotes completados: {current_lote - 1}").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text=f"Lotes faltantes: {lotes_faltantes}").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text=f"Total de lotes: {total_lotes}").grid(row=3, column=0, sticky=tk.W, pady=5)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, pady=10)
        
        self.resume_button = ttk.Button(button_frame, text="Reanudar (5)", 
                                       command=self.start_countdown)
        self.resume_button.grid(row=0, column=0, padx=5)
        
        self.exit_button = ttk.Button(button_frame, text="Salir", 
                                     command=self.controller.stop_search)
        self.exit_button.grid(row=0, column=1, padx=5)
        
        # Configurar expansión
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
    
    def start_countdown(self):
        """Inicia la cuenta regresiva para reanudar"""
        if not self.countdown_running:
            self.countdown_running = True
            self.resume_button.config(state=tk.DISABLED)
            self.update_countdown()
    
    def update_countdown(self):
        """Actualiza la cuenta regresiva"""
        if self.countdown > 0 and self.countdown_running:
            self.resume_button.config(text=f"Reanudar ({self.countdown})")
            self.countdown -= 1
            self.after(1000, self.update_countdown)
        elif self.countdown_running:
            logger.info("Reanudando proceso desde ventana de pausa")
            self.controller.resume_search()
            self.destroy()
    
    def on_close(self):
        """Maneja el cierre de la ventana"""
        self.countdown_running = False
        self.destroy()