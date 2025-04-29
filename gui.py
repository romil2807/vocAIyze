import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from llm import LLM
from tts import TextToSpeech
from stt import SpeechToText
import os
from dotenv import load_dotenv
import threading
from pathlib import Path
import time
import queue

# Load environment variables at the start
load_dotenv()

#Create a queue for thread-safe communication
update_queue = queue.Queue()

class ConversationBuffer:
    def __init__(self, max_turns=5, max_tokens=2000):
        self.buffer = []
        self.max_turns = max_turns
        self.max_tokens = max_tokens
        self.token_count = 0
    
    def add_message(self, speaker, text, language):
        """Add a message to the conversation buffer"""
        message = {
            "speaker": speaker,
            "text": text,
            "language": language,
            "timestamp": time.time()
        }
        
        # Approximate token count (rough estimate)
        message_tokens = len(text.split()) + 5
        
        self.buffer.append(message)
        self.token_count += message_tokens
        
        # Trim buffer if needed
        self._trim_buffer()
    
    def _trim_buffer(self):
        """Remove oldest messages if buffer exceeds limits"""
        # First try to limit by number of turns
        while len(self.buffer) > self.max_turns:
            removed = self.buffer.pop(0)
            self.token_count -= (len(removed["text"].split()) + 5)
            
        # Then check token limit
        while self.token_count > self.max_tokens and len(self.buffer) > 1:
            removed = self.buffer.pop(0)
            self.token_count -= (len(removed["text"].split()) + 5)
    
    def get_context_for_llm(self):
        """Format buffer contents for LLM prompt"""
        formatted_context = []
        for msg in self.buffer:
            speaker_label = "User" if msg["speaker"] == 1 else "Other Speaker"
            formatted_context.append(f"{speaker_label} ({msg['language']}): {msg['text']}")
        
        return "\n".join(formatted_context)
    
    def clear(self):
        """Clear the conversation buffer"""
        self.buffer = []
        self.token_count = 0

class ConversationController:
    def __init__(self, tts_engine):
        self.paused = False
        self.last_response = None
        self.tts_engine = tts_engine
        
    def pause_conversation(self):
        """Pause the ongoing conversation"""
        self.paused = True
        # Stop any ongoing TTS
        # Note: This would require modification to the TTS class to support stopping
    
    def resume_conversation(self):
        """Resume paused conversation"""
        self.paused = False
    
    def repeat_last_response(self):
        """Repeat the last response"""
        if self.last_response:
            self.tts_engine.text_to_speech(self.last_response["text"])
    
    def modify_response_before_speaking(self, text, language, root):
        """Allow modifying response before TTS"""
        # Show dialog for editing text before speaking
        dialog = tk.Toplevel(root)
        dialog.title("Edit Response Before Speaking")
        
        text_widget = tk.Text(dialog, height=10, width=50)
        text_widget.insert("1.0", text)
        text_widget.pack(padx=10, pady=10)
        
        result = [text]  # Use list for closure modification
        
        def on_confirm():
            result[0] = text_widget.get("1.0", "end-1c")
            dialog.destroy()
            
        confirm_button = tk.Button(dialog, text="Confirm", command=on_confirm)
        confirm_button.pack(pady=5)
        
        # Wait for dialog to close
        dialog.transient(root)  # Make dialog modal
        dialog.grab_set()
        root.wait_window(dialog)
        
        return result[0]

class VocAIyzeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("vocAIyze - Voice AI Assistant")
        self.root.geometry("800x600")  # Increased size for better UI

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
            self.conversation_buffer = ConversationBuffer()
            self.conversation_controller = ConversationController(self.tts)
            
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

        # Notebook for tabbed interface
        self.tab_control = ttk.Notebook(self.root)
        
        # Tab 1: Pre-Call Preparation
        self.pre_call_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.pre_call_tab, text="Pre-Call Preparation")
        self.create_pre_call_tab()
        
        # Tab 2: Two-Way Conversation
        self.two_way_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.two_way_tab, text="Two-Way Conversation")
        self.create_two_way_tab()
        
        self.tab_control.pack(expand=1, fill="both", padx=10, pady=10)

        # Status bar at bottom
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_pre_call_tab(self):
        # Frame for inputs
        input_frame = ttk.Frame(self.pre_call_tab)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Goal input
        ttk.Label(input_frame, text="Enter the goal of your call:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.goal_entry = ttk.Entry(input_frame, width=50)
        self.goal_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Language input
        ttk.Label(input_frame, text="Language:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.pre_call_language = ttk.Entry(input_frame, width=50)
        self.pre_call_language.insert(0, "English")
        self.pre_call_language.grid(row=1, column=1, padx=5, pady=5)
        
        # Generate button
        generate_button = ttk.Button(input_frame, text="Generate Script", 
                                     command=self.generate_pre_call_script)
        generate_button.grid(row=2, column=1, sticky=tk.E, pady=10)
        
        # Result area
        ttk.Label(self.pre_call_tab, text="Generated Script:").pack(anchor=tk.W, padx=10, pady=5)
        self.pre_call_result = scrolledtext.ScrolledText(self.pre_call_tab, wrap=tk.WORD, width=70, height=15)
        self.pre_call_result.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def create_two_way_tab(self):
        # Frame for language settings
        settings_frame = ttk.Frame(self.two_way_tab)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # User language
        ttk.Label(settings_frame, text="Your Language:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.user_language = ttk.Entry(settings_frame, width=20)
        self.user_language.insert(0, "English")
        self.user_language.grid(row=0, column=1, padx=5, pady=5)
        
        # Other speaker language
        ttk.Label(settings_frame, text="Other Speaker's Language:").grid(row=0, column=2, sticky=tk.W, pady=5)
        self.other_language = ttk.Entry(settings_frame, width=20)
        self.other_language.insert(0, "Spanish")
        self.other_language.grid(row=0, column=3, padx=5, pady=5)
        
        # Auto-detect checkbox
        self.auto_detect_var = tk.BooleanVar(value=True)
        auto_detect_cb = ttk.Checkbutton(settings_frame, text="Auto-detect languages", 
                                        variable=self.auto_detect_var)
        auto_detect_cb.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Voice selection
        ttk.Label(settings_frame, text="TTS Voice:").grid(row=1, column=2, sticky=tk.W, pady=5)
        self.voice_var = tk.StringVar(value="alloy")
        voice_combo = ttk.Combobox(settings_frame, textvariable=self.voice_var, 
                                  values=self.tts.get_available_voices())
        voice_combo.grid(row=1, column=3, padx=5, pady=5)
        
        # Conversation area
        ttk.Label(self.two_way_tab, text="Conversation:").pack(anchor=tk.W, padx=10, pady=5)
        self.conversation_text = scrolledtext.ScrolledText(self.two_way_tab, wrap=tk.WORD, width=70, height=10)
        self.conversation_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Current speaker indicator
        speaker_frame = ttk.Frame(self.two_way_tab)
        speaker_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(speaker_frame, text="Current Speaker:").pack(side=tk.LEFT, padx=5)
        self.speaker_var = tk.StringVar(value="You")
        self.speaker_label = ttk.Label(speaker_frame, textvariable=self.speaker_var, font=("Arial", 10, "bold"))
        self.speaker_label.pack(side=tk.LEFT, padx=5)
        
        # Translation preview
        ttk.Label(self.two_way_tab, text="Translation:").pack(anchor=tk.W, padx=10, pady=5)
        self.translation_text = scrolledtext.ScrolledText(self.two_way_tab, wrap=tk.WORD, width=70, height=3)
        self.translation_text.pack(fill=tk.X, padx=10, pady=5)
        
        # Control buttons
        control_frame = ttk.Frame(self.two_way_tab)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Start button
        self.start_button = ttk.Button(control_frame, text="Start Conversation", 
                                     command=self.start_two_way_conversation)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Toggle speaker button
        self.toggle_button = ttk.Button(control_frame, text="Switch Speaker", 
                                      command=self.toggle_speaker, state=tk.DISABLED)
        self.toggle_button.pack(side=tk.LEFT, padx=5)
        
        # Pause/resume button
        self.pause_var = tk.BooleanVar(value=False)
        self.pause_button = ttk.Button(control_frame, text="Pause", 
                                     command=self.toggle_pause, state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        # Repeat button
        self.repeat_button = ttk.Button(control_frame, text="Repeat Last", 
                                      command=self.repeat_last, state=tk.DISABLED)
        self.repeat_button.pack(side=tk.LEFT, padx=5)
        
        # Edit button
        self.edit_button = ttk.Button(control_frame, text="Edit Before Speaking", 
                                    command=self.edit_response, state=tk.DISABLED)
        self.edit_button.pack(side=tk.LEFT, padx=5)
        
        # Visual audio indicator
        ttk.Label(self.two_way_tab, text="Audio Level:").pack(anchor=tk.W, padx=10, pady=5)
        self.audio_indicator = ttk.Progressbar(self.two_way_tab, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.audio_indicator.pack(fill=tk.X, padx=10, pady=5)

    def generate_pre_call_script(self):
        goal = self.goal_entry.get()
        language = self.pre_call_language.get() or "English"
        if not goal:
            messagebox.showwarning("Input Error", "Please enter the goal of your call.")
            return
        
        self.status_var.set("Generating script...")
        self.root.update()
        
        try:
            script = self.llm.generate_call_script(goal, language)
            self.pre_call_result.delete(1.0, tk.END)
            self.pre_call_result.insert(tk.END, script)
            self.status_var.set("Script generated")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate script: {str(e)}")
            self.status_var.set("Error occurred")

    def start_two_way_conversation(self):
        # Reset conversation state
        self.conversation_buffer.clear()
        self.conversation_text.delete(1.0, tk.END)
        self.translation_text.delete(1.0, tk.END)
        
        # Set initial state
        self.current_speaker = 1  # 1 = User, 2 = Other Speaker
        self.speaker_var.set("You")
        self.conversation_active = True
        
        # Update UI state
        self.toggle_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.NORMAL)
        self.repeat_button.config(state=tk.NORMAL)
        self.edit_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.DISABLED)
        
        # Initial message
        self.conversation_text.insert(tk.END, "--- Conversation Started ---\n")
        
        # Begin listening
        self.listen_for_speech()

    def listen_for_speech(self):
        """Record speech from current speaker and process it"""
        if not hasattr(self, 'conversation_active') or not self.conversation_active:
            return
            
        if self.conversation_controller.paused:
            # If paused, check again in a second
            self.root.after(1000, self.listen_for_speech)
            return
            
        # Update status
        if self.current_speaker == 1:
            self.status_var.set("Listening to you... (speak now)")
            source_lang = self.user_language.get()
            target_lang = self.other_language.get()
        else:
            self.status_var.set("Listening to other speaker... (speak now)")
            source_lang = self.other_language.get()
            target_lang = self.user_language.get()
            
        self.root.update()
        
        # Start recording in a separate thread
        threading.Thread(target=self.record_and_process_speech, 
                         args=(source_lang, target_lang)).start()

    def record_and_process_speech(self, source_lang, target_lang):
        try:
            # Record audio
            audio_path = str(Path(__file__).parent.absolute() / "user_input.wav")
            self.stt.record_audio(audio_path, duration=7)
            
            # Simulate audio level indicator (would need actual audio level detection)
            for i in range(10):
                if not hasattr(self, 'conversation_active') or not self.conversation_active:
                    return
                level = min(100, i * 10 + (i % 3) * 5)  # Random fluctuation
                self.audio_indicator['value'] = level
                self.root.update()
                time.sleep(0.1)
            self.audio_indicator['value'] = 0
            
            # Update status
            self.status_var.set("Processing speech...")
            self.root.update()
            
            # Transcribe audio
            if self.auto_detect_var.get():
                result = self.stt.speech_to_text(audio_path)
                if isinstance(result, dict) and "text" in result:
                    transcribed_text = result["text"]
                else:
                    transcribed_text = str(result)
                detected_lang = source_lang
            else:
                result = self.stt.speech_to_text(audio_path)
                if isinstance(result, dict) and "text" in result:
                    transcribed_text = result["text"]
                else:
                    transcribed_text = str(result)
                detected_lang = source_lang
                
            if not transcribed_text or transcribed_text.strip() == "":
                self.status_var.set("No speech detected. Try again.")
                self.root.update()
                self.root.after(1000, self.listen_for_speech)
                return
                
            # Display transcribed text
            speaker_name = "You" if self.current_speaker == 1 else "Other Speaker"
            self.conversation_text.insert(tk.END, f"{speaker_name} ({detected_lang}): {transcribed_text}\n")
            self.conversation_text.see(tk.END)
            
            # Add to conversation buffer
            self.conversation_buffer.add_message(self.current_speaker, transcribed_text, detected_lang)
            
            # Translate if languages are different
            if source_lang.lower() != target_lang.lower():
                self.status_var.set(f"Translating to {target_lang}...")
                self.root.update()
                
                translated_text = self.llm.translate_text(transcribed_text, target_lang)
                
                # Show translation
                self.translation_text.delete(1.0, tk.END)
                self.translation_text.insert(tk.END, translated_text)
                
                # Display in conversation
                translation_prefix = "Translation"
                self.conversation_text.insert(tk.END, f"{translation_prefix}: {translated_text}\n")
                self.conversation_text.see(tk.END)
                
                # Store for potential modification
                self.current_translation = translated_text
                
                # Enable edit button
                self.edit_button.config(state=tk.NORMAL)
                
                # Speak the translation
                self.status_var.set("Speaking translation...")
                self.root.update()
                
                # Set voice based on selection
                self.tts.set_voice(self.voice_var.get())
                
                # Store as last response for repeat functionality
                self.conversation_controller.last_response = {
                    "text": translated_text,
                    "language": target_lang
                }
                
                # Speak translation
                self.tts.text_to_speech(translated_text)
            else:
                # Clear translation box if languages are the same
                self.translation_text.delete(1.0, tk.END)
                self.translation_text.insert(tk.END, "(Same language - no translation needed)")
            
            # Reset status
            self.status_var.set("Ready")
            
            # Continue listening
            self.root.after(1000, self.listen_for_speech)
            
        except Exception as e:
            self.conversation_text.insert(tk.END, f"Error: {str(e)}\n")
            self.status_var.set("Error occurred")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
            # Try to continue despite the error
            self.root.after(2000, self.listen_for_speech)

    def toggle_speaker(self):
        """Switch between speakers"""
        self.current_speaker = 3 - self.current_speaker  # Toggle between 1 and 2
        
        if self.current_speaker == 1:
            self.speaker_var.set("You")
        else:
            self.speaker_var.set("Other Speaker")
            
        # Update conversation display
        self.conversation_text.insert(tk.END, f"--- Switched to {self.speaker_var.get()} ---\n")
        self.conversation_text.see(tk.END)
        
        # Clear translation preview
        self.translation_text.delete(1.0, tk.END)

    def toggle_pause(self):
        """Pause or resume conversation"""
        if not hasattr(self, 'conversation_active') or not self.conversation_active:
            return
            
        self.conversation_controller.paused = not self.conversation_controller.paused
        
        if self.conversation_controller.paused:
            self.pause_button.config(text="Resume")
            self.status_var.set("Conversation paused")
            self.conversation_text.insert(tk.END, "--- Conversation Paused ---\n")
        else:
            self.pause_button.config(text="Pause")
            self.status_var.set("Conversation resumed")
            self.conversation_text.insert(tk.END, "--- Conversation Resumed ---\n")
            # Continue listening
            self.listen_for_speech()
            
        self.conversation_text.see(tk.END)

    def repeat_last(self):
        """Repeat the last spoken response"""
        if hasattr(self.conversation_controller, 'last_response') and self.conversation_controller.last_response:
            self.status_var.set("Repeating last response...")
            self.conversation_text.insert(tk.END, "--- Repeating Last Translation ---\n")
            self.conversation_text.see(tk.END)
            
            self.conversation_controller.repeat_last_response()
            
            self.status_var.set("Ready")
        else:
            messagebox.showinfo("Information", "No previous response to repeat.")

    def edit_response(self):
        """Edit the current translation before speaking it"""
        if hasattr(self, 'current_translation') and self.current_translation:
            # Get the target language
            if self.current_speaker == 1:
                target_lang = self.other_language.get()
            else:
                target_lang = self.user_language.get()
                
            edited_text = self.conversation_controller.modify_response_before_speaking(
                self.current_translation, target_lang, self.root)
                
            if edited_text != self.current_translation:
                # Update display
                self.translation_text.delete(1.0, tk.END)
                self.translation_text.insert(tk.END, edited_text)
                
                self.conversation_text.insert(tk.END, f"Edited Translation: {edited_text}\n")
                self.conversation_text.see(tk.END)
                
                # Update stored response
                self.conversation_controller.last_response = {
                    "text": edited_text,
                    "language": target_lang
                }
                
                # Speak edited translation
                self.status_var.set("Speaking edited translation...")
                self.root.update()
                self.tts.text_to_speech(edited_text)
                self.status_var.set("Ready")
        else:
            messagebox.showinfo("Information", "No current translation to edit.")

if __name__ == "__main__":
    root = tk.Tk()
    app = VocAIyzeApp(root)
    root.mainloop()