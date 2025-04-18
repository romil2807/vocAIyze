import os 
from openai import OpenAI
from tts import TextToSpeech
from stt import SpeechToText
from pathlib import Path

# api_key

client = OpenAI(api_key=api_key)


def get_assistant_response(messages: list[dict[str, str]]) -> str:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content


if __name__ == '__main__':
    system_message = {"role": "system", 
                      "content": "You are a helpful assistant."} # words not to use at any cost, sorry cannot help with this

    assistant_initial_text = "Hello, how can I help you today?"
    print(assistant_initial_text) 

    tts = TextToSpeech(api_key)
    tts.text_to_speech(assistant_initial_text)

    assistant_initial_message = {"role": "assistant",
                                 "content": assistant_initial_text}
    
    stt = SpeechToText(api_key)

    while True:
        audio_path = "my_speech.wav"
        stt.record_audio(audio_path, duration=7)

        user_input: str = stt.speech_to_text(audio_path)

        user_message = {"role": "user",
                        "content": user_input}

        messages = [
            system_message,
            assistant_initial_message,
            user_message
        ]

        response = get_assistant_response(messages)
        print(f"Assistant response: {response}")

        messages.append({"role": "assistant", "content": response})
        tts.text_to_speech(response)