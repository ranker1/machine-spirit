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

# Load configuration
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()

# Initialize TTS engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[config['voice_settings']['voice_id']].id)
engine.setProperty('rate', config['voice_settings']['rate'])
engine.setProperty('volume', config['voice_settings']['volume'])

# Warhammer-themed responses
responses = config['commands']

# Global variable to manage activation state
activated = False

def speak(text):
    engine.say(text)
    engine.runAndWait()

def generate_response(prompt):
    nlp = pipeline("text-generation", model="gpt2")
    warhammer_prompt = f"Omnissiah AI speaking about {prompt}. Response should sound reverent and mechanical."
    response = nlp(warhammer_prompt, max_length=50, num_return_sequences=1)[0]['generated_text']
    return response

def run_diagnostics():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()
    diagnostics_report = f"CPU usage is at {cpu_usage}%. Memory usage is {memory_info.percent}% of available resources."
    return diagnostics_report

def open_browser():
    try:
        if os.name == 'nt':  # Windows
            os.startfile(config['paths']['browser_url'])
        elif os.name == 'posix':  # Unix-based systems
            subprocess.call(["xdg-open", config['paths']['browser_url']])
    except Exception as e:
        return f"Failed to open browser: {str(e)}"
    return "The sacred web browser has been opened."

def open_editor():
    try:
        if os.name == 'nt':  # Windows
            os.startfile(config['paths']['editor_path'])
        elif os.name == 'posix':  # Unix-based systems
            subprocess.call([config['paths']['editor_path']])
    except Exception as e:
        return f"Failed to open editor: {str(e)}"
    return "The text editor has been opened."

def shutdown_system():
    try:
        if os.name == 'nt':  # Windows
            subprocess.call(["shutdown", "/s", "/t", "0"])
        elif os.name == 'posix':  # Unix-based systems
            subprocess.call(["shutdown", "-h", "now"])
    except Exception as e:
        return f"Failed to initiate shutdown: {str(e)}"
    return "Shutdown sequence has been initiated."

def restart_system():
    try:
        if os.name == 'nt':  # Windows
            subprocess.call(["shutdown", "/r", "/t", "0"])
        elif os.name == 'posix':  # Unix-based systems
            subprocess.call(["shutdown", "-r", "now"])
    except Exception as e:
        return f"Failed to initiate restart: {str(e)}"
    return "Restart sequence has been initiated."

def create_file():
    try:
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write("This is a new file created by the Omnissiah.")
            return "A new file has been created."
        else:
            return "File creation was canceled."
    except Exception as e:
        return f"Failed to create file: {str(e)}"

def delete_file():
    try:
        file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        if file_path:
            os.remove(file_path)
            return "The file has been deleted."
        else:
            return "File deletion was canceled."
    except Exception as e:
        return f"Failed to delete file: {str(e)}"

def move_file():
    try:
        src_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        if src_path:
            dest_path = filedialog.asksaveasfilename(defaultextension=os.path.splitext(src_path)[1], filetypes=[("All Files", "*.*")])
            if dest_path:
                shutil.move(src_path, dest_path)
                return "The file has been moved."
            else:
                return "Destination path selection was canceled."
        else:
            return "Source path selection was canceled."
    except Exception as e:
        return f"Failed to move file: {str(e)}"

def rename_file():
    try:
        src_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        if src_path:
            dest_path = filedialog.asksaveasfilename(defaultextension=os.path.splitext(src_path)[1], filetypes=[("All Files", "*.*")])
            if dest_path:
                os.rename(src_path, dest_path)
                return "The file has been renamed."
            else:
                return "New name path selection was canceled."
        else:
            return "Source path selection was canceled."
    except Exception as e:
        return f"Failed to rename file: {str(e)}"

def copy_file():
    try:
        src_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
        if src_path:
            dest_path = filedialog.asksaveasfilename(defaultextension=os.path.splitext(src_path)[1], filetypes=[("All Files", "*.*")])
            if dest_path:
                shutil.copy(src_path, dest_path)
                return "The file has been copied."
            else:
                return "Destination path selection was canceled."
        else:
            return "Source path selection was canceled."
    except Exception as e:
        return f"Failed to copy file: {str(e)}"

def setup_gui():
    def on_create_file():
        result = create_file()
        messagebox.showinfo("Result", result)
    
    def on_delete_file():
        result = delete_file()
        messagebox.showinfo("Result", result)
    
    def on_move_file():
        result = move_file()
        messagebox.showinfo("Result", result)
    
    def on_rename_file():
        result = rename_file()
        messagebox.showinfo("Result", result)
    
    def on_copy_file():
        result = copy_file()
        messagebox.showinfo("Result", result)
    
    gui = tk.Tk()
    gui.title("Omnissiah File Operations")

    tk.Button(gui, text="Create File", command=on_create_file).pack(pady=5)
    tk.Button(gui, text="Delete File", command=on_delete_file).pack(pady=5)
    tk.Button(gui, text="Move File", command=on_move_file).pack(pady=5)
    tk.Button(gui, text="Rename File", command=on_rename_file).pack(pady=5)
    tk.Button(gui, text="Copy File", command=on_copy_file).pack(pady=5)
    
    gui.mainloop()

def handle_command(command):
    global activated
    if "machine spirit" in command:
        activated = True
        return "Omnissiah AI activated. You may now issue commands."
    elif "exit" in command:
        activated = False
        return "Command processing has been disabled. Say 'Machine Spirit' to activate."
    elif "deactivate" in command:
        return "Deactivating Omnissiah AI. Goodbye!"
        
    if not activated:
        return "The Omnissiah AI is currently deactivated. Say 'Machine Spirit' to activate."

    if "activate" in command:
        response = responses.get("activate", responses["default"])
    elif "status" in command:
        response = responses.get("status", responses["default"])
    elif "diagnostics" in command:
        response = run_diagnostics()
    elif "purge" in command:
        response = responses.get("purge", responses["default"])
    elif "commune" in command:
        response = responses.get("commune", responses["default"])
    elif "sanctify" in command:
        response = responses.get("sanctify", responses["default"])
    elif "ritual reboot" in command:
        response = responses.get("ritual reboot", responses["default"])
    elif "invoke blessing" in command:
        response = responses.get("invoke blessing", responses["default"])
    elif "access archives" in command:
        response = responses.get("access archives", responses["default"])
    elif "tech blessing" in command:
        response = responses.get("tech blessing", responses["default"])
    elif "open browser" in command:
        response = open_browser()
    elif "open editor" in command:
        response = open_editor()
    elif "shutdown" in command:
        response = shutdown_system()
    elif "restart" in command:
        response = restart_system()
    elif "create file" in command:
        response = "Opening GUI for file creation."
        Thread(target=setup_gui).start()
    elif "delete file" in command:
        response = "Opening GUI for file deletion."
        Thread(target=setup_gui).start()
    elif "move file" in command:
        response = "Opening GUI for file movement."
        Thread(target=setup_gui).start()
    elif "rename file" in command:
        response = "Opening GUI for file renaming."
        Thread(target=setup_gui).start()
    elif "copy file" in command:
        response = "Opening GUI for file copying."
        Thread(target=setup_gui).start()
    elif "error" in command:
        response = responses.get("error", responses["default"])
    elif "help" in command:
        response = responses.get("help", responses["default"])
    else:
        response = responses.get("default", responses["default"])

    return response

def listen_for_command():
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("Calibrating for background noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print(f"Listening with ambient noise threshold set to {recognizer.energy_threshold}")
        
        print("Listening for commands...")
        audio = recognizer.listen(source)
        
        try:
            command = recognizer.recognize_google(audio, language='en-US', show_all=False)
            print(f"Recognized command: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return ""
        except sr.RequestError:
            print("Sorry, there was an issue with the speech recognition service.")
            return ""

def main():
    while True:
        command = listen_for_command()
        if command:
            response = handle_command(command)
            speak(response)
            if "deactivate" in command:
                break

if __name__ == "__main__":
    main()
