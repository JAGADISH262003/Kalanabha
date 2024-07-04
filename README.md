# Kalanabha Project

This project is an end-to-end system for translating and lip-syncing videos from one language to another. It combines state-of-the-art AI models for speech recognition, translation, text-to-speech synthesis, and lip-sync generation.

## Features

- Video input via file upload or YouTube URL
- Automatic speech recognition using OpenAI's Whisper
- Text translation using Google Translate API
- Text-to-speech synthesis with voice cloning capabilities using Coqui TTS
- Two lip-sync options:
  - High-quality lip-sync using Video Retalking
  - Normal-quality lip-sync using Wav2Lip
- Support for multiple languages
- Optional video resizing for optimal processing

## Prerequisites

- Python 3.7+
- CUDA-compatible GPU (for faster processing)
- FFmpeg
- Git

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/video-translation-lipsync.git
   cd video-translation-lipsync
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Install additional dependencies:
   ```
   pip install git+https://github.com/openai/whisper.git
   pip install TTS
   pip install youtube-dl
   pip install aksharamukha
   ```

4. Download the necessary model checkpoints (run the provided scripts in the notebook).

## Usage

1. Open the Jupyter notebook `kalanabha1.ipynb`.

2. Run the cells in order, following the instructions for each step.

3. When prompted, upload your video file or provide a YouTube URL.

4. Choose your target language and lip-sync quality option.

5. Wait for the processing to complete. The final video will be available for download.

## Components

- **Video Processing**: FFmpeg
- **Speech Recognition**: OpenAI's Whisper
- **Translation**: Google Translate API
- **Text-to-Speech**: Coqui TTS (XTTS v2 model)
- **Lip-Sync**: 
  - High Quality: Video Retalking
  - Normal Quality: Wav2Lip

## Limitations

- Processing time can be lengthy for longer videos.
- Lip-sync quality may vary depending on the input video quality and face angles.
- Translation accuracy depends on the Google Translate API.
- The system may struggle with heavily accented speech or poor audio quality.

## Contributing

Contributions to improve the project are welcome. Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License[

Distributed under the Apache-2.0 License. See `LICENSE` for more information.](http://www.apache.org/licenses/LICENSE-2.0)

## Acknowledgments

- OpenAI for the Whisper ASR system
- Google for the Translate API
- Coqui for the TTS system
- The creators of Video Retalking and Wav2Lip

## Contact

-Jagadish Itikala - i.jagadish@outlook.com
-Parasara Bandaru -
-Krishna Vamshi Yechuri - krishnavamshiyechuri@gmail.com
