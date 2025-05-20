# AI Lip Sync Tool

This project is a Streamlit web application that provides a user interface for a comprehensive video translation and lip-syncing pipeline. It allows users to upload a video or provide a YouTube link, transcribe the audio, translate it to a target language, synthesize speech in the target language using the original voice characteristics (voice cloning), and finally, perform lip synchronization on the original video with the new audio.

The pipeline integrates several state-of-the-art machine learning models:
*   **Video Processing:** `ffmpeg`, `yt-dlp` (via `youtube-dl` wrapper or direct use)
*   **Audio Transcription:** OpenAI's Whisper
*   **Text Translation:** Google Translate API (via `googletrans` library)
*   **Speech Synthesis (TTS) with Voice Cloning:** Coqui TTS (XTTSv2 model)
*   **Lip Synchronization:**
    *   Wav2Lip (Normal Quality)
    *   Video-Retalking (High Quality)

## Project Structure

```
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── models/                 # Directory for storing downloaded ML models (Whisper, Coqui TTS)
│   ├── .gitkeep
│   ├── tts/
│   │   └── xtts_v2/        # For Coqui XTTSv2 model files
│   │       └── .gitkeep
│   └── whisper/            # For Whisper model files (.pt)
│       └── .gitkeep
├── src/                    # Source code for different processing modules
│   ├── __init__.py
│   ├── lip_sync.py
│   ├── speech_synthesis.py
│   ├── transcription.py
│   ├── translation.py
│   ├── utils.py
│   └── video_processing.py
├── tests/                  # Unit tests
│   ├── __init__.py
│   └── test_processing_logic.py
├── temp_processing_space/  # Temporary directory for intermediate files (auto-cleaned by app)
├── vendor/                 # For cloned external repositories (Wav2Lip, Video-Retalking)
│   └── .gitkeep
└── results/                # Default output directory for some lip_sync CLI tools (not used by Streamlit app directly)
```

## Features

*   **Video Input:** Upload video files or download from YouTube links.
*   **Configurable Transcription:** Audio transcription using OpenAI's Whisper with selectable model sizes (tiny, base, small, medium, large) for balancing speed and accuracy.
*   **Multilingual Translation:** Translation of transcribed text to a wide range of languages using Google Translate.
*   **Voice Cloning TTS:** Speech synthesis in the target language using Coqui TTS (XTTSv2), cloning the voice characteristics from the original audio.
*   **Dual Lip-Sync Quality Modes:**
    *   Normal Quality: Faster processing using Wav2Lip.
    *   High Quality: Slower, more accurate processing using Video-Retalking.
*   **Video Processing Options:** Optional video resizing to 720p for potentially better results and faster processing with lip-sync models.
*   **User-Friendly Interface:** Streamlined Streamlit web application with clear controls and progress indicators.
*   **Integrated Setup Instructions:** Detailed, step-by-step guidance for downloading AI models and setting up vendor repositories (Wav2Lip, Video-Retalking) is available directly within the application's sidebar.
*   **Automatic Cleanup:** Temporary files and directories created during processing are automatically cleaned up.
*   **Error Handling:** Improved error messages to guide users in case of issues (e.g., missing models, invalid inputs).

## Prerequisites

*   **Python:** Version 3.8 or higher is recommended.
*   **`ffmpeg`:** This utility must be installed on your system and accessible in your system's PATH. `ffmpeg` is crucial for video and audio processing tasks performed by the application.
    *   **Installation (Linux - Ubuntu/Debian):**
        ```bash
        sudo apt-get update && sudo apt-get install ffmpeg
        ```
    *   **Installation (macOS with Homebrew):**
        ```bash
        brew install ffmpeg
        ```
    *   **Installation (Windows):** Download binaries from the [official ffmpeg website](https://ffmpeg.org/download.html) and add the `bin` directory to your system's PATH environment variable.

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url> # Replace <repository_url> with the actual URL
    cd <repository_name>       # Replace <repository_name> with the cloned directory name
    ```

2.  **Create and Activate a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # venv\Scripts\activate   # On Windows
    ```

3.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: If you encounter issues with PyTorch installation (a dependency of Whisper and TTS), especially if you intend to use a GPU, please refer to the [official PyTorch website](https://pytorch.org/get-started/locally/) for specific installation commands tailored to your OS and CUDA version.*

4.  **Model and Vendor Repository Setup:**
    *   This application requires several AI models and external codebases (Wav2Lip, Video-Retalking).
    *   **Detailed, step-by-step instructions for downloading all necessary AI models (for Whisper, Coqui TTS) and for cloning and setting up the vendor repositories (Wav2Lip, Video-Retalking, including their specific models and Python dependencies) are available *within the application itself*.**
    *   Once you run the application (see step 5), look for the "📚 Setup & Instructions" section in the sidebar. These instructions will guide you through:
        *   Placing Whisper `.pt` model files into the `models/whisper/` directory.
        *   Placing Coqui XTTSv2 model files into the `models/tts/xtts_v2/` directory.
        *   Cloning the `Wav2Lip` and `video-retalking` repositories into the `vendor/` directory.
        *   Downloading all required checkpoints for Wav2Lip and Video-Retalking and placing them in the correct subdirectories within `vendor/`.
        *   Installing any specific Python dependencies for `Wav2Lip` and `video-retalking` from their respective `requirements.txt` files.
    *   The `models/` directory is for pre-trained model files that are directly loaded by `src` modules.
    *   The `vendor/` directory is for external Git repositories that contain their own inference scripts and model files, which our application calls.

5.  **Running the Application:**
    Once the prerequisites and dependencies are installed, run the Streamlit application:
    ```bash
    streamlit run app.py
    ```
    This will typically open the application in your default web browser.

6.  **Using the Application:**
    *   Follow the setup instructions in the sidebar if you haven't already.
    *   Use the controls in the sidebar to:
        *   Upload a video file or provide a YouTube URL.
        *   Select the target language for translation.
        *   Choose the Whisper model size (this affects transcription speed and accuracy).
        *   Select the desired lip-sync quality ("Normal" for Wav2Lip, "High Quality" for Video-Retalking).
        *   Optionally, enable video resizing to 720p.
    *   Click the "🚀 Start Processing" button.
    *   Monitor the progress messages. The final video will be displayed and available for download.

## Resource Requirements

This application is resource-intensive due to the nature of the machine learning models it employs.

*   **RAM:** Significant RAM is required, especially for loading multiple models. Expect usage to be in the range of several GBs, potentially **8-16GB or more** depending on the chosen models (e.g., larger Whisper models, Video-Retalking).
*   **GPU:** While some models can run on CPU, a CUDA-enabled GPU is **highly recommended** for acceptable performance, particularly for:
    *   Whisper (especially larger models: medium, large)
    *   Coqui TTS (XTTSv2)
    *   Wav2Lip
    *   Video-Retalking
    GPU memory requirements can be substantial (e.g., **6GB+ VRAM** is a good starting point; more is better for high-quality settings or larger models). Without a GPU, processing will be extremely slow.
*   **Storage:** You will need disk space for:
    *   The Python environment and dependencies (approx. 5-10GB, depending on PyTorch/CUDA versions).
    *   Downloaded model files (Whisper models: ~200MB to 3GB; Coqui TTS: ~2-3GB; Wav2Lip/Video-Retalking checkpoints: several GBs).
    *   Cloned vendor repositories.
    *   Temporary files generated during processing.
    A rough estimate for total storage could be **15-30GB**, depending on the number of models downloaded.
*   **Processing Time:** Processing times can be considerable, ranging from several minutes to much longer (potentially hours for long videos with high-quality settings on less powerful hardware). This depends heavily on:
    *   Video duration and resolution.
    *   Selected model sizes and quality settings (e.g., Video-Retalking is much slower than Wav2Lip).
    *   Hardware capabilities (CPU vs. GPU, specific GPU model and VRAM).

It is advisable to run this application on a machine with a dedicated GPU and ample RAM for a smoother experience. If running on lower-spec hardware, expect very long processing times; use the smallest Whisper model size and "Normal" quality lip-sync.

## License

This project is released under the MIT License. See the `LICENSE` file for details. (Assuming a LICENSE file exists or will be added).

*(Note: Any "Contact Us" or specific "Acknowledgments" from the original Colab notebook have been removed as they are typically specific to the original authors and context. If this project is a direct derivative and those are still applicable, they can be re-added.)*
