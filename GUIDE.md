# Alfred Command Guide 🎙️

Welcome to your personalized Alfred Assistant. Here is a list of all voice commands currently supported by the system.

## 🤖 Basic Interaction
- **"Alfred"**: Triggers a polite "Yes sir, how can I help you?" response. Use this to check if Alfred is listening properly.

## 🌐 Web & Search
- **"Open Google"**: Opens the Google homepage in your Brave browser.
- **"Open YouTube"**: Opens the YouTube homepage.
- **"Search [Query]"**: Searches Google for the specified query (e.g., "Search the weather today").

## 🎵 Music Control
Alfred can play specific songs from your local `musiclib.py` library:
- **"Play 505"**: Plays Arctic Monkeys - 505.
- **"Play Dhurandhar"**: Plays the specified YouTube link for Dhurandhar.
- **"Play Singham"**: Plays the Singham theme song.
- **"Play Skyfall"**: Plays Adele - Skyfall.

## 🛠️ System Tools
- **"Screenshot"**: Captures your current screen and saves it as a `.png` file in the ALFRED folder.
- **"My Location"** or **"Where am I"**: Uses geolocation to identify and speak your current address and city.
- **"Take a photo"** or **"Selfie"**: Activates your webcam, counts down (3, 2, 1), and saves a photo in the `Selfies/` folder.

## 💬 Smart Assistant (Gemini AI)
- Any other query or question (longer than 3 characters) will be sent to the Gemini AI. 
- Example: "Tell me a joke," "Who is Batman?" or "How do I make tea?"
- *Note: If you hear "My apologies sir, I'm having trouble connecting," it means the AI service is temporarily unavailable or your rate limit has been reached.*

## 🚪 Exit
- **"Exit"**, **"Stop"**, or **"Goodbye"**: Closes the application and stops all listening processes.

---
### 💡 Tips for better recognition:
1. Speak clearly and wait for the "Listening..." status to appear in the GUI.
2. If a command isn't recognized, check the terminal for the "Heard: ..." debug log to see what Alfred recognized.
3. Use the **Microphone Button** in the GUI to manualy start/stop the listening mode.
