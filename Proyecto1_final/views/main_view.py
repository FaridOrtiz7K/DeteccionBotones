import tkinter as tk
from tkinter import ttk, scrolledtext
import time
import logging

logger = logging.getLogger(__name__)

class ImageSearchView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding="10")
        self.controller = controller
        self.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Variables para los controles
        self.lote_inicial_var = tk.IntVar(value=self.controller.model.lote_inicial)
        self.lote_final_var = tk.IntVar(value=self.controller.model.lote_final)
        self.distrito_var = tk.StringVar(value=self.controller.model.distrito)
        self.delay_time_var = tk.IntVar(value=self.controller.model.delay_time)
        self.no_distrito_var = tk.BooleanVar(value=self.controller.model.no_distrito)
        
        self.create_widgets()
    
    def create_widgets(self):
        # Configuración de distrito
        distrito_frame = ttk.LabelFrame(self, text="Configuración de Distrito", padding="5")
        distrito_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(distrito_frame, text="Distrito:").grid(row=0, column=0, sticky=tk.W, padx=5)
        distrito_entry = ttk.Entry(distrito_frame, textvariable=self.distrito_var, width=20)
        distrito_entry.grid(row=0, column=1, padx=5)
        distrito_entry.bind("<FocusOut>", lambda e: self.controller.update_distrito(self.distrito_var.get()))
        
        # Checkbox para indicar si no tiene distrito
        no_distrito_check = ttk.Checkbutton(distrito_frame, text="No tiene distrito", 
                                           variable=self.no_distrito_var,
                                           command=lambda: self.controller.update_no_distrito(self.no_distrito_var.get()))
        no_distrito_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Configuración de lotes
        lote_frame = ttk.LabelFrame(self, text="Configuración de Lotes", padding="5")
        lote_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(lote_frame, text="Lote inicial:").grid(row=0, column=0, sticky=tk.W, padx=5)
        lote_inicial_spin = ttk.Spinbox(lote_frame, from_=1, to=1000, textvariable=self.lote_inicial_var, width=10)
        lote_inicial_spin.grid(row=0, column=1, padx=5)
        lote_inicial_spin.bind("<FocusOut>", lambda e: self.controller.update_lote_inicial(self.lote_inicial_var.get()))
        
        ttk.Label(lote_frame, text="Lote final:").grid(row=0, column=2, sticky=tk.W, padx=5)
        lote_final_spin = ttk.Spinbox(lote_frame, from_=1, to=1000, textvariable=self.lote_final_var, width=10)
        lote_final_spin.grid(row=0, column=3, padx=5)
        lote_final_spin.bind("<FocusOut>", lambda e: self.controller.update_lote_final(self.lote_final_var.get()))
        
        ttk.Label(lote_frame, text="Tiempo de espera (segundos):").grid(row=0, column=4, sticky=tk.W, padx=5)
        delay_spin = ttk.Spinbox(lote_frame, from_=1, to=60, textvariable=self.delay_time_var, width=5)
        delay_spin.grid(row=0, column=5, padx=5)
        delay_spin.bind("<FocusOut>", lambda e: self.controller.update_delay_time(self.delay_time_var.get()))
        
        # Botones de control
        button_frame = ttk.Frame(self)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Iniciar", command=self.controller.start_search)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.pause_button = ttk.Button(button_frame, text="Pausar", command=self.controller.pause_search, state=tk.DISABLED)
        self.pause_button.grid(row=0, column=1, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Detener", command=self.controller.stop_search, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=2, padx=5)
        
        # Área de estado
        status_frame = ttk.LabelFrame(self, text="Estado", padding="5")
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=10, width=70)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Configurar expansión de columnas
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        status_frame.columnconfigure(0, weight=1)
    
    def log_message(self, message):
        """Añade un mensaje al área de estado"""
        self.status_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.status_text.see(tk.END)
        logger.info(message)
    
    def update_button_states(self, is_running, is_paused):
        """Actualiza el estado de los botones según el estado actual"""
        if is_running:
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)
            self.pause_button.config(text="Reanudar" if is_paused else "Pausar")
        else:
            self.start_button.config(state=tk.NORMAL)
            self.pause_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.DISABLED)
            self.pause_button.config(text="Pausar")
    
    def show_pause_window(self, current_lote, total_lotes):
        """Muestra la ventana de pausa"""
        from views.pause_window import PauseWindow
        PauseWindow(self.master, self.controller, current_lote, total_lotes)