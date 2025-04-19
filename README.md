# vocAIyze: Voice-Powered AI Assistant

vocAIyze is a comprehensive voice-to-voice AI assistant that leverages OpenAI's powerful APIs to enable natural voice interactions. It combines speech-to-text, large language models, and text-to-speech capabilities to create seamless conversational experiences.

## Features

- **Voice Input/Output**: Speak naturally to vocAIyze and hear AI-generated responses in high-quality voices
- **Advanced Language Processing**: Powered by OpenAI's language models for context-aware responses
- **Multi-Mode Operation**: Use in interactive conversation mode or batch process files
- **Business Assistant Capabilities**: 
  - Task identification and summarization
  - Detection of unrealistic promises or exaggerations
  - Knowledge base integration for domain-specific responses
  - CRM, email, and scheduling simulation (integration points)

## Requirements

- Python 3.8+ 
- OpenAI API key
- PortAudio (for PyAudio)
- ffmpeg (for audio processing)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/vocAIyze.git
   cd vocAIyze
   ```

2. **Create and activate a virtual environment** (recommended):
   ```bash
   python -m venv venv
   
   # On Windows:
   .\venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your OpenAI API key**:
   ```bash
   # On Windows:
   set OPENAI_API_KEY=your_api_key_here
   
   # On macOS/Linux:
   export OPENAI_API_KEY=your_api_key_here
   ```

## Usage

### Interactive Mode

Run vocAIyze in interactive conversation mode:

```bash
python main.py
```

This starts a conversation where you can:
- Speak to the assistant (it records your voice)
- Hear the assistant's response
- Continue the conversation naturally

To exit, say "exit", "quit", or "goodbye", or press Ctrl+C.

### File Processing Mode

Process text or audio files:

```bash
# Convert text file to speech
python main.py --mode file --input your_text.txt --output response.mp3

# Transcribe audio and get AI response as text and speech
python main.py --mode file --input recording.mp3 --output response
```

### Component Testing

Test individual components:

```bash
# Test text-to-speech
python tts.py

# Test speech-to-text
python stt.py
```

## Architecture

vocAIyze consists of three main components:

1. **Speech-to-Text (STT)**: Converts spoken language to text using OpenAI's Whisper model
2. **Language Model (LLM)**: Processes text input and generates appropriate responses using OpenAI's GPT models
3. **Text-to-Speech (TTS)**: Converts text responses back to spoken language using OpenAI's TTS models

## Customization

### Voices

vocAIyze supports multiple voices for text-to-speech:
- alloy (default)
- echo
- fable
- onyx
- nova
- shimmer

To change the voice in code:
```python
tts = TextToSpeech(api_key)
tts.set_voice("nova")
```

### Knowledge Base

You can customize the knowledge base by editing the `knowledge_base.json` file, which will be created automatically on first run with default values.

## API Integration

vocAIyze is designed to easily integrate with:
- CRM systems (through the `update_crm` method)
- Email services (through the `send_email` method)
- Calendar/scheduling systems (through the `schedule_follow_up` method)

## License

[MIT License](LICENSE)

## Contact

For questions or support, please contact [your-email@example.com](mailto:shahromil2807@gmail.com)
