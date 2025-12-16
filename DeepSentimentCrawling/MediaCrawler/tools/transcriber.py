import os
import logging
from typing import Optional

# Check if whisper is available
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

logger = logging.getLogger("Transcriber")

class VideoTranscriber:
    _model = None

    @classmethod
    def get_model(cls, model_name="base"):
        if not WHISPER_AVAILABLE:
            logger.error("openai-whisper not installed. Please run: pip install openai-whisper")
            return None
            
        if cls._model is None:
            logger.info(f"Loading Whisper model: {model_name} ...")
            try:
                cls._model = whisper.load_model(model_name)
                logger.info("Whisper model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                return None
        return cls._model

    @staticmethod
    def transcribe_video(video_path: str) -> str:
        """
        Transcribe a video file using OpenAI Whisper.
        Returns the transcribed text.
        """
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return ""

        model = VideoTranscriber.get_model()
        if not model:
            return ""

        try:
            logger.info(f"Starting transcription for: {video_path}")
            result = model.transcribe(video_path)
            text = result["text"].strip()
            logger.info(f"Transcription complete. Length: {len(text)} chars")
            return text
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""
