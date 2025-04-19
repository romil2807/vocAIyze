from pathlib import Path
import os
from openai import OpenAI
from pydub import AudioSegment
from pydub.playback import play
import logging
import tempfile
import sys
sys.path.append('/usr/bin/ffmpeg')  # Ensure ffmpeg is in path

logger = logging.getLogger("vocAIyze.TTS")

class TextToSpeech:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.speech_file_path = Path(__file__).parent / "speech.mp3"
        self.available_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        self.current_voice = "alloy"  # Default voice
        logger.info("TextToSpeech initialized")

    def text_to_speech(self, text: str, output_path: str = None):
        if not text:
            logger.warning("Empty text provided to text_to_speech")
            return
            
        try:
            # Use provided output path or default with absolute path
            file_path = output_path if output_path else str(Path(__file__).parent.absolute() / "speech.mp3")
            
            # Ensure text isn't too long (API limits)
            if len(text) > 4000:
                logger.warning(f"Text too long ({len(text)} chars), truncating to 4000 chars")
                text = text[:4000]
            
            logger.info(f"Converting text to speech, length: {len(text)} chars")
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=self.current_voice,
                input=text
            )
            
            # Ensure directory exists (create parent directories if needed)
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Print debug info
            print(f"Saving speech to: {file_path}")
            
            # Save to file
            response.stream_to_file(file_path)
            logger.info(f"Speech saved to {file_path}")
            
            # Play audio if no output path specified (interactive mode)
            if not output_path:
                try:
                    sound = AudioSegment.from_file(file_path)
                    play(sound)
                except Exception as e:
                    logger.error(f"Error playing audio: {str(e)}")
                    print(f"Could not play audio: {str(e)}")
                
            return str(file_path)
                
        except Exception as e:
            logger.error(f"Error in text_to_speech: {str(e)}")
            print(f"Text-to-speech error: {str(e)}")
            return None
            
    def set_voice(self, voice_name: str) -> bool:
        """
        Set the voice to use for TTS
        
        Args:
            voice_name: Name of the voice to use
            
        Returns:
            bool: True if successful, False if voice not available
        """
        if voice_name.lower() in [v.lower() for v in self.available_voices]:
            self.current_voice = voice_name.lower()
            logger.info(f"Voice set to {self.current_voice}")
            return True
        else:
            logger.warning(f"Voice '{voice_name}' not available. Using {self.current_voice}")
            return False
    
    def get_available_voices(self) -> list:
        """Returns list of available voice options"""
        return self.available_voices


if __name__ == "__main__":
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
        
    tts = TextToSpeech(api_key)
    
    # Demo different voices
    for voice in tts.available_voices:
        print(f"Playing sample with voice: {voice}")
        tts.set_voice(voice)
        tts.text_to_speech(f"This is a sample of the {voice} voice from vocAIyze.")