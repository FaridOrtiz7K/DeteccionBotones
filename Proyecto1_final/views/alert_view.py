import threading
import time
import winsound
import tkinter as tk
from tkinter import ttk

class ErrorDialog(tk.Toplevel):
    def __init__(self, parent, message):
        super().__init__(parent)
        self.title("Error en la secuencia")
        self.geometry("400x150")
        self.resizable(False, False)
        
        # Hacer la ventana modal
        self.grab_set()
        self.focus_set()
        
        # Contenido del diálogo
        tk.Label(self, text=message, wraplength=380, fg="red").pack(padx=20, pady=20)
        tk.Button(self, text="Aceptar", command=self.destroy).pack(pady=10)
        
        # Iniciar sonido de alerta
        self.sound_thread = threading.Thread(target=self.play_sound, daemon=True)
        self.sound_thread.start()
    
    def play_sound(self):
        """Reproduce sonido de alerta continuamente"""
        while self.winfo_exists():  # Mientras la ventana exista
            winsound.Beep(1000, 500)  # Beep a 1000Hz por 500ms
            time.sleep(0.5)  # Pausa entre beeps
    
    def destroy(self):
        # Detener el sonido al cerrar la ventana
        super().destroy()