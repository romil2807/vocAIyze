import pyaudio
import wave
import os
from openai import OpenAI
import logging
from pathlib import Path
import tempfile

logger = logging.getLogger("VocalAIze.STT")

class SpeechToText:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
        self.default_duration = 5
        self.model = "whisper-1"  # Default model
        logger.info("SpeechToText initialized")

    def record_audio(self, output_path: str, duration: int = None):
        """
        Record audio from the microphone
        
        Args:
            output_path: Path to save the recorded audio
            duration: Recording duration in seconds (default: self.default_duration)
        """
        if duration is None:
            duration = self.default_duration
            
        chunk = 1024  # Record in chunks of 1024 samples
        sample_format = pyaudio.paInt16  # 16 bits per sample
        channels = 1
        fs = 44100  # Record at 44100 samples per second

        try:
            p = pyaudio.PyAudio()  # Create an interface to PortAudio

            logger.info(f"Recording for {duration} seconds...")
            print('Recording...')

            stream = p.open(format=sample_format,
                            channels=channels,
                            rate=fs,
                            frames_per_buffer=chunk,
                            input=True)

            frames = []  # Initialize array to store frames

            # Store data in chunks for the specified duration
            for _ in range(0, int(fs / chunk * duration)):
                data = stream.read(chunk)
                frames.append(data)

            # Stop and close the stream
            stream.stop_stream()
            stream.close()
            # Terminate the PortAudio interface
            p.terminate()

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
            return output_path
            
        except Exception as e:
            logger.error(f"Error in record_audio: {str(e)}")
            raise

    def speech_to_text(self, audio_path: str) -> str:
        """
        Convert speech audio to text using OpenAI's Whisper API
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Transcribed text
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
                    file=audio_file
                )
                
            logger.info("Transcription completed successfully")
            return response.text
            
        except Exception as e:
            logger.error(f"Error in speech_to_text: {str(e)}")
            raise

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
    
    # Test recording and transcription
    output_path = "test_recording.wav"
    print("Recording 5 seconds of audio...")
    stt.record_audio(output_path, 5)
    
    print("Transcribing audio...")
    transcription = stt.speech_to_text(output_path)
    print(f"Transcription: {transcription}")