import os
from unittest.mock import patch, MagicMock
from pathlib import Path
from tempfile import TemporaryDirectory

from hermes.whisper_tool import transcribe, _check_ffmpeg

@patch("hermes.whisper_tool.subprocess.run")
def test_check_ffmpeg_success(mock_run):
    # Simulate ffmpeg returning 0
    mock_run.return_value = MagicMock(returncode=0)
    assert _check_ffmpeg() is True

@patch("hermes.whisper_tool.subprocess.run")
def test_check_ffmpeg_failure(mock_run):
    # Simulate ffmpeg not found
    mock_run.side_effect = FileNotFoundError("ffmpeg not found")
    assert _check_ffmpeg() is False

@patch("hermes.whisper_tool._check_ffmpeg")
@patch("hermes.whisper_tool._convert_to_wav")
@patch("hermes.whisper_tool._load_model")
def test_transcribe_success(mock_load_model, mock_convert, mock_check_ffmpeg):
    # Setup mocks
    mock_check_ffmpeg.return_value = True
    
    mock_result = {
        "text": "Aaj petrol bhara 500 ruppee.",
        "language": "hi",
        "segments": [{"end": 3.4}]
    }
    
    mock_model = MagicMock()
    mock_model.transcribe.return_value = mock_result
    mock_load_model.return_value = mock_model

    with TemporaryDirectory() as tmpdir:
        # Create a dummy audio file
        audio_path = str(Path(tmpdir) / "voice_note.ogg")
        with open(audio_path, "w") as f:
            f.write("dummy audio content")
            
        result = transcribe(audio_path, model_size="tiny", language="hi")
        
        assert result["success"] is True
        assert result["text"] == "Aaj petrol bhara 500 ruppee."
        assert result["language"] == "hi"
        assert result["duration_seconds"] == 3.4
        
        # Verify ffmpeg converter was called
        mock_convert.assert_called_once()
        # Verify model was called
        mock_model.transcribe.assert_called_once()

@patch("hermes.whisper_tool._check_ffmpeg")
def test_transcribe_missing_ffmpeg(mock_check_ffmpeg):
    mock_check_ffmpeg.return_value = False
    
    with TemporaryDirectory() as tmpdir:
        audio_path = str(Path(tmpdir) / "voice_note.ogg")
        with open(audio_path, "w") as f:
            f.write("dummy audio content")
            
        result = transcribe(audio_path)
        assert result["success"] is False
        assert "not installed" in result["raw_response"]

def test_transcribe_missing_file():
    result = transcribe("non_existent.ogg")
    assert result["success"] is False
    assert "not found" in result["raw_response"]
