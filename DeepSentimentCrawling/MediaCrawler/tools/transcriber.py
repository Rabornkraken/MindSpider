import os
import logging
from typing import Optional

logger = logging.getLogger("Transcriber")

# Check for FunASR
try:
    from funasr import AutoModel
    FUNASR_AVAILABLE = True
except ImportError:
    FUNASR_AVAILABLE = False

class VideoTranscriber:
    _model = None

    @classmethod
    def get_model(cls):
        if not FUNASR_AVAILABLE:
            logger.error("funasr not installed. Please run: pip install funasr modelscope torchaudio")
            return None
            
        if cls._model is None:
            logger.info("Loading SenseVoiceSmall model ...")
            try:
                import torch
                if torch.cuda.is_available():
                    device = "cuda"
                elif torch.backends.mps.is_available():
                    device = "mps"
                else:
                    device = "cpu"
                
                logger.info(f"Using device: {device}")

                # Load SenseVoiceSmall
                cls._model = AutoModel(
                    model="iic/SenseVoiceSmall",
                    trust_remote_code=True,
                    device=device,
                    disable_update=True
                )
                logger.info("SenseVoiceSmall model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load SenseVoiceSmall model: {e}")
                return None
        return cls._model

    @staticmethod
    def transcribe_video(video_path: str) -> str:
        """
        Transcribe a video file using SenseVoiceSmall.
        """
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return ""

        model = VideoTranscriber.get_model()
        if not model:
            return ""

        try:
            logger.info(f"Starting transcription for: {video_path}")
            # SenseVoice uses 'generate' but arguments might slightly differ.
            # It usually supports language="auto" or specific.
            res = model.generate(
                input=video_path,
                cache={}, 
                language="auto", # auto detect language
                use_itn=True,
                batch_size_s=60,
                merge_vad=True,
                merge_length_s=15
            )
            
            # Result parsing
            text = ""
            if res and isinstance(res, list):
                text = res[0].get("text", "")
            
            # Clean up text (SenseVoice sometimes includes tags like <|zh|>)
            import re
            text = re.sub(r'<\|.*?\|>', '', text).strip()
            
            logger.info(f"Transcription complete. Length: {len(text)} chars")
            return text
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""
