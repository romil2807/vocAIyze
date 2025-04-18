import unittest
import os
from unittest.mock import patch, MagicMock, mock_open
from llm import LLM
from tts import TextToSpeech
from stt import SpeechToText

class TestLLM(unittest.TestCase):

    @patch('openai.OpenAI')
    def test_generate_method(self, mock_openai):
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Test response"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test
        llm = LLM("fake_api_key")
        result = llm.generate("Test prompt")
        
        # Assert
        self.assertEqual(result, "Test response")
        mock_client.chat.completions.create.assert_called_once()

    @patch('openai.OpenAI')
    @patch('json.load')
    @patch('builtins.open', new_callable=mock_open, read_data='{"test": "data"}')
    def test_load_knowledge_base(self, mock_file, mock_json_load, mock_openai):
        # Setup
        mock_json_load.return_value = {"test": "knowledge"}
        
        # Test
        with patch('os.path.exists', return_value=True):
            llm = LLM("fake_api_key")
            result = llm.knowledge_base
        
        # Assert
        self.assertEqual(result, {"test": "knowledge"})

class TestTextToSpeech(unittest.TestCase):

    @patch('openai.OpenAI')
    @patch('pydub.AudioSegment.from_file')
    @patch('pydub.playback.play')
    def test_text_to_speech(self, mock_play, mock_audio_segment, mock_openai):
        # Setup
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_client.audio.speech.create.return_value = mock_response
        
        # Test
        with patch('os.makedirs'):
            with patch.object(mock_response, 'stream_to_file') as mock_stream:
                tts = TextToSpeech("fake_api_key")
                tts.text_to_speech("Test text")
                
                # Assert
                mock_client.audio.speech.create.assert_called_once()
                mock_stream.assert_called_once()

    def test_set_voice(self):
        with patch('openai.OpenAI'):
            tts = TextToSpeech("fake_api_key")
            
            # Test valid voice
            result = tts.set_voice("nova")
            self.assertTrue(result)
            self.assertEqual(tts.current_voice, "nova")
            
            # Test invalid voice
            result = tts.set_voice("invalid_voice")
            self.assertFalse(result)
            self.assertEqual(tts.current_voice, "nova")  # Should not change

class TestSpeechToText(unittest.TestCase):

    @patch('openai.OpenAI')
    def test_speech_to_text(self, mock_openai):
        # Setup
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.text = "Transcribed text"
        mock_client.audio.transcriptions.create.return_value = mock_response
        
        # Test
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                stt = SpeechToText("fake_api_key")
                result = stt.speech_to_text("test.mp3")
                
                # Assert
                self.assertEqual(result, "Transcribed text")
                mock_client.audio.transcriptions.create.assert_called_once()

    @patch('openai.OpenAI')
    @patch('pyaudio.PyAudio')
    @patch('wave.open')
    def test_record_audio(self, mock_wave, mock_pyaudio, mock_openai):
        # Setup
        mock_py_instance = MagicMock()
        mock_pyaudio.return_value = mock_py_instance
        
        mock_stream = MagicMock()
        mock_py_instance.open.return_value = mock_stream
        mock_stream.read.return_value = b'audio data'
        
        mock_wave_instance = MagicMock()
        mock_wave.return_value = mock_wave_instance
        
        # Test
        with patch('os.path.exists', return_value=True):
            with patch('os.makedirs'):
                stt = SpeechToText("fake_api_key")
                result = stt.record_audio("test.wav", 1)
                
                # Assert
                self.assertEqual(result, "test.wav")
                mock_py_instance.open.assert_called_once()
                mock_wave_instance.writeframes.assert_called_once()

if __name__ == "__main__":
    unittest.main()