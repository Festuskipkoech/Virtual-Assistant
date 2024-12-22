# Import necessary libraries
import datetime
import os
import sys
import time
import webbrowser
import pyautogui
import speech_recognition as sr
import json
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import psutil 
from gtts import gTTS

class VirtualAssistant:
    """
    A class representing a voice-controlled virtual assistant that can perform various tasks
    including speech recognition, text-to-speech conversion, and system monitoring.
    
    The class uses object-oriented programming to organize related functionality and maintain state:
    - Encapsulation: Keeps related data and methods together
    - Abstraction: Hides complex implementation details behind simple interfaces
    - State Management: Maintains loaded models and configuration across method calls
    """
    
    def __init__(self):
        """
        Initialize the Virtual Assistant by setting up required components.
        This constructor creates a single instance with all necessary resources.
        """
        # Initialize ML models and recognizer - these will persist throughout the object's lifetime
        self.load_models()
        self.recognizer = sr.Recognizer()
        
    def load_models(self):
        """
        Load all necessary ML models and data for natural language processing.
        Centralizes model loading and handles errors appropriately.
        
        Loads:
        - Intent classification model
        - Text tokenizer
        - Label encoder
        - Intent data
        """
        try:
            # Load conversation intents from JSON
            with open("intents.json") as file:
                self.data = json.load(file)
            # Load the trained neural network model
            self.model = load_model("chat_model.h5")
            # Load text tokenizer for processing input
            with open("tokenizer.pkl", "rb") as f:
                self.tokenizer = pickle.load(f)
            # Load label encoder for intent classification
            with open("label_encoder.pkl", "rb") as encoder_file:
                self.label_encoder = pickle.load(encoder_file)
        except FileNotFoundError as e:
            print(f"Error loading models: {e}")
            sys.exit(1)

    def speak(self, text, language='en'):
        """
        Convert text to speech and play it.
        
        Args:
            text (str): Text to be converted to speech
            language (str): Language code for speech synthesis (default: 'en')
        """
        try:
            # Create text-to-speech object
            tts = gTTS(text=text, lang=language)
            filename = "output.mp3"
            # Save and play the audio file
            tts.save(filename)
            os.system(f'mpg123 {filename}')
            # Clean up temporary file
            os.remove(filename)
        except Exception as e:
            print(f"Error in speech synthesis: {e}")
            
    def listen_command(self):
        """
        Listen for voice commands and convert them to text.
        
        Returns:
            str: Recognized text from speech, or 'None' if recognition fails
        """
        try:
            # Use microphone as audio source
            with sr.Microphone() as source:
                print("Listening...", end="", flush=True)
                # Adjust for background noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Listen for audio input
                audio = self.recognizer.listen(source, timeout=5)
                
            print("\rRecognizing...", end="", flush=True)
            # Convert speech to text
            query = self.recognizer.recognize_google(audio, language='en-us')
            print(f"\rUser said: {query}\n")
            return query.lower()
        except (sr.RequestError, sr.UnknownValueError, Exception) as e:
            print(f"Error in speech recognition: {e}")
            return "None"

    def get_day_and_time(self):
        """
        Get current day and time information.
        
        Returns:
            tuple: (day_name, hour)
        """
        current_time = datetime.datetime.now()
        day_dict = {
            1: "Monday", 2: "Tuesday", 3: "Wednesday",
            4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"
        }
        return day_dict[current_time.weekday() + 1], current_time.hour

    def greet(self):
        """Generate and speak an appropriate greeting based on time of day."""
        day, hour = self.get_day_and_time()
        time_str = time.strftime("%I:%M %p")
        
        # Determine appropriate greeting based on time
        if 0 <= hour < 12:
            greeting = "Good morning"
        elif 12 <= hour < 16:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
            
        self.speak(f"{greeting} Festus, it's {day} and the time is {time_str}")

    def check_system_condition(self):
        """Monitor and report system status including CPU and battery levels."""
        try:
            # Get system metrics
            cpu_usage = psutil.cpu_percent()
            battery = psutil.sensors_battery()
            
            if battery is None:
                self.speak("Unable to get battery information")
                return
                
            # Report system status
            self.speak(f"CPU is at {cpu_usage} percent")
            self.speak(f"Battery is at {battery.percent} percent")
            
            # Provide appropriate battery warnings
            if battery.percent >= 80:
                self.speak("Power level is good")
            elif 40 <= battery.percent < 80:
                self.speak("Consider connecting to power in 30 minutes")
            else:
                self.speak("Low power, please connect to power source")
        except Exception as e:
            print(f"Error checking system condition: {e}")

    def process_query(self, query):
        """
        Process and respond to user queries.
        
        Args:
            query (str): User's voice command converted to text
        """
        try:
            if query == "None":
                return
                
            # Route queries to appropriate handlers based on keywords
            if any(word in query for word in ['whatsapp', 'instagram']):
                self.handle_social_media(query)
            elif any(word in query for word in ['schedule', 'university timetable']):
                self.get_schedule()
            elif any(word in query for word in ['volume up', 'increase volume']):
                pyautogui.press("volumeup")
                self.speak("Volume increased")
            elif "system condition" in query:
                self.check_system_condition()
            elif "exit" in query:
                self.speak("Goodbye!")
                sys.exit(0)
            else:
                self.handle_chat(query)
        except Exception as e:
            print(f"Error processing query: {e}")

    def handle_chat(self, query):
        """
        Process general chat queries using the ML model.
        
        Args:
            query (str): User's text query to be processed
        """
        try:
            # Preprocess the query
            padded_sequences = pad_sequences(
                self.tokenizer.texts_to_sequences([query]), 
                maxlen=20, 
                truncating='post'
            )
            # Get prediction from model
            result = self.model.predict(padded_sequences)
            tag = self.label_encoder.inverse_transform([np.argmax(result)])
            
            # Find and speak appropriate response
            for intent in self.data['intents']:
                if intent['tag'] == tag:
                    response = np.random.choice(intent['responses'])
                    self.speak(response)
                    break
        except Exception as e:
            print(f"Error in chat handling: {e}")

    def run(self):
        """Main loop to run the virtual assistant continuously."""
        self.greet()
        while True:
            try:
                query = self.listen_command()
                self.process_query(query)
            except KeyboardInterrupt:
                print("\nExiting...")
                sys.exit(0)
            except Exception as e:
                print(f"Error in main loop: {e}")
                continue

if __name__ == "__main__":
    # Create and run a single instance of the virtual assistant
    assistant = VirtualAssistant()
    assistant.run()