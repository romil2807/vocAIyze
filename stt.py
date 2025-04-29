import pyaudio
import wave
import os
from openai import OpenAI
import logging
from pathlib import Path
import tempfile
import numpy as np

logger = logging.getLogger("vocAIyze.STT")

class SpeechToText:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.default_duration = 5
        self.model = "whisper-1"  # Default model
        self.is_recording = False
        logger.info("SpeechToText initialized")

    def record_audio(self, output_path: str, duration: int = None):
        """
        Record audio from the microphone
        
        Args:
            output_path: Path to save the recorded audio
            duration: Recording duration in seconds (default: self.default_duration)
        """
        if duration is None:
            duration = int(os.getenv("DEFAULT_RECORDING_DURATION", self.default_duration))
            
        chunk = 1024  # Record in chunks of 1024 samples
        sample_format = pyaudio.paInt16  # 16 bits per sample
        channels = 1
        fs = 44100  # Record at 44100 samples per second

        try:
            p = pyaudio.PyAudio()  # Create an interface to PortAudio

            logger.info(f"Recording for {duration} seconds...")
            print('Recording...')
            
            self.is_recording = True

            stream = p.open(format=sample_format,
                            channels=channels,
                            rate=fs,
                            frames_per_buffer=chunk,
                            input=True)

            frames = []  # Initialize array to store frames
            audio_levels = []  # Store audio levels for visualization

            # Store data in chunks for the specified duration
            for _ in range(0, int(fs / chunk * duration)):
                if not self.is_recording:
                    break
                    
                data = stream.read(chunk)
                frames.append(data)
                
                # Calculate audio level (root mean square of the amplitude)
                audio_array = np.frombuffer(data, dtype=np.int16)
                # Add a small epsilon to avoid sqrt of zero
                squared_values = np.square(audio_array)
                mean_squared = np.mean(squared_values) 
                if mean_squared > 0:
                    rms = np.sqrt(mean_squared)
                else:
                    rms = 0  # Handle silence case
                audio_levels.append(rms)
            # Stop and close the stream
            stream.stop_stream()
            stream.close()
            # Terminate the PortAudio interface
            p.terminate()
            
            self.is_recording = False

            print('Finished recording')
            logger.info("Recording finished")

            # Save the recorded data as a WAV file
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            wf = wave.open(output_path, 'wb')
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(sample_format))
            wf.setframerate(fs)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            logger.info(f"Audio saved to {output_path}")
            
            # Return path and average audio level for visualization
            return output_path, np.mean(audio_levels) if audio_levels else 0
            
        except Exception as e:
            self.is_recording = False
            logger.error(f"Error in record_audio: {str(e)}")
            raise

    def stop_recording(self):
        """Stop any ongoing recording"""
        self.is_recording = False
        logger.info("Recording manually stopped")

    def speech_to_text(self, audio_path: str, detect_language=False) -> dict:
        """
        Convert speech audio to text using OpenAI's Whisper API
        
        Args:
            audio_path: Path to the audio file
            detect_language: Whether to detect the language
            
        Returns:
            Dictionary with transcribed text and detected language
        """
        try:
            logger.info(f"Transcribing audio from {audio_path}")
            
            # Check if file exists
            if not os.path.exists(audio_path):
                logger.error(f"Audio file not found: {audio_path}")
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
                
            # Check file extension
            if not audio_path.lower().endswith(('.mp3', '.wav', '.m4a')):
                logger.warning(f"Unsupported file format: {audio_path}")
                
            with open(audio_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    response_format="json"
                )
                
            logger.info("Transcription completed successfully")
            
            # Handle the response correctly
            if hasattr(response, 'text'):
                transcribed_text = response.text
            elif isinstance(response, dict) and 'text' in response:
                transcribed_text = response['text']
            else:
                # Convert the entire response to string as fallback
                transcribed_text = str(response)
                logger.warning(f"Unexpected response format: {type(response)}")
            
            # For language detection
            detected_language = None
            if detect_language:
                if hasattr(response, 'language'):
                    detected_language = response.language
                elif isinstance(response, dict) and 'language' in response:
                    detected_language = response['language']
            
            return {
                "text": transcribed_text,
                "language": detected_language
            }
            
        except Exception as e:
            logger.error(f"Error in speech_to_text: {str(e)}")
            # Return empty result on error
            return {
                "text": "",
                "language": None
            }
    
    def detect_and_process_speech(self, audio_path: str):
        """
        Detect language from speech and process accordingly
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Dictionary with transcribed text and detected language
        """
        try:
            # For language detection, we need a separate call with the right format
            with open(audio_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=audio_file,
                    response_format="verbose_json"
                )
            
            # Extract text and language from response
            if hasattr(response, 'text') and hasattr(response, 'language'):
                transcribed_text = response.text
                detected_language = response.language
            elif isinstance(response, dict):
                transcribed_text = response.get('text', '')
                detected_language = response.get('language', None)
            else:
                # Fallback to regular transcription without language detection
                result = self.speech_to_text(audio_path, detect_language=False)
                transcribed_text = result["text"]
                detected_language = None
                
            return {
                "text": transcribed_text,
                "language": detected_language
            }
            
        except Exception as e:
            logger.error(f"Error in detect_and_process_speech: {str(e)}")
            return {
                "text": "",
                "language": None
            }

    def set_model(self, model_name: str) -> bool:
        """
        Set the model for transcription
        
        Args:
            model_name: Name of the model to use
            
        Returns:
            bool: True if successful
        """
        self.model = model_name
        logger.info(f"Model set to {self.model}")
        return True


if __name__ == "__main__":
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        import sys
        sys.exit(1)
        
    stt = SpeechToText(api_key)
    
    # Test recording and transcription with language detection
    output_path = "test_recording.wav"
    print("Recording 5 seconds of audio...")
    stt.record_audio(output_path, 5)
    
    print("Transcribing audio with language detection...")
    result = stt.detect_and_process_speech(output_path)
    print(f"Transcription: {result['text']}")
    print(f"Detected language: {result['language']}")