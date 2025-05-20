import streamlit as st
import os
import shutil # For directory cleanup
from src.utils import language_mapping, is_valid_youtube_link # Import the new utility function
from src.video_processing import download_youtube_video, resize_video, extract_audio
from src.transcription import transcribe_audio
from src.translation import translate_text
from src.speech_synthesis import synthesize_speech, release_tts_models
from src.lip_sync import run_wav2lip, run_video_retalking, get_wav2lip_readme_instructions, get_video_retalking_readme_instructions

st.set_page_config(layout="wide")
st.title("AI Lip Sync Tool 👄")

# --- Main UI Elements ---
st.sidebar.title("⚙️ Controls")
uploaded_file = st.sidebar.file_uploader("1. Upload a video file", type=["mp4", "mov", "avi", "mkv"])
youtube_link = st.sidebar.text_input("Or provide a YouTube link")

if st.sidebar.button("Clear Input", key="clear_input"):
    uploaded_file = None # This won't directly clear the widget state due to Streamlit's rerun nature
    youtube_link = ""    # This will clear the text input
    # To truly clear file_uploader, it's more complex, often involving session state.
    # For now, this primarily clears the youtube_link and signals intent.
    st.experimental_rerun()


target_language_name = st.sidebar.selectbox("2. Select target language", options=list(language_mapping.keys()))

whisper_model_options = ["tiny", "base", "small", "medium", "large"]
whisper_model_size = st.sidebar.selectbox(
    "Select Whisper Model Size", 
    options=whisper_model_options, 
    index=whisper_model_options.index("medium"), # Default to medium
    help="Smaller models are faster but less accurate. Larger models are more accurate but slower and use more memory. Ensure you have downloaded the corresponding .pt file."
)

quality = st.sidebar.radio("Select lip-sync quality", options=["Normal (Wav2Lip)", "High Quality (Video Retalking)"])
resize_720p = st.sidebar.checkbox("Resize video to 720p (recommended for better results)", True)

if st.sidebar.button("Start Processing"):
    # Clear previous run's output on the main page
    main_placeholder = st.empty() # Create a placeholder for all dynamic content

    if not uploaded_file and not youtube_link:
        st.error("Please upload a video or provide a YouTube link.")
    else:
        # Create temp directory
        temp_dir = "temp_processing_space"
        os.makedirs(temp_dir, exist_ok=True)
        
        source_video_path = None
        current_video_path = None # To track the video path through processing steps

        if uploaded_file:
            source_video_path = os.path.join(temp_dir, uploaded_file.name)
            with open(source_video_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.info(f"Uploaded {uploaded_file.name}")
            current_video_path = source_video_path
        elif youtube_link:
            with st.spinner("Downloading YouTube video..."):
                downloaded_video_filename = "downloaded_youtube_video.mp4" # Define a fixed name
                # Adapt download_youtube_video to save in temp_dir with a specific name
                source_video_path = download_youtube_video(youtube_link, os.path.join(temp_dir, downloaded_video_filename))
            if not source_video_path or not os.path.exists(source_video_path):
                st.error("Failed to download YouTube video.")
                st.stop() 
            st.success(f"YouTube video downloaded: {source_video_path}")
            current_video_path = source_video_path
        
        if not current_video_path:
            st.error("Video source is not available.")
            st.stop()

        st.success(f"Video ready for processing: {os.path.basename(current_video_path)}")

        # --- Actual processing pipeline ---
        st.info("Starting processing pipeline...")
        
        # 1. Resize (optional)
        if resize_720p:
            resized_video_path = os.path.join(temp_dir, f"resized_{os.path.basename(current_video_path)}")
            with st.spinner("Resizing video..."):
                current_video_path = resize_video(current_video_path, resized_video_path)
                # st.info("Video resize placeholder") # Placeholder
                # current_video_path = os.path.join(temp_dir, "resized_placeholder.mp4") # Placeholder
            if not current_video_path or not os.path.exists(current_video_path):
                st.error("Failed to resize video.")
                st.stop()
            st.success(f"Video resized: {os.path.basename(current_video_path)}")

        # 2. Extract Audio
        extracted_audio_path = os.path.join(temp_dir, "original_audio.wav")
        with st.spinner("Extracting audio..."):
            extracted_audio_path = extract_audio(current_video_path, extracted_audio_path)
            # st.info("Audio extraction placeholder") # Placeholder
        if not extracted_audio_path or not os.path.exists(extracted_audio_path):
            st.error("Failed to extract audio.")
            st.stop()
        st.success(f"Audio extracted: {os.path.basename(extracted_audio_path)}")
        
        # 3. Transcribe Audio
        transcribed_text = None
        detected_lang = None
        with st.spinner(f"Transcribing audio with '{whisper_model_size}' model..."):
            transcribed_text, detected_lang = transcribe_audio(extracted_audio_path, model_name=whisper_model_size)
        if not transcribed_text or not detected_lang: # Allow empty transcription for silent videos
            if detected_lang is None and transcribed_text is None: # Actual error
                st.error("Failed to transcribe audio.")
                st.stop()
            elif transcribed_text == "" and detected_lang: # Empty transcription but language detected
                 st.warning("Audio transcribed as empty. The video might be silent or have very low audio.")
                 # Proceed with empty string, translation might handle it or TTS might produce silent audio
            else: # Should not happen if API is consistent
                st.error("Transcription failed with an unexpected state.")
                st.stop()

        st.success(f"Audio transcribed. Detected language: {detected_lang if detected_lang else 'unknown'}")
        st.text_area("Transcribed Text", transcribed_text if transcribed_text else "<No speech detected>", height=100)


        # 4. Translate Text
        translated_text = None
        target_lang_code = language_mapping[target_language_name]
        if detected_lang == target_lang_code:
            st.info(f"Source language ({detected_lang}) is the same as target language ({target_lang_code}). Skipping translation.")
            translated_text = transcribed_text
        else:
            with st.spinner(f"Translating text from {detected_lang} to {target_lang_code}..."):
                translated_text = translate_text(transcribed_text, detected_lang, target_lang_code)
                # translated_text = "This is a sample translated text." # Placeholder
                # st.info("Text translation placeholder") # Placeholder
            if not translated_text:
                st.error("Failed to translate text.")
                st.stop()
            st.success(f"Text translated to {target_lang_code}.")
            st.text_area("Translated Text", translated_text, height=100)

        # 5. Synthesize Speech
        synthesized_audio_path = os.path.join(temp_dir, "synthesized_audio.wav")
        with st.spinner("Synthesizing speech..."):
            # Using original extracted audio as speaker reference for voice cloning
            synthesized_audio_path = synthesize_speech(translated_text, target_lang_code, extracted_audio_path, synthesized_audio_path)
            # st.info("Speech synthesis placeholder") # Placeholder
        if not synthesized_audio_path or not os.path.exists(synthesized_audio_path):
            st.error("Failed to synthesize speech.")
            st.stop()
        st.success(f"Speech synthesized: {os.path.basename(synthesized_audio_path)}")
        st.audio(synthesized_audio_path)

        # Inner try-finally for model-dependent operations and their cleanup
        try:
            # 6. Lip Sync
            final_video_path = os.path.join(temp_dir, f"final_{os.path.basename(current_video_path)}")
            with st.spinner(f"Performing {quality} lip sync... This may take a while..."):
                if "Normal" in quality:
                    final_video_path = run_wav2lip(current_video_path, synthesized_audio_path, final_video_path)
                else: # High Quality (Video Retalking)
                    final_video_path = run_video_retalking(current_video_path, synthesized_audio_path, final_video_path)
            
            if not final_video_path or not os.path.exists(final_video_path):
                st.error("Lip sync process failed or did not produce a video.")
                st.stop()
            st.success("Lip sync complete!")
            
            # --- End of processing pipeline ---
            st.video(final_video_path)
            with open(final_video_path, "rb") as f_vid:
                st.download_button("Download Processed Video", data=f_vid, file_name=f"lipsynced_{os.path.basename(current_video_path)}")
        
        finally: # Inner finally: Release TTS models
            with st.spinner("Releasing TTS models from memory..."):
                release_tts_models() 
            st.info("TTS Models released from memory.")

    except Exception as e:
        st.error(f"An error occurred during the main processing pipeline: {e}")
        # Consider logging the full traceback here for debugging
        # import traceback
        # st.text_area("Error Traceback", traceback.format_exc(), height=200)
    finally: # Outermost finally: Clean up the temporary directory
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                st.info(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                st.warning(f"Could not automatically clean up temporary directory {temp_dir}: {e}")
            
# --- Sidebar for Setup Instructions ---
st.sidebar.title("Setup & Instructions")
st.sidebar.info(
    "This tool requires several models to be downloaded and placed in specific directories. "
    "Please follow the instructions below carefully."
)

with st.sidebar.expander("Whisper Model Setup (Transcription)", expanded=False):
    st.markdown("""
    1.  **Download Models:**
        *   Whisper models are language-specific. Download the `.pt` file corresponding to the size you want to use (e.g., `tiny.pt`, `base.pt`, `medium.pt`).
        *   You can find these via the [OpenAI Whisper GitHub repository](https://github.com/openai/whisper#available-models-and-languages) or Hugging Face.
    2.  **Place Models:**
        *   Create a directory: `models/whisper/` in the root of this project.
        *   Place your downloaded `.pt` files into this directory (e.g., `models/whisper/medium.pt`, `models/whisper/small.pt`).
    *The application allows you to select the model size from the sidebar. Ensure the corresponding file is present in the `models/whisper/` directory.*
    """)

with st.sidebar.expander("Coqui XTTSv2 Model Setup (Speech Synthesis)", expanded=False):
    st.markdown("""
    1.  **Download Model:**
        *   The XTTSv2 model needs to be downloaded from Coqui. You might need to agree to terms on their site or use their tools if direct download links are not obvious.
        *   Typically, this involves downloading files like `model.pth`, `config.json`, `vocab.json`, and potentially speaker encoder files if separate.
    2.  **Place Model Files:**
        *   Create a directory: `models/tts/xtts_v2/` in the root of this project.
        *   Place all the downloaded model files into this directory.
        Example structure:
        ```
        models/
        └── tts/
            └── xtts_v2/
                ├── model.pth
                ├── config.json
                ├── vocab.json
                └── ... (any other model files)
        ```
    """)

with st.sidebar.expander("Wav2Lip Model Setup (Lip Sync - Normal Quality)", expanded=False):
    st.markdown(get_wav2lip_readme_instructions())

with st.sidebar.expander("Video-Retalking Model Setup (Lip Sync - High Quality)", expanded=False):
    st.markdown(get_video_retalking_readme_instructions())
