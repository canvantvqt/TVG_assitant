# streamlit_app_optimized.py
# -*- coding: utf-8 -*-
import streamlit as st
import threading
import time
from main import AssistantVoice  # Lớp trợ lý bạn đã có

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
