from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

from piper.voice import PiperVoice
from pathlib import Path
import io
import wave

# ---------- CONFIGURACIÓN ----------

# Carpeta base = carpeta donde está este archivo main.py
BASE_DIR = Path(__file__).resolve().parent

# Ruta al modelo de MIRA (voz femenina mexicana)
MODEL_PATH = BASE_DIR / "models" / "es_MX-claude-high.onnx"

print("🔧 Iniciando MIRA TTS...")
print(f"🔎 Buscando modelo en: {MODEL_PATH}")

voice = None
try:
    if MODEL_PATH.exists():
        voice = PiperVoice.load(str(MODEL_PATH))
        print("✅ Modelo Piper cargado correctamente.")
    else:
        print("❌ NO se encontró el modelo en esa ruta.")
except Exception as e:
    print("❌ Error cargando el modelo Piper:", e)

app = FastAPI()

# Orígenes permitidos (tus páginas en GitHub Pages)
origins = [
    "https://innova-space-edu.github.io",
    "https://innova-space-edu.github.io/ceo_AI_mira",
    "https://innova-space-edu.github.io/miraAI",
    # Si quieres ser más estricto, quita "*" después de probar
    "*",
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
    return {
        "status": "ok",
        "message": "MIRA TTS (Piper es_MX-claude-high) activo",
        "model_loaded": voice is not None,
        "model_path": str(MODEL_PATH),
    }


@app.post("/tts")
def tts(req: TTSRequest):
    if voice is None:
        # Si el modelo no se cargó, devolvemos error claro
        return JSONResponse(
            status_code=500,
            content={"error": "Modelo de voz no cargado en el servidor."},
        )

    text = (req.text or "").strip()
    if not text:
        text = "No se recibió texto para leer."

    try:
        # Generar audio WAV en memoria
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)  # 16 bits
            wav_file.setframerate(voice.config.sample_rate)
            voice.synthesize(text, wav_file)

        buffer.seek(0)
        return StreamingResponse(buffer, media_type="audio/wav")

    except Exception as e:
        print("❌ Error generando audio TTS:", e)
        return JSONResponse(
            status_code=500,
            content={"error": "Error generando el audio TTS en el servidor."},
        )
