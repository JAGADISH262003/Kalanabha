import whisper
import os

def transcribe_audio(audio_path="audio.wav"):
    """
    Transcribes the given audio file using Whisper.

    Args:
        audio_path (str): Path to the audio file.
        model_name (str): Name of the Whisper model to use (e.g., "tiny", "base", "small", "medium", "large").

    Returns:
        tuple: (transcribed_text, detected_language)
               Returns (None, None) if transcription fails.
    """
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found at {audio_path}")
        return None, None

    # Model path is constructed based on the model_name parameter.
    # User is expected to download the model (e.g., "medium.pt") and place it in "models/whisper/"
    model_filename = f"{model_name}.pt"
    model_download_path = os.path.join("models", "whisper", model_filename) # Path where user downloads .pt file
    
    # Whisper's load_model can take the name directly (e.g., "medium") and it will download if not found in default cache,
    # or it can take the path to a .pt file.
    # To use our local "models/whisper/" directory as the primary source:
    # We'll pass the path if the file exists there, otherwise, we can let Whisper try to download to its cache
    # by passing just the model_name, or handle it more strictly.
    # For this implementation, we'll require the .pt file to be in our designated models/whisper/ directory.

    if not os.path.exists(model_download_path):
        error_msg = f"Whisper model file '{model_filename}' not found at {model_download_path}. Please check setup instructions."
        print(f"Error: {error_msg}")
        raise FileNotFoundError(error_msg)

    print(f"Loading Whisper model ({model_name})...")
    try:
        model = whisper.load_model(model_download_path)
        print(f"Whisper model '{model_name}' loaded successfully from {model_download_path}.")
    except Exception as e:
        error_msg = f"Error loading Whisper model '{model_name}' from {model_download_path}: {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg)
    
    try:
        print(f"Starting transcription for {audio_path}...")
        result = model.transcribe(audio_path)
        transcribed_text = result["text"]
        detected_language = result["language"]
        print(f"Transcription complete. Detected language: {detected_language}")
        # print(f"Transcribed text: {transcribed_text}") # Can be very long

        # Clean up the model (optional, managed globally or per-session in a real app)
        # del model
        # if torch.cuda.is_available(): torch.cuda.empty_cache()
        return transcribed_text, detected_language
    except Exception as e:
        error_msg = f"Error during audio transcription with Whisper model '{model_name}': {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg)

if __name__ == '__main__':
    # Example usage (requires a dummy audio.wav file and models downloaded)
    # Ensure `models/whisper/medium.pt` (or other selected model) exists for this example.
    dummy_audio_file = "audio.wav"
    selected_model_name = "medium" # or "base", "tiny" if available

    if not os.path.exists(dummy_audio_file):
        try:
            print(f"Creating dummy '{dummy_audio_file}' for testing...")
            subprocess.run([
                "ffmpeg", "-f", "lavfi", "-i", f"anullsrc=channel_layout=mono:sample_rate=24000", # Using 24kHz like our main pipeline
                "-t", "2", dummy_audio_file, "-y"
            ], check=True)
            print(f"'{dummy_audio_file}' created.")
        except Exception as e:
            print(f"Could not create dummy '{dummy_audio_file}': {e}. Please provide an audio file for testing.")
    
    if os.path.exists(dummy_audio_file):
        print(f"\n--- Testing transcription with '{selected_model_name}' model ---")
        try:
            # Construct path to the model file for the test
            model_file_path_for_test = os.path.join("models", "whisper", f"{selected_model_name}.pt")
            if not os.path.exists(model_file_path_for_test):
                print(f"Test SKIPPED: Model file {model_file_path_for_test} not found for testing.")
            else:
                text, lang = transcribe_audio(dummy_audio_file, model_name=selected_model_name)
                if text is not None and lang is not None: # Check for None, as empty string is a valid transcription
                    print(f"Successfully transcribed '{dummy_audio_file}'")
                    print(f"Language: {lang}")
                    print(f"Text: '{text}'")
                else:
                    print(f"Transcription test failed or returned None for '{dummy_audio_file}'.")
        except FileNotFoundError as fnf_error:
            print(f"Test FAILED: {fnf_error}")
        except RuntimeError as rt_error:
            print(f"Test FAILED: {rt_error}")
        except Exception as ex:
            print(f"Test FAILED with unexpected error: {ex}")
    else:
        print(f"Skipping example usage as '{dummy_audio_file}' was not found/created.")
