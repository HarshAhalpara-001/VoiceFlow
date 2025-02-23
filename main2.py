import os
import json
import speech_recognition as sr
import subprocess
import pyperclip
import webbrowser
from dotenv import load_dotenv
from AI_runner import AI

# Load environment variables
load_dotenv()

# Load user preferences
def load_user_data():
    with open("user_data.json", "r") as file:
        return json.load(file)

user_data = load_user_data()

# Voice recognition with multiple language support
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"Listening, {user_data['name']}...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = recognizer.recognize_google(audio).lower()
            print(f"You said: {text}")
            return text
        except (sr.UnknownValueError, sr.RequestError):
            return "Sorry, I couldn't understand."

# AI Assistant for intent extraction (Supports Multiple Intents)
ai = AI(api_key=os.getenv("OPENAI_API_KEY"),
        system_prompt='''Extract multiple intents & entities in JSON format:

{
  "intents": [
    {"intent": "<intent>", "entity": "<entity>"},
    {"intent": "<intent>", "entity": "<entity>"}
  ]
}

### Supported Intents:
1. **set_brightness**: Set brightness (0-100).
2. **set_volume**: Set system volume (0-100).
3. **shutdown**: Shutdown the system.
4. **restart**: Restart the system.
5. **open_app**: Open an application.
6. **open_website**: Open a website.
7. **search_youtube**: Search YouTube.
8. **search_web**: Google search query.
9. **set_reminder**: Set a reminder in seconds.
10. **summarize_pdf**: Summarize a PDF file.
11. **open_file**: Open a file.
12. **move_file**: Move a file.
13. **delete_file**: Delete a file.
14. **play_music**: Play music.
15. **check_weather**: Get the weather.
16. **wifi_control**: Enable or disable Wi-Fi.
17. **bluetooth_control**: Enable or disable Bluetooth.
18. **clipboard_copy**: Copy text to clipboard.
19. **clipboard_paste**: Paste clipboard content.
20. **clipboard_clear**: Clear clipboard content.
21. **take_screenshot**: Capture and save a screenshot.
22. **get_system_info**: Retrieve system details.
23. **add_comment**: Add a comment to a file.
24. **remove_comment**: Remove all comments from a file.

If unclear, return {"intents": [{"intent": "unknown", "entity": ""}]}.
''')

# Perform system actions
def execute_task(intent, entity):
    if intent == "set_brightness":
        os.system(f"powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{entity})")
        print(f"Brightness set to {entity}%")

    elif intent == "set_volume":
        os.system(f"nircmd.exe setsysvolume {int(entity) * 655}")
        print(f"Volume set to {entity}%")

    elif intent == "shutdown":
        os.system("shutdown /s /t 5")
        print("System will shut down in 5 seconds.")

    elif intent == "restart":
        os.system("shutdown /r /t 5")
        print("System will restart in 5 seconds.")

    elif intent == "open_app":
        os.system(f"start {entity}")
        print(f"Opening {entity}...")

    elif intent == "open_website":
        webbrowser.open(entity)
        print(f"Opening website: {entity}")

    elif intent == "search_web":
        webbrowser.open(f"https://www.google.com/search?q={entity}")
        print(f"Searching Google for: {entity}")

    elif intent == "search_youtube":
        webbrowser.open(f"https://www.youtube.com/results?search_query={entity}")
        print(f"Searching YouTube for: {entity}")

    elif intent == "set_reminder":
        time, message = entity.split(",", 1)
        print(f"Reminder set for {message} in {time} seconds.")
        subprocess.Popen(["python", "-c", f"import time; time.sleep({time}); print('Reminder:', '{message}')"])

    elif intent == "open_file":
        os.system(f"start {entity}")
        print(f"Opening file {entity}...")

    elif intent == "move_file":
        src, dest = entity.split(",", 1)
        os.rename(src, dest)
        print(f"Moved {src} to {dest}")

    elif intent == "delete_file":
        os.remove(entity)
        print(f"Deleted file {entity}")

    elif intent == "play_music":
        os.system(f"start {entity}.mp3")
        print(f"Playing {entity}...")

    elif intent == "check_weather":
        webbrowser.open("https://www.weather.com")
        print("Fetching weather details...")

    elif intent == "wifi_control":
        if entity == "enable":
            os.system("netsh interface set interface Wi-Fi admin=enabled")
            print("Wi-Fi enabled")
        else:
            os.system("netsh interface set interface Wi-Fi admin=disabled")
            print("Wi-Fi disabled")

    elif intent == "bluetooth_control":
        if entity == "enable":
            os.system("powershell Start-Service bthserv")
            print("Bluetooth enabled")
        else:
            os.system("powershell Stop-Service bthserv")
            print("Bluetooth disabled")

    elif intent == "clipboard_copy":
        pyperclip.copy(entity)
        print(f"Copied to clipboard: {entity}")

    elif intent == "clipboard_paste":
        print(f"Pasted: {pyperclip.paste()}")

    elif intent == "clipboard_clear":
        pyperclip.copy("")
        print("Clipboard cleared")

    elif intent == "take_screenshot":
        os.system("nircmd.exe savescreenshot screenshot.png")
        print("Screenshot saved as 'screenshot.png'")

    elif intent == "get_system_info":
        os.system("systeminfo")
        print("Fetching system info...")

    elif intent == "add_comment":
        file_path, comment = entity.split(",", 1)
        with open(file_path, "r+") as file:
            content = file.readlines()
            content.insert(0, f"# {comment}\n")
            file.seek(0)
            file.writelines(content)
        print(f"Comment added to {file_path}: {comment}")

    elif intent == "remove_comment":
        file_path = entity.strip()
        with open(file_path, "r") as file:
            lines = file.readlines()
        with open(file_path, "w") as file:
            for line in lines:
                if not line.strip().startswith("#"):
                    file.write(line)
        print(f"Comments removed from {file_path}")

# Main execution loop
command = listen()
response = json.loads(ai.chat(command))  # AI extracts multiple intents
print(response)
# Execute all detected intents
for intent_obj in response["intents"]:
    execute_task(intent_obj["intent"], intent_obj["entity"])
