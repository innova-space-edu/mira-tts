from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from piper.voice import PiperVoice
import io
import wave
import os

# ---------- CONFIGURACIÓN ----------
# Ruta al modelo de MIRA (voz femenina mexicana)
MODEL_PATH = os.path.join("models", "es_MX-claude-high.onnx")

# Cargar la voz una sola vez al iniciar el servidor
voice = PiperVoice.load(MODEL_PATH)

app = FastAPI()

# Orígenes permitidos (tus páginas en GitHub Pages)
origins = [
    "https://innova-space-edu.github.io",
    "https://innova-space-edu.github.io/ceo_AI_mira",
    "https://innova-space-edu.github.io/miraAI",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TTSRequest(BaseModel):
    text: str


@app.get("/")
def root():
    return {"status": "ok", "message": "MIRA TTS (Piper es_MX-claude-high) activo"}


@app.post("/tts")
def tts(req: TTSRequest):
    text = req.text.strip()
    if not text:
        text = "No se recibió texto para leer."

    # Generar audio WAV en memoria
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 16 bits
        wav_file.setframerate(voice.config.sample_rate)
        voice.synthesize(text, wav_file)

    buffer.seek(0)
    return StreamingResponse(buffer, media_type="audio/wav")
