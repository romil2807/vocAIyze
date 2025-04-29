from pathlib import Path
import os
from openai import OpenAI
from pydub import AudioSegment
from pydub.playback import play
import logging
import tempfile
import sys
import threading
sys.path.append('/usr/bin/ffmpeg')  # Ensure ffmpeg is in path

logger = logging.getLogger("vocAIyze.TTS")

class TextToSpeech:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.speech_file_path = Path(__file__).parent / "speech.mp3"
        self.available_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        
        # Voice personality mapping
        self.voice_personalities = {
            "formal_male": "onyx",
            "formal_female": "nova", 
            "casual_male": "echo",
            "casual_female": "alloy",
            "friendly": "shimmer",
            "storytelling": "fable"
        }
        
        # Language-specific voices (would be expanded)
        self.language_voices = {
            "English": self.available_voices,
            "Spanish": self.available_voices,
            "French": self.available_voices,
            "German": self.available_voices,
            "Chinese": self.available_voices,
            "Japanese": self.available_voices
        }
        
        self.current_voice = os.getenv("DEFAULT_VOICE", "alloy")  # Default voice
        self.is_speaking = False
        self.stop_requested = False
        logger.info("TextToSpeech initialized")

    def text_to_speech(self, text: str, output_path: str = None, play_audio: bool = True):
        if not text:
            logger.warning("Empty text provided to text_to_speech")
            return
            
        try:
            self.is_speaking = True
            self.stop_requested = False
            
            # Use provided output path or default with absolute path
            file_path = output_path if output_path else str(Path(__file__).parent.absolute() / "speech.mp3")
            
            # Ensure text isn't too long (API limits)
            if len(text) > 4000:
                logger.warning(f"Text too long ({len(text)} chars), truncating to 4000 chars")
                text = text[:4000]
            
            logger.info(f"Converting text to speech, length: {len(text)} chars, voice: {self.current_voice}")
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=self.current_voice,
                input=text
            )
            
            # Ensure directory exists (create parent directories if needed)
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Save to file
            response.stream_to_file(file_path)
            logger.info(f"Speech saved to {file_path}")
            
            # Play audio if requested
            if play_audio and not self.stop_requested:
                try:
                    sound = AudioSegment.from_file(file_path)
                    play(sound)
                except Exception as e:
                    logger.error(f"Error playing audio: {str(e)}")
                    print(f"Could not play audio: {str(e)}")
            
            self.is_speaking = False
            return str(file_path)
                
        except Exception as e:
            self.is_speaking = False
            logger.error(f"Error in text_to_speech: {str(e)}")
            print(f"Text-to-speech error: {str(e)}")
            return None
    
    def stop_speaking(self):
        """Stop any ongoing speech"""
        self.stop_requested = True
        # Note: This doesn't actually stop playing audio immediately
        # Additional code would be required for immediate stopping
        logger.info("Stop speaking requested")
            
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
    
    def get_appropriate_voice(self, language: str, sentiment: str = "neutral", style: str = "formal") -> str:
        """
        Select an appropriate voice based on language, sentiment, and style
        
        Args:
            language: Target language
            sentiment: Detected sentiment (positive, negative, neutral)
            style: Voice style (formal, casual)
            
        Returns:
            Voice identifier
        """
        # Default to a neutral voice
        selected_voice = self.current_voice
        
        # Determine personality based on sentiment and style
        personality = f"{style}_"
        
        if sentiment == "negative":
            # More formal/authoritative voice for negative sentiment
            personality += "male" if personality == "formal_" else "female"
        else:
            # More casual/friendly voice for positive sentiment
            personality += "female" if personality == "formal_" else "male"
            
        # Get voice from personality map
        if personality in self.voice_personalities:
            selected_voice = self.voice_personalities[personality]
            
        # Ensure voice is available for this language (simplified check)
        if language in self.language_voices and selected_voice in self.language_voices[language]:
            return selected_voice
        else:
            # Fallback to default voice
            return self.current_voice
    
    def get_available_voices(self) -> list:
        """Returns list of available voice options"""
        return self.available_voices
    
    def get_voice_personalities(self) -> dict:
        """Returns mapping of personality types to voices"""
        return self.voice_personalities
        
    def text_to_speech_async(self, text: str, output_path: str = None, callback=None):
        """
        Perform text-to-speech conversion asynchronously
        
        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file
            callback: Function to call when complete
        """
        def _tts_worker():
            result = self.text_to_speech(text, output_path)
            if callback:
                callback(result)
                
        # Start in a separate thread
        tts_thread = threading.Thread(target=_tts_worker)
        tts_thread.daemon = True
        tts_thread.start()
        return tts_thread


if __name__ == "__main__":
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
        
    tts = TextToSpeech(api_key)
    
    # Demo voice selection based on sentiment
    print("Testing sentiment-based voice selection:")
    for sentiment in ["positive", "negative", "neutral"]:
        for style in ["formal", "casual"]:
            voice = tts.get_appropriate_voice("English", sentiment, style)
            print(f"For {sentiment} sentiment and {style} style, selected voice: {voice}")
    
    # Demo different voices
    print("\nTesting available voices:")
    for voice in tts.available_voices:
        print(f"Playing sample with voice: {voice}")
        tts.set_voice(voice)
        tts.text_to_speech(f"This is a sample of the {voice} voice from vocAIyze.")