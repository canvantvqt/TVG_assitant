# streamlit_app_optimized_cloud.py
# -*- coding: utf-8 -*-
import streamlit as st
import threading
import time
import json
import tempfile
from pathlib import Path
from io import BytesIO
from gtts import gTTS
from pydub import AudioSegment
import speech_recognition as sr
import os

# ---------- Load FAQ JSON ----------
FAQ_PATH = Path("faq_garden.json")
if not FAQ_PATH.exists():
    st.error("Không tìm thấy file faq_garden.json. Vui lòng đặt file JSON vào cùng thư mục với app")
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
    """Convert bytes to WAV file using pydub."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp_path = f.name
    audio = AudioSegment.from_file(BytesIO(audio_bytes))
    audio.export(tmp_path, format="wav")
    return tmp_path

def transcribe_audio(wav_path: str) -> str:
    r = sr.Recognizer()
    try:
        with sr.AudioFile(wav_path) as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language='vi-VN')
        return text
    except:
        return ""

def tts_gtts_bytes(text: str) -> bytes:
    """Generate mp3 bytes using gTTS."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_mp3 = f.name
    tts = gTTS(text=text, lang='vi')
    tts.save(tmp_mp3)
    b = Path(tmp_mp3).read_bytes()
    try: os.remove(tmp_mp3)
    except: pass
    return b

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Trưng Vương Garden - Voice Assistant", layout="centered")
st.markdown("<h2 style='text-align:center;'>CHÀO MỪNG BẠN ĐẾN TRƯNG VƯƠNG GARDEN</h2>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;'>TRỢ LÝ A.I BẰNG GIỌNG NÓI TVG</h4>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,1,1])
if 'assistant_started' not in st.session_state:
    st.session_state.assistant_started = False

# Placeholders
status_ph = st.empty()
user_text_ph = st.empty()
response_ph = st.empty()

# ---------- START / STOP ----------
def play_intro():
    intro_text = (
        "Xin chào! Tôi là trợ lý Voice AI Trưng Vương Garden. "
        "Bạn có thể hỏi tôi về giờ mở cửa, giá vé, trải nghiệm, khuyến mãi, ẩm thực hoặc liên hệ."
    )
    tts_bytes = tts_gtts_bytes(intro_text)
    st.audio(tts_bytes, format="audio/mp3")

with col1:
    if st.button("▶️ START") and not st.session_state.assistant_started:
        st.session_state.assistant_started = True
        status_ph.info("🎤 Trợ lý đã sẵn sàng. Nghe lời chào...")
        play_intro()
        status_ph.info("💬 Bạn có thể nhấn Record để hỏi câu đầu tiên.")

with col2:
    if st.button("⏹ STOP") and st.session_state.assistant_started:
        st.session_state.assistant_started = False
        status_ph.info("⏹ Trợ lý đã dừng. Nhấn START để bắt đầu lại.")
        user_text_ph.empty()
        response_ph.empty()

# ---------- Record / Upload ----------
st.subheader("Ghi âm câu hỏi")
try:
    from audio_recorder_streamlit import audio_recorder
    audio_bytes = audio_recorder()
except:
    st.info("Component ghi âm chưa cài. Hãy upload file âm thanh (wav/mp3/m4a/webm).")
    uploaded = st.file_uploader("Hoặc tải file âm thanh lên", type=["wav","mp3","m4a","webm"])
    audio_bytes = uploaded.read() if uploaded else None

if audio_bytes and st.session_state.assistant_started:
    status_ph.info("⌛ Đang xử lý âm thanh...")
    wav_path = save_audio_bytes_to_wav(audio_bytes)
    user_text = transcribe_audio(wav_path)
    if not user_text:
        status_ph.warning("Không nhận diện được giọng nói. Hãy thử lại.")
    else:
        user_text_ph.info(f"Bạn nói: {user_text}")
        answer = find_answer(user_text)
        response_ph.success(f"Trợ lý trả lời: {answer}")
        tts_bytes = tts_gtts_bytes(answer)
        st.audio(tts_bytes, format="audio/mp3")

st.markdown("<p style='text-align:center; color: gray;'>Sản phẩm do nhóm học sinh CLB Lập trình lớp 7C</p>", unsafe_allow_html=True)
