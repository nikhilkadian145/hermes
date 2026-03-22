import os
import subprocess
import tempfile

_model_cache = {}

def _check_ffmpeg():
    """Check if FFmpeg is installed and accessible in the system PATH."""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def _convert_to_wav(audio_path: str, output_path: str):
    """Convert audio to a 16kHz mono WAV format compatible with Whisper."""
    cmd = [
        "ffmpeg",
        "-i", audio_path,
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        "-y",
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def _load_model(model_size: str):
    """Loads the Whisper model, caching it in memory to avoid repetitive slow loads."""
    # We import whisper here to avoid heavy PyTorch imports on app startup
    import whisper
    
    if model_size not in _model_cache:
        # device="cpu" is safer by default unless we specifically check for CUDA torch
        _model_cache[model_size] = whisper.load_model(model_size)
    return _model_cache[model_size]

def transcribe(audio_path: str, model_size: str = "small", language: str = None) -> dict:
    """
    Transcribes an audio file into text using OpenAI's Whisper model.
    Returns: {text, language, duration_seconds, success, raw_response}
    """
    error_dict = {
        "text": "",
        "language": None,
        "duration_seconds": 0.0,
        "success": False,
        "raw_response": ""
    }

    if not os.path.exists(audio_path):
        error_dict["raw_response"] = f"Audio file not found: {audio_path}"
        return error_dict

    if not _check_ffmpeg():
        error_dict["raw_response"] = "FFmpeg is not installed or not in PATH."
        return error_dict

    wav_path = None
    try:
        # Convert audio to wav if needed
        fd, wav_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        
        _convert_to_wav(audio_path, wav_path)
        
        # Load cached model
        model = _load_model(model_size)
        
        # Transcribe
        # If language is None, Whisper auto-detects
        transcribe_args = {}
        if language:
            transcribe_args["language"] = language
            
        result = model.transcribe(wav_path, **transcribe_args)
        
        # Calculate duration roughly using ffmpeg or parse from result segments
        duration = 0.0
        if "segments" in result and len(result["segments"]) > 0:
            duration = result["segments"][-1].get("end", 0.0)

        return {
            "text": result.get("text", "").strip(),
            "language": result.get("language", language),
            "duration_seconds": duration,
            "success": True,
            "raw_response": "Transcribed successfully."
        }
        
    except Exception as e:
        error_dict["raw_response"] = f"Transcription failed: {str(e)}"
        return error_dict
    finally:
        if wav_path and os.path.exists(wav_path):
            os.remove(wav_path)
