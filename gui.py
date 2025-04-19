import tkinter as tk
from tkinter import messagebox, scrolledtext
from llm import LLM
from tts import TextToSpeech
from stt import SpeechToText
import os
from dotenv import load_dotenv
import threading
from pathlib import Path


# Load environment variables at the start
load_dotenv()

class VocAIyzeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("vocAIyze - Voice AI Assistant")
        self.root.geometry("600x400")

        # Initialize components with proper error handling
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            messagebox.showerror("Error", "OPENAI_API_KEY not found in .env file")
            self.root.destroy()
            return
        
        try:
            self.llm = LLM(api_key)
            self.tts = TextToSpeech(api_key)
            self.stt = SpeechToText(api_key)
            
            # Create UI elements
            self.create_widgets()
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize components: {str(e)}")
            self.root.destroy()
            return

    def create_widgets(self):
        # Title Label
        title_label = tk.Label(self.root, text="vocAIyze - Voice AI Assistant", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Buttons for features
        pre_call_button = tk.Button(self.root, text="Pre-Call Preparation", command=self.pre_call_preparation, width=25)
        pre_call_button.pack(pady=10)

        real_time_button = tk.Button(self.root, text="Real-Time Call Assistance", command=self.real_time_call_assistance, width=25)
        real_time_button.pack(pady=10)

        # Exit Button
        exit_button = tk.Button(self.root, text="Exit", command=self.root.quit, width=25, bg="red", fg="white")
        exit_button.pack(pady=10)

    def pre_call_preparation(self):
        # Create a new window for Pre-Call Preparation
        pre_call_window = tk.Toplevel(self.root)
        pre_call_window.title("Pre-Call Preparation")
        pre_call_window.geometry("500x400")

        tk.Label(pre_call_window, text="Enter the goal of your call:", font=("Arial", 12)).pack(pady=5)
        goal_entry = tk.Entry(pre_call_window, width=50)
        goal_entry.pack(pady=5)

        tk.Label(pre_call_window, text="Enter the language for the script (default: English):", font=("Arial", 12)).pack(pady=5)
        language_entry = tk.Entry(pre_call_window, width=50)
        language_entry.insert(0, "English")
        language_entry.pack(pady=5)

        result_text = scrolledtext.ScrolledText(pre_call_window, wrap=tk.WORD, width=60, height=10)
        result_text.pack(pady=10)

        def generate_script():
            goal = goal_entry.get()
            language = language_entry.get() or "English"
            if not goal:
                messagebox.showwarning("Input Error", "Please enter the goal of your call.")
                return

            script = self.llm.generate_call_script(goal, language)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, script)

        generate_button = tk.Button(pre_call_window, text="Generate Script", command=generate_script)
        generate_button.pack(pady=5)

    def real_time_call_assistance(self):
        # Create a new window for Real-Time Call Assistance
        real_time_window = tk.Toplevel(self.root)
        real_time_window.title("Real-Time Call Assistance")
        real_time_window.geometry("500x300")

        tk.Label(real_time_window, text="Enter the target language for the call (default: English):", font=("Arial", 12)).pack(pady=5)
        language_entry = tk.Entry(real_time_window, width=50)
        language_entry.insert(0, "English")
        language_entry.pack(pady=5)

        conversation_text = scrolledtext.ScrolledText(real_time_window, wrap=tk.WORD, width=60, height=10)
        conversation_text.pack(pady=10)

        # Add a status label
        status_label = tk.Label(real_time_window, text="Ready", font=("Arial", 10))
        status_label.pack(pady=5)

        # Add a button to start assistance
        start_button = tk.Button(real_time_window, text="Start Assistance", command=lambda: self.start_assistance(language_entry, conversation_text, status_label))
        start_button.pack(pady=10)

    def start_assistance(self, language_entry, conversation_text, status_label):
        target_language = language_entry.get() or "English"
        conversation_text.insert(tk.END, "Starting real-time call assistance...\n")
        conversation_history = []

        def record_and_respond():
            try:
                # Step 1: Record the user's speech
                status_label.config(text="Recording... (speak now)")
                conversation_text.update()
                print("Recording audio...")
                audio_path = str(Path(__file__).parent.absolute() / "user_input.wav")
                self.stt.record_audio(audio_path, duration=7)
                print(f"Audio recorded: {audio_path}")

                # Step 2: Transcribe the speech to text
                status_label.config(text="Processing...")
                conversation_text.update()
                print("Transcribing audio...")
                user_input = self.stt.speech_to_text(audio_path)
                print(f"Transcription: {user_input}")
                conversation_text.insert(tk.END, f"You: {user_input}\n")

                # Step 3: Translate the user's input if needed
                if target_language.lower() != "english":
                    print(f"Translating input to English...")
                    user_input = self.llm.generate(f"Translate this to English: {user_input}")
                    print(f"Translated input: {user_input}")

                # Step 4: Add to conversation history
                conversation_history.append({"role": "user", "content": user_input})

                # Step 5: Generate a response
                print("Generating response...")
                prompt = "\n".join([f"{'User' if item['role'] == 'user' else 'Assistant'}: {item['content']}" 
                                    for item in conversation_history])
                response = self.llm.generate(prompt)
                print(f"Generated response: {response}")

                # Step 6: Translate the response back to the target language if needed
                if target_language.lower() != "english":
                    print(f"Translating response to {target_language}...")
                    response = self.llm.generate(f"Translate this to {target_language}: {response}")
                    print(f"Translated response: {response}")

                # Step 7: Display the response
                conversation_text.insert(tk.END, f"Assistant: {response}\n")
                conversation_text.see(tk.END)  # Scroll to bottom

                # Step 8: Add the response to conversation history
                conversation_history.append({"role": "assistant", "content": response})

                # Step 9: Play the response
                print("Playing response...")
                self.tts.text_to_speech(response)

                # Update status
                status_label.config(text="Ready")
            except Exception as e:
                conversation_text.insert(tk.END, f"Error: {str(e)}\n")
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
                status_label.config(text="Error occurred")
                print(f"Error: {str(e)}")

        # Run the recording and response generation in a separate thread
        threading.Thread(target=record_and_respond).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = VocAIyzeApp(root)
    root.mainloop()