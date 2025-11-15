# Trưng Vương Garden - Voice Assistant (Streamlit)

Repo demo: Trợ lý Voice AI cho Trưng Vương Garden, chạy trên Streamlit.

## Nội dung
- `streamlit_app.py` : app Streamlit (ghi âm/upload -> STT -> tra JSON -> TTS)
- `faq_garden.json` : dữ liệu FAQ & thông tin (thầy đã cung cấp)
- `requirements.txt`

## Hướng dẫn nhanh (local)
1. Tạo virtualenv:
   - `python -m venv venv`
   - Windows: `venv\Scripts\activate`
   - mac/linux: `source venv/bin/activate`
2. Cài dependency:
   - `pip install -r requirements.txt`
3. Chạy app:
   - `streamlit run streamlit_app.py`
4. Mở http://localhost:8501

## Deploy lên Streamlit Community Cloud
1. Push repo lên GitHub.
2. Vào https://share.streamlit.io → New app → chọn repo, branch, file `streamlit_app.py` → Deploy.

## Lưu ý
- STT mặc định dùng Google Web Speech (speech_recognition) — cần internet.
- TTS dùng gTTS (cần internet).
- Để nâng cấp STT/TTS (Whisper, Google Cloud TTS...), chỉnh `streamlit_app.py` và thêm keys vào `st.secrets`.
