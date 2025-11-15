# streamlit_app_optimized.py
# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#from main import AssistantVoice

import streamlit as st
import threading
import time

#from main import AssistantVoice  # Lớp trợ lý bạn đã có
# -*- coding: utf-8 -*-
"""
Trợ lý Voice – Trưng Vương Garden
Nghe tiếng Việt, tư vấn dịch vụ, trả lời chi tiết theo JSON.
"""

import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import os
import time
import json

# ---- HÀM TRA CỨU JSON ----
def find_answer(user_text):
    """Tra cứu câu trả lời từ file JSON faq_garden.json"""
    try:
        with open("faq_garden.json", encoding="utf-8") as f:
            faq_data = json.load(f)
    except Exception:
        return "Xin lỗi, hiện tại tôi không thể truy cập dữ liệu tư vấn."

    for item in faq_data["faq"]:
        for keyword in item["question"]:
            if keyword.lower() in user_text.lower():
                return item["answer"]
    return ("Xin lỗi, tôi chưa hiểu câu hỏi của bạn. "
            "Bạn có thể hỏi về giờ mở cửa, giá vé, trải nghiệm, ẩm thực, khuyến mãi hoặc liên hệ.")

# ---- LỚP TRỢ LÝ ẢO ----
class AssistantVoice:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.unclear_count = 0
        print("TVS-Assistant: Khởi động thành công.")

    # ---- HÀM NÓI TIẾNG VIỆT ----
    def speak_vietnamese(self, text):
        """Chuyển văn bản thành giọng nói tiếng Việt và phát ra loa."""
        try:
            filename = f"response_{int(time.time()*1000)}.mp3"
            tts = gTTS(text=text, lang='vi')
            tts.save(filename)
            playsound(filename)  # Phát và chờ kết thúc
            os.remove(filename)
        except Exception as e:
            print(f"TVS-Assistant: Lỗi khi phát giọng nói: {e}")

    # ---- HÀM NGHE GIỌNG NÓI ----
    def listen(self):
        """Lắng nghe giọng nói người dùng từ microphone."""
        with sr.Microphone() as source:
            print("TVS-Assistant: Tôi đang lắng nghe...")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=7)
                print("TVS-Assistant: Đang nhận diện giọng nói...")
                text = self.recognizer.recognize_google(audio, language='vi-VN')
                print(f"Bạn hỏi: {text}")
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

    # ---- HÀM PHẢN HỒI ----
    def respond(self, text):
        """Trả lời dựa trên JSON hoặc câu hỏi tạm biệt."""
        if not text:
            return
        if "tạm biệt" in text.lower():
            self.speak_vietnamese("Chào tạm biệt! Hẹn gặp lại bạn.")
            exit()
        answer = find_answer(text)
        self.speak_vietnamese(answer)

    # ---- CHẠY TRỢ LÝ ----
    def run(self):
        # Giới thiệu tổng quan khi khởi động
        intro_text = (
            "Xin chào! Tôi là trợ lý Voice AI Trưng Vương Garden. "
            "Khu trải nghiệm của chúng tôi có nhiều dịch vụ thú vị: "
            "Vé tham quan, Vườn cây nhiệt đới, Vườn chim Aviary, Sở thú ăn chay, "
            "Thác nước Apsara, Suối đá Mồ Côi, Bến Thiên Cầm, Nhà tre cộng đồng, "
            "Vườn tượng cảnh quan, Hồ Thiên Nga, Cầu Kiều. "
            "Các hoạt động trải nghiệm: cưỡi ngựa, Hồ bơi Pool Party, xe đạp đôi và đơn, "
            "xe điện tham quan, thuyền Thiên Nga, thuyền SUP, KAYAK, "
            "Trượt phao cầu vồng, xe đua Gokart. "
            "Ẩm thực tại nhà hàng Champa phục vụ ẩm thực địa phương, "
            "bãi đỗ xe miễn phí và nhiều góc checkin. "
            "Bạn có thể hỏi tôi về: giờ mở cửa, giá vé, trải nghiệm, khuyến mãi, ẩm thực hoặc liên hệ."
        )
        self.speak_vietnamese(intro_text)

        # Vòng lặp chính
        while True:
            text = self.listen()
            if text:
                self.respond(text)

# ---- CHẠY TRỢ LÝ ----
if __name__ == "__main__":
    assistant = AssistantVoice()
    assistant.run()



st.set_page_config(page_title="Trưng Vương Garden - Voice Assistant", layout="centered")

# ---------- UI ----------
st.markdown("<h2 style='text-align:center;'>CHÀO MỪNG BẠN ĐẾN TRƯNG VƯƠNG GARDEN</h2>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;'>TRỢ LÝ A.I BẰNG GIỌNG NÓI TVG</h4>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
if 'assistant_thread' not in st.session_state:
    st.session_state.assistant_thread = None
if 'assistant_running' not in st.session_state:
    st.session_state.assistant_running = False
if 'assistant_instance' not in st.session_state:
    st.session_state.assistant_instance = None

status_placeholder = st.empty()
user_text_placeholder = st.empty()
response_placeholder = st.empty()

# ---------- Functions ----------
def assistant_loop():
    assistant = AssistantVoice()
    st.session_state.assistant_instance = assistant
    intro_text = (
        "Xin chào! Tôi là trợ lý Voice AI Trưng Vương Garden. "
        "Bạn có thể hỏi về giờ mở cửa, giá vé, trải nghiệm, khuyến mãi, ẩm thực hoặc liên hệ."
    )
    assistant.speak_vietnamese(intro_text)
    while st.session_state.assistant_running:
        status_placeholder.info("🎧 Đang lắng nghe...")
        text = assistant.listen()
        if text and st.session_state.assistant_running:
            user_text_placeholder.info(f"Bạn nói: {text}")
            answer = assistant.find_answer(text) if hasattr(assistant, 'find_answer') else text
            response_placeholder.success(f"Trợ lý trả lời: {answer}")
            assistant.speak_vietnamese(answer)
        time.sleep(0.5)
    status_placeholder.info("⏹ Trợ lý đã dừng.")

# ---------- START / STOP ----------
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

st.markdown("<p style='text-align:center; color: gray;'>Sản phẩm do nhóm học sinh CLB Lập trình lớp 7C</p>", unsafe_allow_html=True)
