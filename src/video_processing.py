import os
import subprocess
import re
import youtube_dl

def upload_video(video_path):
    """
    Placeholder function for uploading a video.
    This will be adapted for Streamlit's file uploader.
    """
    # In a Streamlit app, this would use st.file_uploader
    print("Placeholder: Implement video upload with Streamlit's file_uploader")
    if video_path and os.path.exists(video_path):
        return video_path
    return None

def download_youtube_video(youtube_url, output_path="downloaded_video.mp4"):
    """Downloads a video from YouTube."""
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'retries': 10,
        'socket_timeout': 300,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True, # To potentially bypass some SSL issues if they arise
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
    except Exception as e:
        error_message = f"Failed to download YouTube video from {youtube_url}. Error: {str(e)}. Please check the link and your internet connection."
        print(error_message)
        raise ValueError(error_message)
    return output_path

def resize_video(video_path, output_path="resized_video.mp4", target_width=720, target_height=720):
    """Resizes a video to the target width and height using ffmpeg."""
    # Check if video dimensions are already as desired
    try:
        cmd_probe = [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", video_path
        ]
        process = subprocess.run(cmd_probe, capture_output=True, text=True, check=False)
        if process.returncode != 0:
            raise RuntimeError(f"ffprobe failed to get video dimensions. Error: {process.stderr}")
        width, height = map(int, process.stdout.strip().split('x'))

        if width == target_width and height == target_height:
            print(f"Video is already {target_width}x{target_height}. No resize needed.")
            if video_path != output_path:
                 cp_process = subprocess.run(["cp", video_path, output_path], check=False, capture_output=True, text=True)
                 if cp_process.returncode != 0:
                     raise RuntimeError(f"Failed to copy video: {cp_process.stderr}")
            return output_path

        # Get video duration
        cmd_duration = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", video_path
        ]
        duration_process = subprocess.run(cmd_duration, capture_output=True, text=True, check=False)
        if duration_process.returncode != 0:
            raise RuntimeError(f"ffprobe failed to get video duration. Error: {duration_process.stderr}")
        duration_str = duration_process.stdout.strip()
        duration = float(duration_str)
        output_options = []
        if duration > 60: # if video is longer than 60s, then cut it to 60s
            output_options = ["-t", "60"]

        cmd_resize = [
            "ffmpeg", "-i", video_path, "-vf",
            f"scale=w={target_width}:h={target_height}:force_original_aspect_ratio=decrease,pad=w={target_width}:h={target_height}:x=(ow-iw)/2:y=(oh-ih)/2,setsar=1",
            "-c:a", "copy", *output_options, output_path, "-y"
        ]
        print(f"Executing ffmpeg resize command: {' '.join(cmd_resize)}")
        resize_process = subprocess.run(cmd_resize, check=False, capture_output=True, text=True)
        if resize_process.returncode != 0:
            error_message = f"ffmpeg command failed during video resize. Error: {resize_process.stderr}"
            print(error_message)
            raise RuntimeError(error_message)
        print(f"Video resized successfully to {output_path}")
    except Exception as e:
        # Catch any other exception during the process (e.g., float conversion if duration_str is empty)
        error_message = f"An error occurred during video resizing: {str(e)}"
        print(error_message)
        raise RuntimeError(error_message)
    return output_path

def extract_audio(video_path, output_audio_path="audio.wav"):
    """
    Extracts audio from a video file using ffmpeg, resampling to 24kHz and 16-bit PCM.
    This is optimized for Coqui XTTSv2 (24kHz) and generally good for Whisper/Wav2Lip.
    """
    command = [
        "ffmpeg", "-i", video_path,
        "-vn",  # No video output
        "-acodec", "pcm_s16le",  # Audio codec: PCM signed 16-bit little-endian
        "-ar", "24000",  # Audio sample rate: 24kHz
        "-ac", "1",  # Audio channels: 1 (mono)
        # "-q:a", "0", # Highest quality for the chosen codec - often implicit for PCM
        output_audio_path,
        "-y"  # Overwrite output file if it exists
    ]
    print(f"Executing ffmpeg audio extract command: {' '.join(command)}")
    try:
        extract_process = subprocess.run(command, check=False, capture_output=True, text=True)
        if extract_process.returncode != 0:
            error_message = f"ffmpeg command failed during audio extraction. Error: {extract_process.stderr}"
            print(error_message)
            raise RuntimeError(error_message)
        print(f"Audio extracted successfully to {output_audio_path}")
    except subprocess.CalledProcessError as e: # Should be caught by check=False and returncode check, but as fallback
        error_message = f"ffmpeg command failed during audio extraction (CalledProcessError). Error: {e.stderr}"
        print(error_message)
        raise RuntimeError(error_message)
    except Exception as e:
        error_message = f"An unexpected error occurred during audio extraction: {str(e)}"
        print(error_message)
        raise RuntimeError(error_message)
    return output_audio_path
