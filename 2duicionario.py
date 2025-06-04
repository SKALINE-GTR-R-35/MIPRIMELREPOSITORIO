import tkinter as tk
from googletrans import Translator
import pygame
from gtts import gTTS
from tkinter import messagebox
import os
import threading # Necesario para la reproducción de audio en un hilo separado
from PIL import Image, ImageTk # Necesario para poner imágenes en Tkinter

# --- Configuración global y constantes ---
AUDIO_TEMP_FILE = "temp_translation_audio.mp3"
translator = Translator() # Instancia global del traductor

# --- Funciones de Audio y Pygame ---
def init_pygame_mixer():
    """Inicializa el mezclador de Pygame si no está ya inicializado."""
    if not pygame.mixer.get_init():
        pygame.mixer.init()
        print("Mezclador de Pygame inicializado.")

def play_audio_pygame(audio_filepath):
    """Reproduce un archivo de audio usando Pygame."""
    init_pygame_mixer()

    if not os.path.exists(audio_filepath):
        print(f"Error: Archivo de audio no encontrado en {audio_filepath}")
        return

    try:
        pygame.mixer.music.load(audio_filepath)
        pygame.mixer.music.play()
        print(f"Reproduciendo: {audio_filepath}")
        # Esperar a que el audio termine de reproducirse
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10) # Pequeña pausa para no consumir CPU
        print("Reproducción de audio terminada.")
    except pygame.error as e:
        print(f"Error al reproducir audio con Pygame: {e}")
    finally:
        # Detener y descargar la música para liberar el archivo si es necesario
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        # pygame.mixer.music.unload() # Descomentar si quieres liberar el archivo inmediatamente

def generate_and_play_audio(text_to_speak, lang):
    """Genera audio con gTTS y lo reproduce con Pygame en un hilo."""
    if not text_to_speak:
        print("No hay texto para generar audio.")
        return

    try:
        tts = gTTS(text=text_to_speak, lang=lang, slow=False)
        tts.save(AUDIO_TEMP_FILE)
        print(f"Audio generado y guardado en {AUDIO_TEMP_FILE}")
        # Reproducir el audio en un hilo para no bloquear la GUI
        audio_thread = threading.Thread(target=play_audio_pygame, args=(AUDIO_TEMP_FILE,))
        audio_thread.start()
    except Exception as e:
        messagebox.showerror("Error de Audio", f"No se pudo generar o reproducir el audio: {e}")


# --- Funciones de Tkinter ---

def traducir(idioma):
    """Traduce el texto de la entrada principal."""
    texto_original = entrada.get("1.0", tk.END).strip()
    if texto_original:
        traduccion_obj = translator.translate(texto_original, src='es', dest=idioma)
        translated_text = traduccion_obj.text
        resultado.config(text=translated_text)
        # Guarda la traducción actual para usarla en la segunda ventana
        ventana.last_translated_text = translated_text
        ventana.last_translated_lang = idioma
    else:
        resultado.config(text="Por favor, introduce texto para traducir.")
        ventana.last_translated_text = "" # Limpiar si no hay texto

def abrir_segunda_ventana():
    """Abre la segunda ventana de Tkinter con imagen y opción de audio."""
    segunda_ventana = tk.Toplevel(ventana) # Toplevel crea una nueva ventana, no un widget dentro de la principal
    segunda_ventana.title("Detalles de Traducción y Audio")
    segunda_ventana.geometry("500x550")
    segunda_ventana.resizable(False, False)

    # --- Mostrar Imagen ---
    try:
        #la 'imagen_fondo.png' (o .jpg) esté en el mismo directorio
        img_path = "papu.jpeg"
        img_pillow = Image.open(img_path)
        # Redimensiona la imagen para que encaje bien en la ventana secundaria
        img_pillow = img_pillow.resize((400, 300), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img_pillow)

        label_img = tk.Label(segunda_ventana, image=img_tk)
        label_img.pack(pady=10)
        label_img.image = img_tk # IMPORTANTE: Mantener referencia a la imagen
    except FileNotFoundError:
        messagebox.showerror("Error de Imagen", f"No se encontró el archivo de imagen: {img_path}")
        label_img = tk.Label(segunda_ventana, text="Imagen no encontrada.")
        label_img.pack(pady=10)
    except Exception as e:
        messagebox.showerror("Error de Imagen", f"Error al cargar la imagen: {e}")
        label_img = tk.Label(segunda_ventana, text="Error al cargar imagen.")
        label_img.pack(pady=10)

    # --- Mostrar Traducción Actual ---
    translated_text_display = tk.Label(segunda_ventana,
                                       text=f"Traducción: {ventana.last_translated_text}",
                                       wraplength=450,
                                       font=("Arial", 10, "italic"))
    translated_text_display.pack(pady=10)

    # --- Botón para Reproducir Audio de la Traducción ---
    def reproducir_audio_actual():
        text = ventana.last_translated_text
        lang = ventana.last_translated_lang if hasattr(ventana, 'last_translated_lang') else 'en' # Idioma por defecto si no se ha traducido
        generate_and_play_audio(text, lang)

    btn_reproducir_audio = tk.Button(segunda_ventana,
                                     text="Reproducir Audio de la Traducción",
                                     command=reproducir_audio_actual)
    btn_reproducir_audio.pack(pady=15)

    # Asegurarse de que Pygame se cierre al cerrar la ventana principal o al final del programa
    # (Ya se maneja en el cleanup del final)

# --- Configuración de la Ventana Principal ---
ventana = tk.Tk()
ventana.title("Traductor y Visualizador")
ventana.geometry("500x450")

# Guardar la última traducción y su idioma en la ventana principal para acceso desde la segunda ventana
ventana.last_translated_text = ""
ventana.last_translated_lang = "es" # Idioma por defecto al inicio

# Área de texto para entrada
entrada_label = tk.Label(ventana, text="Texto a Traducir:")
entrada_label.pack(pady=5)
entrada = tk.Text(ventana, height=5, width=50)
entrada.pack(padx=10, pady=5)
entrada.insert(tk.END, " ")

# Crear menú
menú = tk.Menu(ventana)
ventana.config(menu=menú)

# Agregar submenu de traducción
submenu_traducción = tk.Menu(menú, tearoff=0)
submenu_traducción.add_command(label="Inglés", command=lambda: traducir('en'))
submenu_traducción.add_command(label="Francés", command=lambda: traducir('fr'))
submenu_traducción.add_command(label="Italiano", command=lambda: traducir('it'))
submenu_traducción.add_command(label="Japonés", command=lambda: traducir('ja'))
submenu_traducción.add_command(label="Alemán", command=lambda: traducir('de'))
submenu_traducción.add_command(label="Ruso", command=lambda: traducir('ru'))
menú.add_cascade(label="Traducir a", menu=submenu_traducción)

# Botón para traducir al idioma por defecto (Inglés)
boton_traducir_default = tk.Button(ventana, text=" Traducir ", command=lambda: traducir('en'))
boton_traducir_default.pack(pady=5)

# Etiqueta para mostrar la traducción
resultado_label = tk.Label(ventana, text="Traducción:", font=("Arial", 10, "bold"))
resultado_label.pack(pady=5)
resultado = tk.Label(ventana, text="", font=("Arial", 12), wraplength=450) # wraplength para que el texto se ajuste
resultado.pack(padx=10, pady=5)

# --- Botón principal que abre la segunda ventana ---
boton_abrir_segunda_ventana = tk.Button(ventana,
                                        text="Ver Traducción y Audio ",
                                        command=abrir_segunda_ventana,
                                        bg="lightblue", fg="darkblue",
                                        font=("Arial", 10, "bold"))
boton_abrir_segunda_ventana.pack(pady=20)


# --- Inicio y Limpieza ---
if __name__ == "__main__":
    pygame.init() # Inicializar Pygame una vez al inicio para el mezclador
    pygame.font.init() # Inicializar módulo de fuentes de Pygame si se usara texto en Pygame

    ventana.mainloop()

    # Limpiar el archivo de audio temporal y desinicializar Pygame al cerrar la aplicación
    if os.path.exists(AUDIO_TEMP_FILE):
        os.remove(AUDIO_TEMP_FILE)
        print(f"Archivo temporal {AUDIO_TEMP_FILE} eliminado.")
    if pygame.mixer.get_init():
        pygame.mixer.quit()
        print("Mezclador de Pygame desinicializado.")
    if pygame.get_init():
        pygame.quit()
        print("Pygame desinicializado.")

        
