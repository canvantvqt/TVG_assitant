# -*- coding: utf-8 -*-
import streamlit as st
import threading
import time
import json
import os
import tempfile
from gtts import gTTS
import speech_recognition as sr

st.set_page_config(page_title="Trưng Vương Garden - Voice Assistant", layout="centered")

# ---------- Load FAQ ----------
FAQ_PATH = "faq_garden.json"
if not os.path.exists(FAQ_PATH):
    st.error("Không tìm thấy file faq_garden.json. Vui lòng đặt file JSON vào cùng thư mục với streamlit_app.py")
    st.stop()

with open(FAQ_PATH, encoding="utf-8") as f:
    faq_data = json.load(f)

# ---------- Assistant Class ----------
class AssistantVoice:
    def __init__(self, status_placeholder, user_placeholder, response_placeholder):
        self.recognizer = sr.Recognizer()
        self.unclear_count = 0
        self.status_placeholder = status_placeholder
        self.user_placeholder = user_placeholder
        self.response_placeholder = response_placeholder

    def find_answer(self, user_text):
        for item in faq_data.get("faq", []):
            for keyword in item.get("question", []):
                if keyword.lower() in user_text.lower():
                    return item.get("answer", "")
        return ("Xin lỗi, tôi chưa hiểu câu hỏi của bạn. "
                "Bạn có thể hỏi về giờ mở cửa, giá vé, trải nghiệm, ẩm thực, khuyến mãi hoặc liên hệ.")

    def speak_vietnamese(self, text):
        # TTS -> phát trên web
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tts = gTTS(text=text, lang='vi')
                tts.save(f.name)
                self.response_placeholder.audio(f.name, format="audio/mp3")
                os.remove(f.name)
        except Exception as e:
            self.response_placeholder.error(f"Lỗi khi phát giọng nói: {e}")

    def listen(self):
        try:
            with sr.Microphone() as source:
                self.status_placeholder.info("🎧 Đang lắng nghe...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=7)
                text = self.recognizer.recognize_google(audio, language='vi-VN')
                self.user_placeholder.info(f"Bạn nói: {text}")
                return text
        except sr.UnknownValueError:
            self.unclear_count += 1
            if self.unclear_count >= 3:
                self.speak_vietnamese("Bạn có muốn thử lại sau không?")
                self.unclear_count = 0
            else:
                self.speak_vietnamese("Tôi không nghe rõ, bạn nói lại nhé!")
            return None
        except sr.RequestError:
            self.speak_vietnamese("Hiện tại tôi không thể kết nối dịch vụ.")
            return None
        except Exception as e:
            self.speak_vietnamese(f"Đã xảy ra lỗi: {e}")
            return None

# ---------- UI Layout ----------
st.markdown("<h2 style='text-align:center;'>CHÀO MỪNG BẠN ĐẾN TRƯNG VƯƠNG GARDEN</h2>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;'>TRỢ LÝ A.I BẰNG GIỌNG NÓI TVG</h4>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color: gray;'>Sản phẩm do nhóm học sinh CLB Lập trình lớp 7C</p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
status_placeholder = st.empty()
user_placeholder = st.empty()
response_placeholder = st.empty()

if 'assistant_thread' not in st.session_state:
    st.session_state.assistant_thread = None
if 'assistant_running' not in st.session_state:
    st.session_state.assistant_running = False

# ---------- Assistant Loop ----------
def assistant_loop():
    assistant = AssistantVoice(status_placeholder, user_placeholder, response_placeholder)
    intro_text = ("Xin chào! Tôi là trợ lý Voice AI Trưng Vương Garden. "
                  "Bạn có thể hỏi về giờ mở cửa, giá vé, trải nghiệm, khuyến mãi, ẩm thực hoặc liên hệ.")
    assistant.speak_vietnamese(intro_text)
    while st.session_state.assistant_running:
        text = assistant.listen()
        if text and st.session_state.assistant_running:
            answer = assistant.find_answer(text)
            response_placeholder.success(f"Trợ lý trả lời: {answer}")
            assistant.speak_vietnamese(answer)
        time.sleep(0.5)
    status_placeholder.info("⏹ Trợ lý đã dừng.")

# ---------- START / STOP Buttons ----------
with col1:
    if st.button("▶️ START") and not st.session_state.assistant_running:
        st.session_state.assistant_running = True
        st.session_state.assistant_thread = threading.Thread(target=assistant_loop, daemon=True)
        st.session_state.assistant_thread.start()
        st.success("Trợ lý đang chạy! Nói vào micro laptop của bạn.")

with col2:
    if st.button("⏹ STOP") and st.session_state.assistant_running:
        st.session_state.assistant_running = False
        st.success("Trợ lý đã dừng. Bạn có thể nhấn START để chạy lại.")

# ---------- Optional: Show FAQ raw ----------
with st.expander("Hiển thị JSON FAQ raw"):
    st.json(faq_data)
