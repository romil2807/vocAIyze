import os
from openai import OpenAI
from llm import LLM
from tts import TextToSpeech
from stt import SpeechToText
from pathlib import Path
import logging
import argparse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("vocAIyze.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("vocAIyze")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="vocAIyze - Voice-based AI Assistant")
    parser.add_argument("--mode", choices=["interactive", "file"], default="interactive",
                        help="Run in interactive mode or process from file")
    parser.add_argument("--input", help="Input file path (for file mode)")
    parser.add_argument("--output", help="Output file path (for file mode)")
    args = parser.parse_args()

    # Fetch the API key from an environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        raise ValueError("OPENAI_API_KEY environment variable not set")

    # Initialize components
    llm = LLM(api_key)
    tts = TextToSpeech(api_key)
    stt = SpeechToText(api_key)
    
    # File mode
    if args.mode == "file":
        process_file_mode(llm, tts, stt, args.input, args.output)
    # Interactive mode
    else:
        run_interactive_mode(llm, tts, stt)

def process_file_mode(llm, tts, stt, input_path, output_path):
    """Process input from a file and save results to output file"""
    try:
        logger.info(f"Processing file: {input_path}")
        
        if input_path.endswith('.txt'):
            # Text input: generate response and convert to speech
            with open(input_path, 'r') as file:
                text_input = file.read()
            
            generated_text = llm.generate(text_input)
            logger.info("Text generated successfully")
            
            output_audio = output_path or f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
            tts.text_to_speech(generated_text, output_audio)
            logger.info(f"Audio saved to {output_audio}")
            
        elif input_path.endswith(('.mp3', '.wav')):
            # Audio input: transcribe and process
            transcribed_text = stt.speech_to_text(input_path)
            logger.info("Audio transcribed successfully")
            
            response = llm.generate(transcribed_text)
            logger.info("Response generated")
            
            output_file = output_path or f"response_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Save text response
            with open(f"{output_file}.txt", 'w') as file:
                file.write(response)
                
            # Generate audio response
            tts.text_to_speech(response, f"{output_file}.mp3")
            logger.info(f"Response saved to {output_file}.txt and {output_file}.mp3")
    
    except Exception as e:
        logger.error(f"Error in file processing: {str(e)}")
        raise

def run_interactive_mode(llm, tts, stt):
    """Run an interactive conversation session"""
    logger.info("Starting interactive mode")
    
    # Greeting
    greeting = "Hello, I'm vocAIyze. How can I assist you today?"
    print(greeting)
    tts.text_to_speech(greeting)
    
    conversation_history = []
    
    try:
        while True:
            # Record user input
            print("\nListening... (speak now)")
            audio_path = Path("./user_input.wav")
            stt.record_audio(str(audio_path), duration=7)
            
            # Convert speech to text
            user_input = stt.speech_to_text(str(audio_path))
            print(f"You: {user_input}")
            
            if user_input.lower() in ["exit", "quit", "goodbye", "bye"]:
                farewell = "Thank you for using vocAIyze. Goodbye!"
                print(f"Assistant: {farewell}")
                tts.text_to_speech(farewell)
                break
            
            # Add to conversation history and generate response
            conversation_history.append({"role": "user", "content": user_input})
            
            # Generate context-aware response
            prompt = "\n".join([f"{'User' if item['role'] == 'user' else 'Assistant'}: {item['content']}" 
                               for item in conversation_history])
            response = llm.generate(prompt)
            
            print(f"Assistant: {response}")
            tts.text_to_speech(response)
            
            # Add response to history
            conversation_history.append({"role": "assistant", "content": response})
            
            # Keep conversation history manageable
            if len(conversation_history) > 10:
                conversation_history = conversation_history[-10:]
                
    except KeyboardInterrupt:
        print("\nExiting vocAIyze...")
    except Exception as e:
        logger.error(f"Error in interactive mode: {str(e)}")
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()