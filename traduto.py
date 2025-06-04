import tkinter as tk
from googletrans import Translator

def traducir():
    texto = entrada.get("1.0", tk.END).strip()
    if texto:
        traduccion = translator.translate(texto, src='es', dest='en')
        resultado.config(text=traduccion.text)

# Crear ventana
ventana = tk.Tk()
ventana.title("Traductor")

translator = Translator()

# Área de texto para entrada
entrada = tk.Text(ventana, height=5, width=40)
entrada.pack()

# Botón para traducir
boton = tk.Button(ventana, text="Traducir", command=traducir)
boton.pack()

# Etiqueta para mostrar la traducción
resultado = tk.Label(ventana, text="", font=("Arial", 12))
resultado.pack()

ventana.mainloop()
