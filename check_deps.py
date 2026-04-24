import importlib

dependencies = [
    "speech_recognition",
    "webbrowser",
    "pyttsx3",
    "time",
    "sys",
    "os",
    "platform",
    "pywhatkit",
    "pyautogui",
    "wikipedia",
    "pygame",
    "requests",
    "cv2",
    "asyncio",
    "geopy",
    "gtts",
    "google.genai",
    "musiclib",
    "winsdk.windows.devices.geolocation"
]

missing = []
for dep in dependencies:
    try:
        importlib.import_module(dep)
        print(f"OK: {dep}")
    except ImportError:
        missing.append(dep)
        print(f"MISSING: {dep}")

if missing:
    print("\nMissing dependencies found:")
    for m in missing:
        print(f"- {m}")
else:
    print("\nAll dependencies are satisfied!")
