from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment
import speech_recognition as sr
import tempfile
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

@app.post("/stt")
async def stt(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    suffix = os.path.splitext(file.filename)[1] or ".tmp"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        uploaded_path = tmp.name

    try:
        # Convert **any audio format** to WAV
        wav_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        wav_path = wav_temp.name
        wav_temp.close()

        audio = AudioSegment.from_file(uploaded_path)  # auto-detect format
        audio = audio.set_channels(1).set_frame_rate(16000)  # mono 16kHz
        audio.export(wav_path, format="wav")

        # Speech Recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        return {"text": text}

    except Exception as e:
        return {"error": str(e)}
    finally:
        for f in [uploaded_path, wav_path]:
            try: os.remove(f)
            except: pass
