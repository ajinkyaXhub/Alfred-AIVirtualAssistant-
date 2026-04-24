import speech_recognition as sr
import webbrowser
import pyttsx3
import time
import os
import asyncio
import pywhatkit
import pyautogui
import cv2
from winsdk.windows.devices.geolocation import Geolocator
from geopy.geocoders import Nominatim
from google import genai
import musiclib

class AlfredCore:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1.5
        self.recognizer.non_speaking_duration = 0.5
        self.client = genai.Client(api_key="AIzaSyDNrvDAn0wL-fCd2gqVGNXg00IWlOAeXP4")
        self.chat_session = self.client.chats.create(
            model="gemini-2.0-flash",
            config={"system_instruction": "You are Alfred, a loyal and witty indian butler assistant. Keep your responses concise and helpful."}
        )
        self.brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        webbrowser.register('brave', None, webbrowser.GenericBrowser(self.brave_path))

    def speak(self, text, callback=None):
        if callback: callback(text)
        print(f"Alfred: {text}")
        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"Speech Error: {e}")

    def listen(self, status_callback=None):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            if status_callback: status_callback("Listening...")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                if status_callback: status_callback("Processing...")
                text = self.recognizer.recognize_google(audio).lower()
                print(f"Heard: {text}")
                return text
            except Exception as e:
                print(f"Listen Error: {e}")
                return ""

    def ask_gemini(self, query):
        try:
            response = self.chat_session.send_message(query)
            return response.text
        except Exception as e:
            print(f"Gemini Error: {e}")
            return "My apologies sir, I'm having trouble connecting."

    async def get_coords(self):
        locator = Geolocator()
        pos = await locator.get_geoposition_async()
        return pos.coordinate.latitude, pos.coordinate.longitude

    def process_command(self, command, speak_callback=None, status_callback=None):
        c_lower = command.lower().strip()
        if not c_lower: return True
        
        if c_lower == "alfred":
            self.speak("Yes sir, how can I help you?", speak_callback)
            return True

        if "search" in c_lower:
            query = c_lower.replace("search", "").replace("for", "").strip()
            self.speak(f"Searching Google for {query}", speak_callback)
            pywhatkit.search(query)
            return True

        elif "open google" in c_lower:
            self.speak("Opening Google", speak_callback)
            webbrowser.get('brave').open("https://www.google.com")
            return True
            
        elif "open youtube" in c_lower:
            self.speak("Opening YouTube", speak_callback)
            webbrowser.open("https://www.youtube.com")
            return True

        elif "play" in c_lower:
            try:
                parts = c_lower.split(" ")
                song = parts[1] if len(parts) > 1 else ""
                if song in musiclib.music:
                    link = musiclib.music[song]
                    self.speak(f"Playing {song}", speak_callback)
                    webbrowser.get('brave').open(link)
                else:
                    self.speak("Song not found in library.", speak_callback)
            except:
                self.speak("I couldn't fulfill the play request.", speak_callback)
            return True 

        elif "exit" in c_lower or "stop" in c_lower or "goodbye" in c_lower:
            self.speak("Goodbye sir", speak_callback)
            return False 

        elif "screenshot" in c_lower:
            name = f"screenshot_{int(time.time())}.png"
            pyautogui.screenshot(name)
            self.speak("Screenshot saved, sir.", speak_callback)
            return True

        elif "my location" in c_lower or "where am i" in c_lower:
            self.speak("Identifying your current address, sir.", speak_callback)
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                coords = loop.run_until_complete(self.get_coords())
                lat, lon = coords
                geolocator = Nominatim(user_agent="AlfredAssistant")
                location = geolocator.reverse(f"{lat}, {lon}")
                address_data = location.raw['address']
                city = address_data.get('city') or address_data.get('town') or address_data.get('village')
                self.speak(f"Sir, you are currently in {city}. The exact address is {location.address}", speak_callback)
            except:
                self.speak("I couldn't pinpoint the address, sir.", speak_callback)
            return True

        elif "take a photo" in c_lower or "selfie" in c_lower:
            self.speak("Initializing camera. 3... 2... 1...", speak_callback)
            cam = cv2.VideoCapture(0)
            ret, frame = cam.read()
            if ret:
                if not os.path.exists("Selfies"): os.makedirs("Selfies")
                file_name = f"Selfies/selfie_{int(time.time())}.png"
                cv2.imwrite(file_name, frame)
                self.speak("Photo captured, sir.", speak_callback)
            cam.release()
            return True

        elif len(c_lower) > 3:
            reply = self.ask_gemini(command)
            self.speak(reply, speak_callback)
            return True
        
        return True
