# YEREMMY WILLIAM TRAVIESO PEÑA - 23-EISN-2-071

import gradio as gr
from openai import OpenAI
from gtts import gTTS
import tempfile
import os
import speech_recognition as sr

# 👉 Coloca aquí tu API key real
client = OpenAI(api_key="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")

# Tipos válidos
pokemon_types = [
    "agua", "bicho", "dragón", "eléctrico", "fantasma", "hada", "hielo",
    "lucha", "normal", "planta", "psíquico", "siniestro", "tierra", "veneno", "volador"
]

# Prompt para DALL·E
def prompt_imagen(tipo):
    return f"Ilustración digital de un Pokémon tipo {tipo}, en pose dinámica, estilo anime, fondo simple."

# Descripción del Pokémon
def generar_descripcion(tipo):
    prompt = f"Inventa un Pokémon del tipo {tipo}. Describe su apariencia, comportamiento y una habilidad especial."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=100
    )
    return response.choices[0].message.content.strip()

# Imagen con DALL·E (tamaño válido: 512x512)
def generar_imagen(tipo):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt_imagen(tipo),
        size="1024x1024",  # ✅ Tamaño válido y pequeño
        quality="standard",
        n=1
    )
    return response.data[0].url

# Texto a voz
def texto_a_audio(texto):
    tts = gTTS(text=texto, lang='es')
    archivo_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(archivo_temp.name)
    return archivo_temp.name

# Proceso general
def generar_pokemon(tipo):
    tipo = tipo.lower()
    if tipo not in pokemon_types:
        return None, f"Tipo '{tipo}' no válido", None
    descripcion = generar_descripcion(tipo)
    imagen = generar_imagen(tipo)
    audio = texto_a_audio(descripcion)
    return imagen, descripcion, audio

# Procesar voz
def procesar_audio(audio_path):
    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = r.record(source)
    try:
        texto = r.recognize_google(audio, language="es-ES").lower()
        if texto in pokemon_types:
            return generar_pokemon(texto)
        else:
            return None, f"No se reconoció un tipo válido. Dijiste: '{texto}'", None
    except Exception as e:
        return None, f"Error procesando audio: {str(e)}", None

# Interfaz Gradio
with gr.Blocks() as demo:
    gr.Markdown("## 🧠 Proyecto Final IA - Generador de Pokémon por Tipo")
    gr.Markdown("Selecciona o di el tipo de Pokémon. Se generará una imagen, una descripción y una narración.")

    with gr.Row():
        selector_tipo = gr.Dropdown(label="Selecciona un tipo", choices=pokemon_types)
        entrada_voz = gr.Audio(label="O habla el tipo", type="filepath", format="wav")

    boton = gr.Button("🎨 Generar Pokémon")

    imagen = gr.Image(label="Imagen generada")
    descripcion = gr.Textbox(label="Descripción")
    narracion = gr.Audio(label="Narración", autoplay=True)

    selector_tipo.change(fn=generar_pokemon, inputs=selector_tipo, outputs=[imagen, descripcion, narracion])
    boton.click(fn=generar_pokemon, inputs=selector_tipo, outputs=[imagen, descripcion, narracion])
    entrada_voz.change(fn=procesar_audio, inputs=entrada_voz, outputs=[imagen, descripcion, narracion])

demo.launch()
