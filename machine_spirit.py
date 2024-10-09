import pyttsx3
import speech_recognition as sr
from transformers import pipeline
import psutil
import os
import subprocess
import shutil
import json
import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread
import pvporcupine
import pyaudio
import numpy as np
import schedule
import time
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from groq import Groq

pronunciation_dict = {
    # Primarch Names
    "Horus": "Hoh-rus",
    "Sanguinius": "San-gwin-ee-us",
    "Angron": "An-gron",
    "Roboute Guilliman": "Ro-boo-tay Gee-lee-man",
    "Leman Russ": "Lee-man Russ",
    "Jaghatai Khan": "Jah-gah-tie Kahn",
    "Vulkan": "Vool-kan",
    "Magnus the Red": "Mag-nus the Red",
    "Perturabo": "Per-tuh-rah-bo",
    "Fulgrim": "Fool-grim",
    "Corvus Corax": "Cor-vus Cor-ax",
    "Mortarion": "Mor-tar-ee-on",
    "Lion El'Jonson": "Lion El-John-son",
    "Konrad Curze": "Kon-rad Kur-zay",
    "Angels of Death": "An-gels of Death",

    # Legion Names
    "Ultramarines": "Ul-trah-ma-reens",
    "World Eaters": "World Eat-ers",
    "Blood Angels": "Blood An-gels",
    "Dark Angels": "Dark An-gels",
    "Space Wolves": "Space Wolves",
    "Death Guard": "Death Guard",
    "Thousand Sons": "Thou-sand Sons",
    "Iron Hands": "Iron Hands",
    "Raven Guard": "Raven Guard",
    "Salamanders": "Sal-am-anders",
    "Word Bearers": "Word Bear-ers",
    "Emperor's Children": "Em-per-or's Chil-dren",
    "Alpha Legion": "Al-fa Lee-gion",
    "Imperial Fists": "Im-per-ee-al Fists",
    "Night Lords": "Night Lords",
    "White Scars": "White Scars",

    # Military Forces in the Imperium
    "Imperial Guard": "Im-per-ee-al Guard",
    "Adeptus Mechanicus": "A-dep-tus Mech-an-i-cus",
    "Adeptus Custodes": "A-dep-tus Cus-to-des",
    "Sisters of Battle": "Sis-ters of Bat-tle",
    "Inquisition": "In-quis-i-tion",
    "Astropath": "As-tro-path",
    "Sanctus": "Sanct-us",
    "Imperial Navy": "Im-per-ee-al Navy",
    "Tempestus Scions": "Tem-pes-tus Sci-ons",
    "Titan Legion": "Ti-tan Lee-gion",
    "Adeptus Sororitas": "A-dep-tus So-ro-ri-tas",
    
    # Miscellaneous Terms
    "The Emperor": "The Em-per-or",
    "Chaos": "Kay-os",
    "Xenos": "Zee-nos",
    "Orks": "Orks",
    "Necrons": "Ne-crons",
    "Tyranids": "Tyr-an-ids",
    "Genestealer": "Gene-steal-er",
}



# Load and save config functions
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

# Load configuration
config = load_config()

# Initialize text-to-speech engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[config['voice_settings']['voice_id']].id)
engine.setProperty('rate', config['voice_settings']['rate'])
engine.setProperty('volume', config['voice_settings']['volume'])

responses = config['commands']

audio_stream = None
pa = None
porcupine = None

# Initialize Groq client with API key
client = Groq(api_key="add-yours")

# Function to generate response using Groq AI
def generate_response(prompt):
    warhammer_prompt = f"The Omnissiah responds reverently about {prompt}. Ensure the response is accurate."
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": warhammer_prompt}
            ],
            model="llama3-8b-8192"  # You can choose the model based on availability
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating response: {str(e)}"


# Run system diagnostics
def run_diagnostics():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    diagnostics_report = responses['diagnostics'].format(cpu_usage=cpu_usage, memory_info=memory_info.used / (1024 ** 2))  # Convert bytes to MB
    return diagnostics_report

# Open browser or editor
def open_browser():
    return open_app(config['paths']['browser_url'], "browser")

def open_editor():
    return open_app(config['paths']['editor_path'], "editor")

# Open application based on path
def open_app(app_path, app_name):
    try:
        if os.name == 'nt':
            os.startfile(app_path)
        elif os.name == 'posix':
            subprocess.call(["xdg-open", app_path])
        return f"The sacred {app_name} has been opened by the grace of the Omnissiah."
    except Exception as e:
        return f"Failed to open {app_name}: {str(e)}"

# Shutdown or restart the system
def shutdown_system():
    return execute_system_command(["shutdown", "/s", "/t", "0"], "shutdown")

def restart_system():
    return execute_system_command(["shutdown", "/r", "/t", "0"], "restart")

def execute_system_command(command, action):
    try:
        subprocess.call(command)
        return f"The machine shall slumber now, as the Omnissiah wills it." if action == "shutdown" else "The Machine Spirit shall reboot, guided by the will of the Omnissiah."
    except Exception as e:
        return f"Failed to initiate {action}: {str(e)}"

# Handle file operations
def handle_file_operation(operation_func, operation_desc):
    def operation():
        result = operation_func()
        messagebox.showinfo("Result", result)
    
    Thread(target=operation).start()
    return f"Preparing to {operation_desc}, blessed be the Omnissiah."

# File operations: create, delete, move
def create_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "w") as file:
            file.write("This is a new file created by the Omnissiah.")
        return "A new file has been created, as ordained."
    return "File creation was canceled."

def delete_file():
    file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
    if file_path:
        os.remove(file_path)
        return "The file has been purged in the name of the Omnissiah."
    return "File deletion was canceled."

def move_file():
    src_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
    if src_path:
        dest_path = filedialog.asksaveasfilename(defaultextension=os.path.splitext(src_path)[1], filetypes=[("All Files", "*.*")])
        if dest_path:
            shutil.move(src_path, dest_path)
            return "The file has been relocated, as per the Omnissiah's will."
    return "Source or destination path selection was canceled."

# Weather functionality
def get_weather(city):
    api_key = "add-key"
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    response = requests.get(base_url)
    
    if response.status_code == 200:
        data = response.json()
        temperature = data['main']['temp']
        weather_description = data['weather'][0]['description']
        return f"The current temperature in {city} is {temperature}°C with {weather_description}."
    else:
        return "Could not retrieve weather data. Please check the city name."

# Voice registration and authentication
def register_voice(user_name):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print(f"Please say 'I am the {user_name}' to register your voice.")
        audio = recognizer.listen(source)
        try:
            voice_sample = recognizer.recognize_google(audio, show_all=False)
            voice_sample = voice_sample.lower()  # Convert to lowercase for matching
            config['users'][user_name]['voiceprint'] = voice_sample
            save_config(config)
            print(f"{user_name}'s voice has been registered successfully.")
            return True
        except sr.UnknownValueError:
            print("Could not understand the audio.")
            return False
        except sr.RequestError:
            print("Failed to connect to the Google API.")
            return False

def authenticate_user(voice_input):
    for user, profile in config['users'].items():
        if match_voiceprint(voice_input, profile['voiceprint']):
            return user, profile['role']
    return None, None

def match_voiceprint(voice_input, stored_voiceprint):
    return voice_input == stored_voiceprint

# Command and permission handling
def check_permissions(command, role):
    restricted_commands = ['shutdown', 'restart']
    if role == 'Tech-Priest' or role == 'admin':
        return True
    if command in restricted_commands:
        return False
    return True

# Listen for voice commands
def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio, show_all=False)
            print(f"Command recognized: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Could not understand the command.")
            return ""
        except sr.RequestError:
            print("Failed to connect to the Google API.")
            return ""

# Global variable to track if the assistant is active
is_active = False

# Handle the incoming command
def handle_command(command):
    global is_active  # Access the global variable
    role = None  # Initialize role variable

    # Check for activation or deactivation commands
    if "activate" in command:
        if not is_active:
            voice_input = capture_voice()
            user, role = authenticate_user(voice_input)
            if not user:
                return "Authentication failed. You do not have access."
            is_active = True
            return responses["activate"]

        return "The assistant is already active."

    elif "deactivate" in command:
        if is_active:
            is_active = False
            return "The assistant has been deactivated. Awaiting reactivation."

        return "The assistant is already inactive."

    if not is_active:
        return "The assistant is currently inactive. Please activate it first."

    # Open the GUI for file operations in a separate thread
    if "create file" in command:
        time.sleep(1)  # Add a delay of 1 second
        Thread(target=setup_gui).start()  # Run GUI in a separate thread
        return "Opening the file creation interface."

    elif "delete file" in command:
        time.sleep(1)  # Add a delay of 1 second
        Thread(target=setup_gui).start()  # Run GUI in a separate thread
        return "Opening the file deletion interface."

    elif "move file" in command:
        time.sleep(1)  # Add a delay of 1 second
        Thread(target=setup_gui).start()  # Run GUI in a separate thread
        return "Opening the file moving interface."

    # Other commands as before...
    if "register voice" in command:
        user_name = "Tech_Priest"  # You can customize this or ask the user
        if register_voice(user_name):
            return f"Your voice has been registered as {user_name}."
        else:
            return "Voice registration failed."

    # Check permissions only if the assistant is active
    if role is not None and not check_permissions(command, role):
        return "Access denied. Only authorized users have the authority for this command."

    # Additional command processing...
    if "diagnostics" in command:
        return run_diagnostics()
    elif "open browser" in command:
        return open_browser()
    elif "open editor" in command:
        return open_editor()
    elif "shutdown" in command:
        return shutdown_system()
    elif "restart" in command:
        return restart_system()
    elif "weather" in command:
        city = command.split("weather in")[-1].strip()
        return get_weather(city)
    elif command in responses:
        return responses[command]
    
    return generate_response(command)

# Capture voice for authentication
def capture_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for authentication...")
        audio = recognizer.listen(source)
        try:
            voice_input = recognizer.recognize_google(audio, show_all=False)
            return voice_input.lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""

def speak(text):
    # Replace words based on the pronunciation dictionary
    for word, pronunciation in pronunciation_dict.items():
        text = text.replace(word, pronunciation)

    engine.say(text)
    engine.runAndWait()


# Wake word listener with Porcupine
def wake_word_listener():
    access_key = "add-access-key"
    
    global porcupine, audio_stream, pa
    try:
        porcupine = pvporcupine.create(
            keyword_paths=["path-to-ppn"],
            access_key=access_key
        )
    except ValueError as e:
        print(f"Failed to create Porcupine instance: {e}")
        return
    
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    print("Listening for the wake word...")

    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = np.frombuffer(pcm, dtype=np.int16)
        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
            print("Wake word detected! Listening for command...")
            command = listen_for_command()
            if command:
                response = handle_command(command)
                speak(response)  # Make sure `speak` is defined before this
            print("Back to listening for the wake word...")


# GUI setup for file operations
def setup_gui():
    gui = tk.Tk()
    gui.title("Omnissiah File Operations")

    # Set the color scheme
    gui.configure(bg='black')
    gui.geometry("300x200")  # Set a fixed size for the window

    # Create a frame for the buttons
    frame = tk.Frame(gui, bg='black')
    frame.pack(pady=10)

    # Create buttons with Mechanicus-themed styling
    button_style = {
        "bg": "#A52A2A",  # Dark Red
        "fg": "gold",  # Gold text
        "font": ('Exocet Heavy', 12),  # Change to a known font for testing
        "relief": tk.RAISED,
        "bd": 5
    }

    tk.Button(frame, text="Create File", command=lambda: handle_file_operation(create_file, "create a file"), **button_style).pack(pady=5)
    tk.Button(frame, text="Delete File", command=lambda: handle_file_operation(delete_file, "delete a file"), **button_style).pack(pady=5)
    tk.Button(frame, text="Move File", command=lambda: handle_file_operation(move_file, "move a file"), **button_style).pack(pady=5)

    # Customization for hover effect (optional)
    for button in frame.winfo_children():
        button.bind("<Enter>", lambda e: e.widget.config(bg="#FF4500"))  # Change color on hover
        button.bind("<Leave>", lambda e: e.widget.config(bg="#A52A2A"))  # Revert color

    gui.mainloop()


if __name__ == "__main__":
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)

    Thread(target=run_scheduler).start()

    try:
        wake_word_listener()
    except KeyboardInterrupt:
        print("Terminating the program.")
    finally:
        if audio_stream is not None:
            audio_stream.stop_stream()
            audio_stream.close()
        if pa is not None:
            pa.terminate()
        if porcupine is not None:
            porcupine.delete()
