import streamlit as st
import whisper
import google.generativeai as genai
import edge_tts
import asyncio
import subprocess
import os

st.set_page_config(page_title="AI Dubbing App", layout="centered")
st.title("🎬 AI Dubbing Tool")
st.write("ဗီဒီယို (၅ မိနစ်အထိ) တင်ပြီး မြန်မာအသံသွင်း ဗီဒီယို အလိုအလျောက် ထုတ်ယူပါ")

api_key = st.text_input("Gemini API Key ထည့်ပါ", type="password")
uploaded_file = st.file_uploader("ဗီဒီယိုဖိုင် ရွေးပါ (MP4)", type=["mp4", "mkv", "mov"])

async def text_to_speech(text, output_file):
    communicate = edge_tts.Communicate(text, "my-MM-NilarNeural")
    await communicate.save(output_file)

if st.button("စတင် အသံသွင်းမည်") and uploaded_file and api_key:
    genai.configure(api_key=api_key)
    
    with st.spinner("ဖိုင်ကို သိမ်းဆည်းနေပါသည်..."):
        video_path = "input_video.mp4"
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

    with st.spinner("၁/၄ - မူရင်းဗီဒီယိုမှ စကားသံများကို ရေးသားထုတ်ယူနေပါသည် (Whisper)..."):
        model = whisper.load_model("base")
        result = model.transcribe(video_path)
        original_text = result["text"]
        st.write("**မူရင်းအသံ စာသား -**", original_text[:200] + "...")

    with st.spinner("၂/၄ - မြန်မာလို အဓိပ္ပာယ်ပြန်ဆိုနေပါသည် (Gemini)..."):
        gemini_model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"Translate the following transcript into natural, engaging Burmese narrative suitable for a movie recap: {original_text}"
        response = gemini_model.generate_content(prompt)
        burmese_text = response.text
        st.write("**မြန်မာဘာသာပြန် -**", burmese_text[:200] + "...")

    with st.spinner("၃/၄ - မြန်မာအသံဖိုင် ဖန်တီးနေပါသည်..."):
        burmese_audio = "burmese_voice.mp3"
        asyncio.run(text_to_speech(burmese_text, burmese_audio))

    with st.spinner("၄/၄ - ဗီဒီယိုထဲ အသံအသစ် ထည့်သွင်းနေပါသည်..."):
        output_video = "output_dubbed_video.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", burmese_audio,
            "-c:v", "copy",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            output_video
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    st.success("ဗီဒီယို အောင်မြင်စွာ ဖန်တီးပြီးပါပြီ!")
    st.video(output_video)
    with open(output_video, "rb") as file:
        st.download_button("ဗီဒီယို ဒေါင်းလုဒ်ရယူပါ", file, file_name="dubbed_movie.mp4")
