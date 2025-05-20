import os
import torch
from TTS.api import TTS

# Global variable to hold the TTS model instance
tts_model_instance = None

def get_tts_model(language_code, use_cuda=False):
    """
    Initializes and returns a TTS model based on the language code.
    Manages a global model instance to avoid reloading.

    Args:
        language_code (str): The language code for TTS (e.g., 'en', 'es').
        use_cuda (bool): Whether to use CUDA if available.

    Returns:
        TTS.api.TTS: The initialized TTS model, or None if initialization fails.
    """
    global tts_model_instance

    # Determine the device
    device = "cuda" if use_cuda and torch.cuda.is_available() else "cpu"
    print(f"TTS will use device: {device}")

    # Map language codes to specific Coqui TTS models
    # This mapping needs to be curated based on available Coqui models
    # and the desired voice characteristics.
    # For voice cloning, XTTS models are generally preferred.
    # The model path is now constructed to point to a local directory.
    # User is expected to download the model and place it in 'models/tts/xtts_v2/'
    model_base_path = "models"
    tts_model_dir = "tts"
    xtts_v2_dir = "xtts_v2"
    model_path = os.path.join(model_base_path, tts_model_dir, xtts_v2_dir) # e.g. models/tts/xtts_v2

    # Check if the model path and key files exist (e.g., config.json, model.pth - actual names might vary)
    expected_config_path = os.path.join(model_path, "config.json")
    # Add more critical file checks if necessary, e.g., model.pth, vocab.json
    # For this example, checking config.json and the directory itself.
    if not os.path.exists(model_path) or not os.path.isdir(model_path):
        error_msg = f"Coqui TTS model directory not found at '{model_path}'. Please check setup instructions."
        print(error_msg)
        raise FileNotFoundError(error_msg)
    if not os.path.exists(expected_config_path):
        error_msg = f"Coqui TTS model config file not found at '{expected_config_path}'. Ensure the model is correctly downloaded and placed."
        print(error_msg)
        raise FileNotFoundError(error_msg)
    # Check if directory is empty (additional check)
    if not os.listdir(model_path):
         error_msg = f"Coqui TTS model directory '{model_path}' is empty. Please ensure model files are present."
         print(error_msg)
         raise FileNotFoundError(error_msg)


    if tts_model_instance is None:
        print(f"Loading TTS model from path: {model_path} for language: {language_code}...")
        try:
            tts_model_instance = TTS(model_path=model_path, config_path=expected_config_path, progress_bar=True).to(device)
            print("TTS model loaded successfully.")
        except Exception as e:
            error_msg = f"Error loading Coqui TTS model from '{model_path}': {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)
    # If a model is already loaded, we might need to check if it's compatible
    # with the new language_code or if it needs to be reloaded.
    # For XTTS models, they are often multilingual, so reloading might not be necessary
    # unless a very different language or voice characteristic is needed.
    # For simplicity, this current implementation uses one global model.
    # If you switch languages frequently and need different base models,
    # this logic would need to be more sophisticated.

    return tts_model_instance

def synthesize_speech(text, target_lang_code, speaker_wav_path, output_synth_wav_path="synthesized_audio.wav"):
    """
    Synthesizes speech from text using a TTS model, with voice cloning.

    Args:
        text (str): The text to synthesize.
        target_lang_code (str): The language code for the TTS model (e.g., "en", "es").
        speaker_wav_path (str): Path to the original audio file for voice cloning.
        output_synth_wav_path (str): Path to save the synthesized audio.

    Returns:
        str: Path to the synthesized audio file, or None if synthesis fails.
    """
    if not text:
        print("Error: No text provided for speech synthesis.")
        return None
    if not os.path.exists(speaker_wav_path):
        error_msg = f"Speaker WAV file not found at {speaker_wav_path} for voice cloning."
        print(error_msg)
        raise FileNotFoundError(error_msg)

    use_cuda = torch.cuda.is_available()
    try:
        tts_model = get_tts_model(language_code=target_lang_code, use_cuda=use_cuda)
    except (FileNotFoundError, RuntimeError) as e: # Catch errors from get_tts_model
        # These errors are already printed in get_tts_model, re-raise to propagate
        raise
    
    if tts_model is None: # Should be caught by exceptions in get_tts_model
        error_msg = "TTS model not available after attempting to load. Cannot synthesize speech."
        print(error_msg)
        raise RuntimeError(error_msg) # Should not happen if get_tts_model raises properly

    try:
        print(f"Synthesizing speech for text: '{text[:50]}...' in language: '{target_lang_code}'")
        print(f"Using speaker WAV for voice cloning: {speaker_wav_path}")

        tts_model.tts_to_file(
            text=text,
            speaker_wav=speaker_wav_path,
            language=target_lang_code,
            file_path=output_synth_wav_path,
        )
        print(f"Speech synthesized successfully to {output_synth_wav_path}")
        return output_synth_wav_path
    except Exception as e:
        error_msg = f"Error during Coqui TTS speech synthesis: {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg)

def release_tts_models(whisper_model_to_release=None):
    """
    Releases the TTS model and optionally a Whisper model from memory.
    Also clears CUDA cache if PyTorch is using CUDA.

    Args:
        whisper_model_to_release: An optional Whisper model object to delete.
    """
    global tts_model_instance
    if tts_model_instance is not None:
        print("Releasing TTS model from memory...")
        # How to properly delete a TTS object depends on its internal structure.
        # Often, setting to None and letting Python's garbage collector handle it,
        # along with torch.cuda.empty_cache(), is sufficient.
        del tts_model_instance
        tts_model_instance = None
        print("TTS model released.")

    if whisper_model_to_release is not None:
        print("Releasing Whisper model from memory...")
        del whisper_model_to_release # Assuming whisper_model is passed if loaded elsewhere
        print("Whisper model released.")

    if torch.cuda.is_available():
        print("Emptying CUDA cache...")
        torch.cuda.empty_cache()
        print("CUDA cache emptied.")

if __name__ == '__main__':
    # Example Usage (ensure models/tts/xtts_v2 exists and has model files)
    dummy_speaker_wav = "audio.wav" # Reusing from transcription test
    
    if not os.path.exists(dummy_speaker_wav):
        print(f"Warning: Dummy speaker WAV '{dummy_speaker_wav}' not found. Creating one for TTS test.")
        try:
            subprocess.run([ # Using 24kHz as per our audio pipeline
                "ffmpeg", "-f", "lavfi", "-i", "anullsrc=channel_layout=mono:sample_rate=24000",
                "-t", "2", dummy_speaker_wav, "-y"
            ], check=True)
            print(f"Created dummy '{dummy_speaker_wav}'.")
        except Exception as e:
            print(f"Could not create dummy '{dummy_speaker_wav}': {e}. TTS example might fail.")

    if os.path.exists(dummy_speaker_wav):
        sample_text_en = "Hello, this is a test of Coqui TTS with voice cloning."
        sample_lang_en = "en"
        output_tts_path_en = "synthesized_en_tts.wav"

        print(f"\n--- Testing Coqui TTS English speech synthesis ---")
        try:
            # Check if TTS model files are present for the test
            tts_model_dir_for_test = os.path.join("models", "tts", "xtts_v2")
            if not os.path.exists(tts_model_dir_for_test) or not os.path.exists(os.path.join(tts_model_dir_for_test, "config.json")):
                 print(f"Test SKIPPED: Coqui TTS model not found at '{tts_model_dir_for_test}'. Please download and set it up.")
            else:
                synthesized_audio_en = synthesize_speech(sample_text_en, sample_lang_en, dummy_speaker_wav, output_tts_path_en)
                if synthesized_audio_en:
                    print(f"English speech saved to: {synthesized_audio_en}")
                else:
                    print(f"TTS English synthesis test failed or returned None.")
        except (FileNotFoundError, RuntimeError) as model_error:
             print(f"TTS Test FAILED due to model loading/setup: {model_error}")
        except Exception as ex:
            print(f"TTS Test FAILED with unexpected error: {ex}")
        finally:
            # Clean up models after test
            release_tts_models()
    else:
        print(f"Skipping TTS example as '{dummy_speaker_wav}' was not found/created.")
