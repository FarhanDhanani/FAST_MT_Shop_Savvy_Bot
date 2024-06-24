import io
import streamlit as st
from config import Config
from openai import OpenAI

def whisper_stt(audio, openai_api_key=None, language=None):
    if not 'openai_client' in st.session_state:
        st.session_state.openai_client = OpenAI(api_key=openai_api_key)

    if audio is None:
        output = None
    else:
        output = None
        audio_bio = io.BytesIO(audio['bytes'])
        audio_bio.name = 'audio.mp3'
        success = False
        err = 0
        if Config.USE_OPEN_AI_WHISPER_MODEL:
            while not success and err < 3:  # Retry up to 3 times in case of OpenAI server error.
                try:
                    transcript = st.session_state.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_bio,
                        language=language
                    )
                except Exception as e:
                    print(str(e))  # log the exception in the terminal
                    err += 1
                else:
                    success = True
                    output = transcript.text
                    st.session_state._last_speech_to_text_transcript = output
        # Dummy case to test out the flow
        else:
            success = True
            output = "What is the price of the product Chai?"
            st.session_state._last_speech_to_text_transcript = output
    return output