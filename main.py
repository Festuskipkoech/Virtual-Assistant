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
    def __init__(self):
        # Initialize all necessary components
        self.load_models()
        self.recognizer = sr.Recognizer()
        
    def load_models(self):
        """Load all necessary ML models and data"""
        try:
            with open("intents.json") as file:
                self.data = json.load(file)
            self.model = load_model("chat_model.h5")
            with open("tokenizer.pkl", "rb") as f:
                self.tokenizer = pickle.load(f)
            with open("label_encoder.pkl", "rb") as encoder_file:
                self.label_encoder = pickle.load(encoder_file)
        except FileNotFoundError as e:
            print(f"Error loading models: {e}")
            sys.exit(1)

    def speak(self, text, language='en'):
        """Text-to-speech conversion with error handling"""
        try:
            tts = gTTS(text=text, lang=language)
            filename = "output.mp3"
            tts.save(filename)
            os.system(f'mpg123 {filename}')
            os.remove(filename)
        except Exception as e:
            print(f"Error in speech synthesis: {e}")
            
    def listen_command(self):
        """Improved speech recognition with error handling"""
        try:
            with sr.Microphone() as source:
                print("Listening...", end="", flush=True)
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self.recognizer.pause_threshold = 1.0
                self.recognizer.phrase_threshold = 0.3
                self.recognizer.non_speaking_duration = 0.5
                audio = self.recognizer.listen(source, timeout=5)
                
            print("\rRecognizing...", end="", flush=True)
            query = self.recognizer.recognize_google(audio, language='en-us')
            print(f"\rUser said: {query}\n")
            return query.lower()
        except sr.RequestError:
            # print("Could not request results; check googler internet connection")
            return "None"
        except sr.UnknownValueError:
            # print("Could not understand audio")
            return "None"
        except Exception as e:
            # print(f"Error in speech recognition: {e}")
            return "None"

    def get_day_and_time(self):
        """Get current day and time information"""
        current_time = datetime.datetime.now()
        day_dict = {
            1: "Monday", 2: "Tuesday", 3: "Wednesday",
            4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"
        }
        return day_dict[current_time.weekday() + 1], current_time.hour

    def greet(self):
        """Improved greeting function"""
        day, hour = self.get_day_and_time()
        time_str = time.strftime("%I:%M %p")
        
        if 0 <= hour < 12:
            greeting = "Good morning"
        elif 12 <= hour < 16:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
            
        self.speak(f"{greeting} Festus, it's {day} and the time is {time_str}")

    def handle_social_media(self, query):
        """Handle social media related commands"""
        try:
            if 'whatsapp' in query:
                self.speak("Opening WhatsApp")
                webbrowser.open("https://web.whatsapp.com/")
            elif 'instagram' in query:
                self.speak("Opening Instagram")
                webbrowser.open("https://www.instagram.com/")
            else:
                self.speak("No result found")
        except Exception as e:
            print(f"Error opening social media: {e}")

    def get_schedule(self):
        """Get the schedule for the current day"""
        day, _ = self.get_day_and_time()
        day = day.lower()
        
        schedule = {
            "monday": "Boss, from 9:00 to 9:50 you have Algorithms class, from 10:00 to 11:50 you have System Design class, from 12:00 to 2:00 you have a break, and today you have Programming Lab from 2:00 onwards.",
            "tuesday": "Boss, from 9:00 to 9:50 you have Web Development class, from 10:00 to 10:50 you have a break, from 11:00 to 12:50 you have Database Systems class, from 1:00 to 2:00 you have a break, and today you have Open Source Projects lab from 2:00 onwards.",
            "wednesday": "Boss, today you have a full day of classes. From 9:00 to 10:50 you have Machine Learning class, from 11:00 to 11:50 you have Operating Systems class, from 12:00 to 12:50 you have Ethics in Technology class, from 1:00 to 2:00 you have a break, and today you have Software Engineering workshop from 2:00 onwards.",
            "thursday": "Boss, today you have a full day of classes. From 9:00 to 10:50 you have Computer Networks class, from 11:00 to 12:50 you have Cloud Computing class, from 1:00 to 2:00 you have a break, and today you have Cybersecurity lab from 2:00 onwards.",
            "friday": "Boss, today you have a full day of classes. From 9:00 to 9:50 you have Artificial Intelligence class, from 10:00 to 10:50 you have Advanced Programming class, from 11:00 to 12:50 you have UI/UX Design class, from 1:00 to 2:00 you have a break, and today you have Capstone Project work from 2:00 onwards.",
            "saturday": "Boss, today you have a more relaxed day. From 9:00 to 11:50 you have team meetings for your Capstone Project, from 12:00 to 12:50 you have Innovation and Entrepreneurship class, from 1:00 to 2:00 you have a break, and today you have extra time to work on personal development and coding practice from 2:00 onwards.",
            "sunday": "Boss, today is a holiday, but keep an eye on upcoming deadlines and use this time to catch up on any reading or project work."
        }
        
        if day in schedule:
            self.speak(schedule[day])
        else:
            self.speak("I couldn't determine the day's schedule")

    def open_app(self, query):
        """Open system applications"""
        try:
            if "calculator" in query:
                self.speak("Opening calculator")
                os.startfile('C:\\Windows\\System32\\calc.exe')
            elif "notepad" in query:
                self.speak("Opening notepad")
                os.startfile('C:\\Windows\\System32\\notepad.exe')
            elif "paint" in query:
                self.speak("Opening paint")
                os.startfile('C:\\Windows\\System32\\mspaint.exe')
        except Exception as e:
            print(f"Error opening application: {e}")

    def close_app(self, query):
        """Close system applications"""
        try:
            if "calculator" in query:
                self.speak("Closing calculator")
                os.system("taskkill /f /im calc.exe")
            elif "notepad" in query:
                self.speak("Closing notepad")
                os.system("taskkill /f /im notepad.exe")
            elif "paint" in query:
                self.speak("Closing paint")
                os.system("taskkill /f /im mspaint.exe")
        except Exception as e:
            print(f"Error closing application: {e}")

    def handle_browsing(self, query):
        """Handle web browsing requests"""
        try:
            if 'google' in query:
                self.speak("Boss, what should I search on Google...")
                search_query = self.listen_command()
                if search_query != "None":
                    webbrowser.open(f"https://www.google.com/search?q={search_query}")
        except Exception as e:
            print(f"Error in web browsing: {e}")

    def check_system_condition(self):
        """Check system status with error handling"""
        try:
            cpu_usage = psutil.cpu_percent()
            battery = psutil.sensors_battery()
            
            if battery is None:
                self.speak("Unable to get battery information")
                return
                
            self.speak(f"CPU is at {cpu_usage} percent")
            self.speak(f"Battery is at {battery.percent} percent")
            
            if battery.percent >= 80:
                self.speak("Power level is good, keep writing codes")
            elif 40 <= battery.percent < 80:
                self.speak("Connect to power in 30 minutes")
            else:
                self.speak("Low power, plug cable to power")
        except Exception as e:
            print(f"Error checking system condition: {e}")

    def process_query(self, query):
        """Process user queries with improved error handling"""
        try:
            if query == "None":
                return
                
            if any(word in query for word in ['whatsapp', 'instagram']):
                self.handle_social_media(query)
            elif any(word in query for word in ['schedule', 'university timetable']):
                self.get_schedule()
            elif "open" in query:
                self.open_app(query)
            elif "close" in query:
                self.close_app(query)
            elif "google" in query:
                self.handle_browsing(query)
            elif any(word in query for word in ['volume up', 'increase volume']):
                pyautogui.press("volumeup")
                self.speak("Volume increased")
            elif any(word in query for word in ['volume down', 'decrease volume']):
                pyautogui.press("volumedown")
                self.speak("Volume decreased")
            elif any(word in query for word in ['volume mute', 'mute the sound']):
                pyautogui.press("volumemute")
                self.speak("Volume muted")
            elif "system condition" in query:
                self.check_system_condition()
            elif "exit" in query:
                self.speak("Goodbye!")
                sys.exit(0)
            elif any(word in query for word in ['what', 'who', 'how', 'hi', 'thanks', 'hello']):
                self.handle_chat(query)
        except Exception as e:
            print(f"Error processing query: {e}")

    def handle_chat(self, query):
        """Handle chat responses using the ML model"""
        try:
            padded_sequences = pad_sequences(
                self.tokenizer.texts_to_sequences([query]), 
                maxlen=20, 
                truncating='post'
            )
            result = self.model.predict(padded_sequences)
            tag = self.label_encoder.inverse_transform([np.argmax(result)])
            
            for intent in self.data['intents']:
                if intent['tag'] == tag:
                    response = np.random.choice(intent['responses'])
                    self.speak(response)
                    break
        except Exception as e:
            print(f"Error in chat handling: {e}")

    def run(self):
        """Main loop with improved error handling"""
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
    assistant = VirtualAssistant()
    assistant.run()