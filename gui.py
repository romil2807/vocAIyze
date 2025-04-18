import tkinter as tk
from tkinter import messagebox, scrolledtext
from llm import LLM
from tts import TextToSpeech
from stt import SpeechToText
import os

class VocAIyzeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("vocAIyze - Voice AI Assistant")
        self.root.geometry("600x400")

        # Initialize components
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            messagebox.showerror("Error", "OPENAI_API_KEY environment variable not set")
            self.root.destroy()
            return

        self.llm = LLM(api_key)
        self.tts = TextToSpeech(api_key)
        self.stt = SpeechToText(api_key)

        # Create UI elements
        self.create_widgets()

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

        def start_assistance():
            target_language = language_entry.get() or "English"
            conversation_text.insert(tk.END, "Starting real-time call assistance...\n")
            conversation_text.insert(tk.END, "Press Ctrl+C in the terminal to stop.\n")

            try:
                conversation_history = []
                while True:
                    # Record the user's speech
                    audio_path = "./user_input.wav"
                    self.stt.record_audio(audio_path, duration=7)

                    # Transcribe the speech to text
                    user_input = self.stt.speech_to_text(audio_path)
                    conversation_text.insert(tk.END, f"You: {user_input}\n")

                    # Translate the user's input if needed
                    if target_language.lower() != "english":
                        user_input = self.llm.generate(f"Translate this to English: {user_input}")

                    # Add to conversation history
                    conversation_history.append({"role": "user", "content": user_input})

                    # Generate a response
                    prompt = "\n".join([f"{'User' if item['role'] == 'user' else 'Assistant'}: {item['content']}" 
                                        for item in conversation_history])
                    response = self.llm.generate(prompt)

                    # Translate the response back to the target language if needed
                    if target_language.lower() != "english":
                        response = self.llm.generate(f"Translate this to {target_language}: {response}")

                    conversation_text.insert(tk.END, f"Assistant: {response}\n")
                    self.tts.text_to_speech(response)

                    # Add the response to conversation history
                    conversation_history.append({"role": "assistant", "content": response})

                    # Keep the conversation history manageable
                    if len(conversation_history) > 10:
                        conversation_history = conversation_history[-10:]

            except KeyboardInterrupt:
                conversation_text.insert(tk.END, "\nExiting real-time call assistance...\n")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

        start_button = tk.Button(real_time_window, text="Start Assistance", command=start_assistance)
        start_button.pack(pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = VocAIyzeApp(root)
    root.mainloop()