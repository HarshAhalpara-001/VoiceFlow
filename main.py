import speech_recognition as sr
import pyttsx3
import spacy
import os
import pyperclip

# Load the trained spaCy model
nlp = spacy.load("winTA_model_updated")

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function to convert text to speech
def speak(text):
    print(f"System: {text}")
    engine.say(text)
    engine.runAndWait()

# Function to predict intent and entities
def predict_intent_and_entities(text):
    doc = nlp(text)
    intent = max(doc.cats, key=doc.cats.get)
    confidence = doc.cats[intent]
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    print(f"User Input: {text}\nPredicted Intent: {intent} (Confidence: {confidence:.2f})\nEntities: {entities}\n")
    return intent, entities

# Function to handle intents and entities
def handle_intent(intent, entities, text):
    if intent == "copy_text":
        pyperclip.copy(text)
        speak("Text copied to clipboard.")
    elif intent == "paste_text":
        pasted_text = pyperclip.paste()
        speak(f"Pasted Text: {pasted_text}")
    elif intent == "shutdown_system":
        # os.system("shutdown /s /t 1")  # Windows shutdown command
        speak("System is shutting down...")
    elif intent == "restart_system":
        # os.system("shutdown /r /t 1")  # Windows restart command
        speak("System is restarting...")
    elif intent == "open_app":
        app_name = next((ent[0] for ent in entities if ent[1] == "APP_NAME"), None)
        if app_name:
            os.system(f"start {app_name}")  # Open app on Windows
            speak(f"Opening {app_name}...")
        else:
            speak("App name not found.")
    elif intent == "adjust_volume":
        volume_level = next((ent[0] for ent in entities if ent[1] == "VOLUME_LEVEL"), None)
        if volume_level:
            speak(f"Adjusting volume to {volume_level}...")  # Add volume control logic here
        else:
            speak("Volume level not found.")
    elif intent == "terminate_app":
        app_name = next((ent[0] for ent in entities if ent[1] == "APP_NAME"), None)
        if app_name:
            os.system(f"taskkill /im {app_name}.exe /f")  # Terminate app on Windows
            speak(f"Terminating {app_name}...")
        else:
            speak("App name not found.")
    else:
        speak("Command not recognized.")

# Function to listen to user's voice input
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)  # Reduce background noise
        audio = recognizer.listen(source)

    try:
        print("Processing...")
        text = recognizer.recognize_google(audio)  # Use Google Web Speech API
        print(f"User: {text}")
        return text
    except sr.UnknownValueError:
        speak("Sorry, I did not understand that.")
        return None
    except sr.RequestError:
        speak("Sorry, my speech service is down.")
        return None
        
# Main loop for voice assistance
def voice_assistance():
    speak("Hello! How can I assist you today?")
    while True:
        text = listen()
        print(f"User: {text}")
        if text:
            if text.lower() in ["exit", "quit", "stop"]:
                speak("Goodbye!")
                break
            intent, entities = predict_intent_and_entities(text)
            handle_intent(intent, entities, text)

# Run the voice assistance
voice_assistance()
