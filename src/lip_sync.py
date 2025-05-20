import os
import subprocess

# Base directory for vendored models like Video-Retalking and Wav2Lip
VENDOR_DIR = "vendor"
VIDEO_RETALKING_DIR = os.path.join(VENDOR_DIR, "video-retalking") # Corrected path
WAV2LIP_DIR = os.path.join(VENDOR_DIR, "Wav2Lip")


# --- Video Retalking (High Quality) ---
def get_video_retalking_readme_instructions():
    """
    Returns markdown formatted instructions for setting up Video-Retalking.
    """
    instructions = """
    ## Video-Retalking Setup Instructions

    1.  **Clone the Repository:**
        ```bash
        git clone https://github.com/vinthony/video-retalking.git vendor/video-retalking
        ```
        (Ensure the `vendor` directory exists in your project root, or adjust path accordingly.)

    2.  **Install Dependencies:**
        It's highly recommended to use a virtual environment.
        ```bash
        cd vendor/video-retalking
        pip install -r requirements.txt
        # Additional installations (from original notebook, may vary by system):
        # sudo apt-get install build-essential python-dev # For some dependencies
        python setup.py develop # For third_part/face_alignment, GFPGAN, GPEN (run in respective subdirs or check main setup)

        # Check Video-Retalking's README for detailed and up-to-date dependency installation,
        # especially for `face_alignment`, `GFPGAN`, and `GPEN` which might have their own setup scripts.
        # Example:
        # cd third_part/face_alignment && python setup.py install && cd ../../
        # cd third_part/GFPGAN && python setup.py develop && cd ../../
        # cd third_part/GPEN && python setup.py develop && cd ../../
        ```

    3.  **Download Checkpoints:**
        Download the following files and place them into `vendor/video-retalking/checkpoints/`:

        *   `shape_predictor_68_face_landmarks.dat`: [Download Link](https://github.com/JeffTrain/selfie/raw/master/shape_predictor_68_face_landmarks.dat)
        *   `25_net_G.pth`: [Download Link](https://github.com/vinthony/video-retalking/releases/download/v0.0.1/25_net_G.pth)
        *   `BFM_Fitting.zip`: [Download Link](https://github.com/vinthony/video-retalking/releases/download/v0.0.1/BFM_Fitting.zip)
            *   **Unzip this file**: After downloading, extract `BFM_Fitting.zip` into the `vendor/video-retalking/checkpoints/` directory. It should create a `BFM` subfolder there.
        *   `DNet.pt`: [Download Link](https://github.com/vinthony/video-retalking/releases/download/v0.0.1/DNet.pt)
        *   `expression_net.pt`: [Download Link](https://github.com/vinthony/video-retalking/releases/download/v0.0.1/expression_net.pt)
        *   `face_alignment_model.zip`: [Download Link](https://github.com/vinthony/video-retalking/releases/download/v0.0.1/face_alignment_model.zip)
             *   **Unzip this file**: After downloading, extract `face_alignment_model.zip` into `vendor/video-retalking/checkpoints/`.
        *   `GFPGANv1.3.pth`: [Download Link](https://github.com/vinthony/video-retalking/releases/download/v0.0.1/GFPGANv1.3.pth)
        *   `GPEN-BFR-512.pth`: [Download Link](https://github.com/vinthony/video-retalking/releases/download/v0.0.1/GPEN-BFR-512.pth)
        *   `ParseNet-latest.pth`: [Download Link](https://github.com/vinthony/video-retalking/releases/download/v0.0.1/ParseNet-latest.pth)
        *   `RetalkingHead.pt`: [Download Link](https://github.com/vinthony/video-retalking/releases/download/v0.0.1/RetalkingHead.pt)

        Expected structure for some key files:
        ```
        vendor/video-retalking/
        ├── checkpoints/
        │   ├── 25_net_G.pth
        │   ├── RetalkingHead.pt
        │   ├── BFM/  (from BFM_Fitting.zip)
        │   │   └── ...
        │   ├── DNet.pt
        │   ├── GFPGANv1.3.pth
        │   └── ... (other .pth and .dat files)
        ├── inference.py
        └── ... (rest of the repository)
        ```

    4.  **Verify Paths in `src/lip_sync.py`:**
        The `VIDEO_RETALKING_DIR` variable in `src/lip_sync.py` should correctly point to `vendor/video-retalking`.
    """
    return instructions


def run_video_retalking(video_path, audio_path, output_path="results/retalked_video.mp4"):
    """
    Runs Video Retalking inference.
    Assumes Video-Retalking repository and models are set up in VENDOR_DIR.
    """
    video_path_abs = os.path.abspath(video_path)
    audio_path_abs = os.path.abspath(audio_path)
    output_path_abs = os.path.abspath(output_path)
    
    os.makedirs(os.path.dirname(output_path_abs), exist_ok=True)

    # Check if the Video-Retalking directory and a key checkpoint exist
    if not os.path.isdir(VIDEO_RETALKING_DIR):
        error_msg = f"Video-Retalking directory not found at '{VIDEO_RETALKING_DIR}'. Please follow setup instructions."
        print(error_msg)
        raise FileNotFoundError(error_msg)
        
    expected_checkpoint = os.path.join(VIDEO_RETALKING_DIR, "checkpoints", "RetalkingHead.pt") # A key checkpoint
    if not os.path.exists(expected_checkpoint):
        error_msg = f"Video-Retalking key checkpoint not found at '{expected_checkpoint}'. Ensure models are downloaded correctly."
        print(error_msg)
        raise FileNotFoundError(error_msg)

    print(f"Running Video-Retalking on {video_path_abs} with audio {audio_path_abs}...")
    command = [
        "python", "inference.py",
        "--face", video_path_abs, 
        "--audio", audio_path_abs, 
        "--outfile", output_path_abs 
    ]
    try:
        process = subprocess.run(command, cwd=VIDEO_RETALKING_DIR, check=False, capture_output=True, text=True)
        if process.returncode != 0:
            error_message = f"Video-Retalking inference.py script failed with return code {process.returncode}.\n" \
                            f"Stdout: {process.stdout}\nStderr: {process.stderr}"
            print(error_message)
            raise RuntimeError(error_message)
        
        print(f"Video-Retalking finished. Output: {output_path_abs}")
        # print(f"Stdout: {process.stdout}") # Can be very verbose
        if process.stderr: # Print stderr if any, even on success, for warnings
            print(f"Video-Retalking Stderr (may contain warnings): {process.stderr}")
        return output_path_abs
    except FileNotFoundError as fnf_error: # e.g. if python or inference.py is not found
        error_msg = f"Could not execute Video-Retalking script. Ensure Python is in PATH and script exists: {fnf_error}"
        print(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e: # Catch any other unexpected error during subprocess execution
        error_msg = f"An unexpected error occurred during Video-Retalking execution: {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg)

# --- Wav2Lip (Normal Quality) ---
def get_wav2lip_readme_instructions():
    """
    Returns markdown formatted instructions for setting up Wav2Lip.
    """
    instructions = """
    ## Wav2Lip Setup Instructions

    1.  **Clone the Repository:**
        ```bash
        git clone https://github.com/Rudrabha/Wav2Lip.git vendor/Wav2Lip
        ```
        (Ensure the `vendor` directory exists in your project root.)

    2.  **Install Dependencies:**
        It's highly recommended to use a virtual environment.
        ```bash
        cd vendor/Wav2Lip
        pip install -r requirements.txt 
        # Wav2Lip often has specific dependencies.
        # The notebook used requirements_colab.txt for some parts.
        # Ensure opencv-python, librosa, numba, scipy, and torch are compatible.
        # A specific numpy version might be needed (e.g., numpy==1.23.4 was seen in Colab logs for Wav2Lip).
        # Our main requirements.txt tries to manage this.
        ```

    3.  **Download Checkpoints:**
        Download the following model files and place them as specified:

        *   **`wav2lip_gan.pth`**: [Download Link from Wav2Lip Repo README or issue #144 for alternatives](https://github.com/Rudrabha/Wav2Lip/issues/144)
            *   Place this file in: `vendor/Wav2Lip/checkpoints/wav2lip_gan.pth`
            *   (The original Colab used a SharePoint link which can be unreliable. Check the Wav2Lip repo for current official links.)
            *   Alternative: `https://www.adrianbulat.com/downloads/python/wav2lip/wav2lip_gan.pth` (often cited)

        *   **`wav2lip.pth`** (Non-GAN version, if you prefer): [Download Link from Wav2Lip Repo]
            *   Place this file in: `vendor/Wav2Lip/checkpoints/wav2lip.pth`

        *   **`s3fd.pth`** (Face detector model): [Download Link - often from adrianbulat.com](https://www.adrianbulat.com/downloads/python/landmark_models/s3fd-619a316812.pth)
            *   Place this file in: `vendor/Wav2Lip/face_detection/detection/sfd/s3fd.pth`
            *   (The Wav2Lip code expects it here: `face_detection/detection/sfd/s3fd-619a316812.pth`. Ensure the filename matches what `face_detection.py` expects or modify the script.)
            *   It is often better to rename the downloaded `s3fd-619a316812.pth` to `s3fd.pth` in that directory if the script looks for `s3fd.pth`. Or, ensure the script loads the full name.
            *   **Let's assume the script looks for `s3fd.pth` for simplicity of instructions.**

        *   **`shape_predictor_68_face_landmarks.dat`** (dlib landmark predictor):
            *   This is often shared. If you downloaded it for Video-Retalking, you can reuse it.
            *   Place it in `vendor/Wav2Lip/shape_predictor_68_face_landmarks.dat` (root of Wav2Lip repo).
            *   [Download Link](https://github.com/JeffTrain/selfie/raw/master/shape_predictor_68_face_landmarks.dat)

        Expected structure for some key files:
        ```
        vendor/Wav2Lip/
        ├── checkpoints/
        │   └── wav2lip_gan.pth  (or wav2lip.pth)
        ├── face_detection/detection/sfd/
        │   └── s3fd.pth
        ├── shape_predictor_68_face_landmarks.dat
        ├── inference.py
        └── ... (rest of the repository)
        ```

    4.  **Verify Paths in `src/lip_sync.py`:**
        The `WAV2LIP_DIR` variable in `src/lip_sync.py` should correctly point to `vendor/Wav2Lip`.
        The `run_wav2lip` function assumes the `--checkpoint_path` is relative to `WAV2LIP_DIR` (e.g., `checkpoints/wav2lip_gan.pth`).
    """
    return instructions


def run_wav2lip(video_path, audio_path, output_path="results/wav2lip_video.mp4",
                pads=(0, 10, 0, 0), resize_factor=1, nosmooth=False):
    """
    Runs Wav2Lip inference.
    Assumes Wav2Lip repository and models are set up in VENDOR_DIR.
    """
    video_path_abs = os.path.abspath(video_path)
    audio_path_abs = os.path.abspath(audio_path)
    output_path_abs = os.path.abspath(output_path)

    os.makedirs(os.path.dirname(output_path_abs), exist_ok=True)

    # Path to the Wav2Lip checkpoint, relative to WAV2LIP_DIR
    # User must place the model here as per setup instructions
    wav2lip_checkpoint_filename = "wav2lip_gan.pth" # Or "wav2lip.pth"
    wav2lip_checkpoint_rel_path = os.path.join("checkpoints", wav2lip_checkpoint_filename)
    
    if not os.path.isdir(WAV2LIP_DIR):
        error_msg = f"Wav2Lip directory not found at '{WAV2LIP_DIR}'. Please follow setup instructions."
        print(error_msg)
        raise FileNotFoundError(error_msg)

    wav2lip_checkpoint_filename = "wav2lip_gan.pth" # Or "wav2lip.pth" if preferred
    wav2lip_checkpoint_rel_path = os.path.join("checkpoints", wav2lip_checkpoint_filename)
    wav2lip_checkpoint_abs_path = os.path.join(WAV2LIP_DIR, wav2lip_checkpoint_rel_path)
    if not os.path.exists(wav2lip_checkpoint_abs_path):
        error_msg = f"Wav2Lip model checkpoint not found at '{wav2lip_checkpoint_abs_path}'. Ensure models are downloaded."
        print(error_msg)
        raise FileNotFoundError(error_msg)
    
    face_detector_model_rel_path = os.path.join("face_detection", "detection", "sfd", "s3fd.pth")
    face_detector_model_abs_path = os.path.join(WAV2LIP_DIR, face_detector_model_rel_path)
    if not os.path.exists(face_detector_model_abs_path):
        error_msg = f"Wav2Lip face detector model not found at '{face_detector_model_abs_path}'. Ensure setup is complete."
        print(error_msg)
        raise FileNotFoundError(error_msg)

    print(f"Running Wav2Lip on {video_path_abs} with audio {audio_path_abs}...")
    command = [
        "python", "inference.py",
        "--checkpoint_path", wav2lip_checkpoint_rel_path, 
        "--face", video_path_abs,      
        "--audio", audio_path_abs,     
        "--outfile", output_path_abs,  
        "--pads", str(pads[0]), str(pads[1]), str(pads[2]), str(pads[3]),
        "--resize_factor", str(resize_factor)
    ]
    if nosmooth:
        command.append("--nosmooth")

    try:
        process = subprocess.run(command, cwd=WAV2LIP_DIR, check=False, capture_output=True, text=True)
        if process.returncode != 0:
            error_message = f"Wav2Lip inference.py script failed with return code {process.returncode}.\n" \
                            f"Stdout: {process.stdout}\nStderr: {process.stderr}"
            print(error_message)
            raise RuntimeError(error_message)
            
        print(f"Wav2Lip finished. Output: {output_path_abs}")
        # print(f"Stdout: {process.stdout}") # Can be verbose
        if process.stderr: # Print stderr if any, even on success
            print(f"Wav2Lip Stderr (may contain warnings): {process.stderr}")
        return output_path_abs
    except FileNotFoundError as fnf_error: # e.g. if python or inference.py is not found
        error_msg = f"Could not execute Wav2Lip script. Ensure Python is in PATH and script exists: {fnf_error}"
        print(error_msg)
        raise RuntimeError(error_msg)
    except Exception as e:
        error_msg = f"An unexpected error occurred during Wav2Lip execution: {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg)

if __name__ == '__main__':
    # This section is for testing and won't run when imported.
    # It requires dummy files and that the setup functions are run or models are already in place.
    # It requires dummy files and that the setup functions are run or models are already in place.

    print("Lip Sync Module - Example Usage (requires models to be set up and dummy files)")
    os.makedirs("results", exist_ok=True) # Ensure results directory exists for outputs
    os.makedirs("dummy_inputs", exist_ok=True)
    
    dummy_video = "dummy_inputs/dummy_video.mp4"
    dummy_audio = "dummy_inputs/dummy_audio.wav"

    # Create dummy video and audio if they don't exist (requires ffmpeg)
    if not os.path.exists(dummy_video):
        print("Creating dummy video for testing...")
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", "testsrc=duration=2:size=128x128:rate=25",
            "-vf", "format=yuv420p", dummy_video, "-y"
        ], check=True)
    if not os.path.exists(dummy_audio):
        print("Creating dummy audio for testing...")
        subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", "anullsrc=channel_layout=mono:sample_rate=16000",
            "-t", "2", dummy_audio, "-y"
        ], check=True)

    # --- Test Video Retalking ---
    print("\n--- Testing Video Retalking ---")
    # First, ensure models are downloaded and set up:
    # setup_video_retalking() # Call this if you haven't set it up manually or via a setup script
    if os.path.exists(VIDEO_RETALKING_DIR) and \
       os.path.exists(os.path.join(VIDEO_RETALKING_DIR, "checkpoints", "RetalkingHead.pt")):
        retalked_output = run_video_retalking(dummy_video, dummy_audio, "results/retalked_dummy.mp4")
        if retalked_output:
            print(f"Video Retalking test output: {retalked_output}")
        else:
            print("Video Retalking test failed or was skipped.")
    else:
        print("Skipping Video Retalking test: Model directory or checkpoint not found. Run setup_video_retalking() or check paths.")

    # --- Test Wav2Lip ---
    print("\n--- Testing Wav2Lip ---")
    # First, ensure models are downloaded and set up:
    # setup_wav2lip() # Call this if you haven't set it up manually
    if os.path.exists(WAV2LIP_DIR) and \
       os.path.exists(os.path.join(WAV2LIP_DIR, "checkpoints", "wav2lip_gan.pth")):
        wav2lip_output = run_wav2lip(dummy_video, dummy_audio, "results/wav2lip_dummy.mp4")
        if wav2lip_output:
            print(f"Wav2Lip test output: {wav2lip_output}")
        else:
            print("Wav2Lip test failed or was skipped.")
    else:
        print("Skipping Wav2Lip test: Model directory or checkpoint not found. Run setup_wav2lip() or check paths.")

    print("\nNote: The setup functions (setup_video_retalking, setup_wav2lip) contain commands "
          "for cloning repositories and downloading models. These are long-running and should ideally "
          "be part of a one-time setup process for your environment, not run every time the main application runs.")
