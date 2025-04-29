# vocAIyze: Real-Time AI-Powered Multilingual Communication Assistant

vocAIyze is a voice-powered AI assistant designed to break down language barriers by providing real-time translation and conversation assistance. It helps users prepare for conversations in foreign languages and facilitates live communication between speakers of different languages.

![vocAIyze Logo](https://via.placeholder.com/150?text=vocAIyze)

## Features

### Pre-Call Preparation
- Generate professional conversation scripts based on your goals
- Support for multiple languages
- Contextually appropriate opening lines, talking points, and closing remarks

### Real-Time Two-Way Conversation
- Live speech recognition and translation
- Support for conversations between speakers of different languages
- Seamless speaker switching
- Language auto-detection capabilities

### Intelligent Controls
- Pause and resume conversations
- Repeat last translation
- Edit translations before they're spoken
- Visual audio level indicators

### Natural Voice Output
- High-quality text-to-speech in multiple voices
- Voice customization options
- Context-aware voice selection based on conversation tone

## System Architecture

vocAIyze is built with a modular architecture consisting of:

- **Speech-to-Text (STT)**: Converts spoken language to text using OpenAI's Whisper API
- **Language Model (LLM)**: Processes and translates text using OpenAI's GPT models
- **Text-to-Speech (TTS)**: Converts translated text back to speech using OpenAI's TTS API
- **GUI**: User-friendly interface built with Tkinter

## Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key
- Working microphone and speakers

### Setup
1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/vocAIyze.git
   cd vocAIyze
   ```

2. Install required packages
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your OpenAI API key
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

### Running the Application
```bash
python gui.py
```

### Pre-Call Preparation
1. Select "Pre-Call Preparation" from the main menu
2. Enter your call goal and target language
3. Click "Generate Script"
4. Review and practice the generated script

### Two-Way Conversation
1. Select "Two-Way Conversation" from the tabbed interface
2. Set your language and the other speaker's language
3. Click "Start Conversation"
4. Speak when prompted and listen to the translations
5. Use "Switch Speaker" when the other person wants to talk
6. Use control buttons to manage the conversation flow

## Project Structure

```
VocalAIze/
├── .env                     # Environment variables (API keys, defaults)
├── .gitignore               # Git ignore file
├── gui.py                   # Main GUI application
├── llm.py                   # Language model interactions
├── stt.py                   # Speech-to-text functionality
├── tts.py                   # Text-to-speech functionality
├── knowledge_base.json      # Knowledge base for contextual responses
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

## Dependencies

- **openai**: For GPT, Whisper, and TTS APIs
- **pyaudio**: For recording audio
- **pydub**: For audio processing and playback
- **python-dotenv**: For managing environment variables
- **tkinter**: For building the GUI
- **numpy**: For audio signal processing

## Future Enhancements

- Mobile application support
- Multiple speaker tracking for group conversations
- Specialized domain knowledge (medical, technical, business)
- Offline mode for basic functionality without internet
- Conversation history export and analysis

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for their powerful API services
- The open-source community for inspiration and tools
- All contributors and testers who helped improve the application

---

Created by [Your Name]