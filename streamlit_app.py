# -*- coding: utf-8 -*-
"""
Trợ lý Voice – Trưng Vương Garden (Streamlit web version)
- Ghi âm (trình duyệt) hoặc upload audio
- STT (Google via SpeechRecognition) -> tra JSON FAQ -> trả lời text
- TTS (gTTS) -> phát mp3 trên web bằng st.audio
"""

import streamlit as st
import json
from pathlib import Path
from io import BytesIO
import tempfile
import time
import os

# STT/TTS libs
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment

# Try to import browser recorder component (optional)
try:
    from audio_recorder_streamlit import audio_recorder
except Exception:
    audio_recorder = None

st.set_page_config(page_title="Trưng Vương Garden - Voice Assistant", layout="centered")

# ---------- Load FAQ ----------
FAQ_PATH = Path("faq_garden.json")
if not FAQ_PATH.exists():
    st.error("Không tìm thấy file faq_garden.json. Vui lòng đặt file JSON vào cùng thư mục với streamlit_app.py")
    st.stop()

faq_data = json.loads(FAQ_PATH.read_text(encoding="utf-8"))

def find_answer(user_text: str) -> str:
    for item in faq_data.get("faq", []):
        for kw in item.get("question", []):
            if kw.lower() in user_text.lower():
                return item.get("answer", "")
    return ("Xin lỗi, tôi chưa hiểu câu hỏi của bạn. "
            "Bạn có thể hỏi về giờ mở cửa, giá vé, trải nghiệm, ẩm thực, khuyến mãi hoặc liên hệ.")

# ---------- Helpers ----------
def save_audio_bytes_to_wav(audio_bytes: bytes) -> str:
    """
    Convert incoming bytes (wav/mp3/webm) to a wav file path using pydub.
    Returns path to wav file.
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp_path = f.name
    try:
        audio = AudioSegment.from_file(BytesIO(audio_bytes))
        audio.export(tmp_path, format="wav")
        return tmp_path
    except Exception:
        # fallback: write raw bytes
        with open(tmp_path, "wb") as out:
            out.write(audio_bytes)
        return tmp_path

def transcribe_with_google(wav_path: str) -> str:
    r = sr.Recognizer()
    try:
        with sr.AudioFile(wav_path) as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language='vi-VN')
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return ""

def tts_gtts_bytes(text: str) -> bytes:
    """
    Generate mp3 bytes using gTTS.
    """
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_mp3 = f.name
    tts = gTTS(text=text, lang='vi')
    tts.save(tmp_mp3)
    b = Path(tmp_mp3).read_bytes()
    try:
        os.remove(tmp_mp3)
    except Exception:
        pass
    return b

# ---------- UI ----------
st.title("Trưng Vương Garden — Trợ lý Voice (Web)")
st.markdown("Nói tiếng Việt vào micro (hoặc upload file âm thanh). Ứng dụng sẽ chuyển lời nói thành văn bản, tra FAQ và trả lời bằng giọng đọc.")

col1, col2 = st.columns([3,1])
with col1:
    st.markdown("""
    **Hướng dẫn nhanh:**  
    1. Nhấn **Record** (nếu component hỗ trợ) hoặc kéo thả file âm thanh.  
    2. Chờ ứng dụng chuyển giọng nói thành văn bản.  
    3. Ấn **Phát lời đáp** để nghe trợ lý.
    """)
with col2:
    if st.checkbox("Hiển thị JSON FAQ raw"):
        st.json(faq_data)

st.divider()

st.subheader("Ghi âm / Upload")
if audio_recorder is not None:
    st.caption("Nhấn Record để thu bằng micro (trong trình duyệt).")
    audio_bytes = audio_recorder()
else:
    st.info("Component ghi âm chưa cài trên hệ thống. Hãy upload file âm thanh (wav/mp3/m4a/webm).")
    uploaded = st.file_uploader("Hoặc tải file âm thanh lên để test", type=["wav","mp3","m4a","webm"])
    audio_bytes = uploaded.read() if uploaded else None

if audio_bytes:
    st.success("Đã nhận âm thanh — đang xử lý...")
    st.audio(audio_bytes)

    wav_path = save_audio_bytes_to_wav(audio_bytes)
    transcribed = transcribe_with_google(wav_path)

    if not transcribed:
        st.warning("Không nhận diện được lời nói. Hãy thử ghi âm lại hoặc upload file khác.")
    else:
        st.write("Bạn nói (chuyển từ giọng nói):")
        st.info(transcribed)

        answer = find_answer(transcribed)
        st.write("Trợ lý trả lời (văn bản):")
        st.success(answer)

        if st.button("Phát lời đáp (TTS)"):
            tts_bytes = tts_gtts_bytes(answer)
            st.audio(tts_bytes, format="audio/mp3")

st.write("---")
st.caption("Ghi chú: Mặc định app dùng Google Web Speech via speech_recognition cho STT và gTTS cho TTS. Đổi sang Whisper/Cloud TTS nếu cần.")
