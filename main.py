import speech_recognition as sr
import pyttsx3
import re
import screen_brightness_control as sbc
import datetime
import webbrowser
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import time
import wmi
import requests
import subprocess
from deep_translator import GoogleTranslator
import os
import winreg
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import json
import os
import pyperclip
from PIL import ImageTk, Image
from colorama import Fore, Back, Style
import random
import json



print("Loading your AI personal assistant - Velion")

# Initialize the speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def speak(text, echo=True, wait=True, speaker="Velion"):
    if echo: print(Style.BRIGHT+speaker+Style.RESET_ALL+":", text)
    engine.say(text)
    try:
        if wait: engine.runAndWait()
    except Exception:
        pass

def load_json(file_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_dir, file_name), 'r') as file:
        return json.load(file)

websites = load_json('websites.json')
jokes = load_json('jokes.json')
riddles = load_json('riddles.json')
quotes = load_json('quotes.json')
trivia_questions = load_json('trivia_questions.json')

def wishMe():
    hour = datetime.datetime.now().hour
    print(Style.BRIGHT+Back.LIGHTGREEN_EX+Fore.GREEN,end=" ")
    if 0 <= hour < 12:
        print("Hello, Good Morning ", end=Style.RESET_ALL+"\n")
        speak("Hello, Good Morning", echo=False)
    elif 12 <= hour < 18:
        print("Hello, Good Afternoon ", end=Style.RESET_ALL+"\n")
        speak("Hello, Good Afternoon", echo=False)
    else:
        print("Hello, Good Evening ", end=Style.RESET_ALL+"\n")
        speak("Hello, Good Evening", echo=False)
    print()

def takeCommand(parseErrorPlayback=True):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print(f"Listening...", end='\r')
        audio = r.listen(source)

        try:
            statement = r.recognize_google(audio, language='en-in')
        except sr.UnknownValueError:
            if parseErrorPlayback: speak("I'm sorry, I didn't catch that. Could you please repeat?")
            return "none"
        except sr.RequestError:
            speak("Sorry, I can't connect to the speech recognition service.")
            return "none"
        print(f"{Back.BLACK}{Style.BRIGHT}You: {Style.RESET_ALL}{statement}       ")
        return statement.lower()
    
def extract_number(text):
    """Extracts the first number found in a string."""
    match = re.search(r"\d+", text)
    return int(match.group()) if match else None

def timer():
    speak("How long should the timer run?")
    while True:
        try:
            raw_time = takeCommand()
            if raw_time == 'none': continue
            raw_time = raw_time.replace('in ', '').replace('and', '')
            
            minutes = int(re.findall(r'\d+', raw_time.split('minute')[0])[-1]) if 'minute' in raw_time else 0
            seconds = int(re.findall(r'\d+', raw_time.split('second')[0])[-1]) if 'second' in raw_time else 0

            if minutes + seconds == 0:
                speak("Please specify a valid time")
                continue

            total_seconds = minutes * 60 + seconds
            speak(f"Starting timer for {minutes} minutes {seconds} seconds")
            time.sleep(total_seconds)
            speak("Timer completed!")
            break
        except Exception:
            speak("Let's try again")
def trivia_game():
    speak("Welcome to the trivia game! I'll ask 10 random questions. Say 'quit' to stop.")
    
    try:
        if not trivia_questions:
            raise ValueError("No questions loaded")
            
        selected = random.sample(trivia_questions, min(10, len(trivia_questions)))
        score = 0
        
        for idx, item in enumerate(selected, 1):
            speak(f"Question {idx}: {item['question']}")
            
            # Get and validate answer
            attempts = 0
            while attempts < 2:
                answer = takeCommand(parseErrorPlayback=False).strip().lower()
                
                if "quit" in answer or "exit" in answer:
                    speak("Ending trivia game early.")
                    return
                
                if not answer or answer == "none":
                    speak("I didn't catch that, please try again.")
                    attempts += 1
                    continue
                
                # Flexible answer comparison
                correct = item['answer'].strip().lower()
                if answer == correct:
                    score += 1
                    speak("Correct!")
                    break
                else:
                    speak(f"Sorry, the correct answer is {item['answer']}.")
                    break
            else:
                speak("Moving to next question.")
                
        speak(f"Final score: {score} out of {len(selected)}!")
        
    except Exception as e:
        speak("Couldn't start trivia game. Please check the questions file.")
        print(f"Trivia error: {str(e)}")


def set_brightness(level):
    c = wmi.WMI(namespace='wmi')
    methods = c.WmiMonitorBrightnessMethods()[0]
    methods.WmiSetBrightness(level, 0)
    speak(f"Brightness set to {level}%")

def ollama_chat(query):
    try:
        # Run Ollama locally to generate a response
        command = f'ollama run deepseek-r1:1.5b "{query}"'
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',  # Explicitly set encoding to UTF-8
            errors='replace'   # Replace invalid characters with a placeholder
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return "Sorry, I couldn't generate a response."
    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, I encountered an error."






def open_application(statement):
    statement = statement.replace("open ", "").strip()  # Extract app name

    # Predefined system applications
    system_apps = {
        "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "command prompt": "cmd.exe",
    "task manager": "taskmgr.exe",
    "control panel": "control.exe",
    "paint": "mspaint.exe",
    "file explorer": "explorer.exe",
    "wordpad": "write.exe",
    "snipping tool": "SnippingTool.exe",
    "windows terminal": "wt.exe",
    "windows settings": "ms-settings:",
    "microsoft edge": "msedge.exe",
    "camera": "start microsoft.windows.camera:"

    }

    # Try opening system applications first
    for app in system_apps:
        if app in statement:
            try:
                subprocess.Popen(system_apps[app])
                speak(f"Opening {app}")
                return True
            except Exception as e:
                speak(f"Sorry, I couldn't open {app}.")
                print(e)
                return False

    # Search installed programs in the Start Menu
    start_menu_paths = [
        os.environ['APPDATA'] + r"\Microsoft\Windows\Start Menu\Programs",
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs"
    ]

    for path in start_menu_paths:
        for root, _, files in os.walk(path):
            for file in files:
                if file.lower().endswith(".lnk") and statement.lower() in file.lower():
                    try:
                        os.startfile(os.path.join(root, file))
                        speak(f"Opening {file.replace('.lnk', '')}")
                        return True
                    except Exception as e:
                        speak("Sorry, I couldn't open the application.")
                        print(e)
                        return False

    

    # Search installed applications from the registry (Uninstall List)
    def get_installed_apps():
        apps = {}
        reg_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall")
        ]

        for hkey, reg_path in reg_paths:
            try:
                with winreg.OpenKey(hkey, reg_path) as key:
                    for i in range(0, winreg.QueryInfoKey(key)[0]):
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                path = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                if name and path:
                                    apps[name.lower()] = path
                            except FileNotFoundError:
                                pass
            except Exception:
                continue
        return apps

    installed_apps = get_installed_apps()
    
    for app_name, app_path in installed_apps.items():
        if statement.lower() in app_name:
            try:
                os.startfile(app_path)
                speak(f"Opening {app_name}")
                return True
            except Exception as e:
                speak(f"Sorry, I couldn't open {app_name}.")
                print(e)
                return False

    # Final fallback: Open using Windows Search (if no match is found)
    try:
        subprocess.run(f'start {statement}', shell=True)
        speak(f"Trying to open {statement}")
        return True
    except Exception as e:
        speak(f"Sorry, I couldn't find an application named {statement}.")
        print(e)
        return False

def convert_currency(statement):
    if "convert" in statement:
        try:
            # Example: "convert 100 USD to EUR"
            words = statement.split()
            amount = float(words[1])  # Amount to convert
            from_currency = words[2].upper()  # From currency code (e.g., USD)
            to_currency = words[4].upper()  # To currency code (e.g., EUR)
            
            # ExchangeRate-API (Free API)
            api_key = "63141497a9a268cd7fe7df7b"  # Replace with your actual API key
                    # E-mail: kayogec629@bmixr.com
                    # Password: password123

            url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{from_currency}"
            
            # Get exchange rates
            response = requests.get(url)
            data = response.json()
            
            # Check if API call was successful
            if data['result'] == 'success':
                conversion_rate = data['conversion_rates'].get(to_currency)
                
                if conversion_rate:
                    converted_amount = amount * conversion_rate
                    speak(f"{amount} {from_currency} is equal to {converted_amount:.2f} {to_currency}")
                else:
                    webbrowser.open_new_tab(f"https://www.google.com/search?q={statement.replace(' ', '+')}")
                    speak(f"Sorry, I couldn't find the conversion rate for {to_currency}. Heres the best I can do.")
            else:
                # Backup method: just search for it on google...
                webbrowser.open_new_tab(f"https://www.google.com/search?q={statement.replace(' ', '+')}")
                speak("Sorry, there was an issue with the currency conversion API. Heres the best I can do.")
        except Exception as e:
            speak("Sorry, I couldn't understand the conversion details.")
            print(e)

def play_music(query):
    try:
        results = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id="a013d93c5f754101a75ac93af8d84065",
            client_secret="e0738d7da50c4043999cf9a8a91d64bf"
        )).search(q=query, type='track', limit=1)
        
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            webbrowser.open(track['external_urls']['spotify'])
            speak(f"Playing {track['name']} by {track['artists'][0]['name']}")
        else:
            speak("Song not found")
    except Exception as e:
        speak("Music playback failed")

def handle_translation():
    speak("What text should I translate?")
    text = takeCommand()
    while text == "none":
        speak("Please repeat the text")
        text = takeCommand()
    
    speak("Target language?")
    lang = takeCommand()
    try:
        translated = GoogleTranslator(source='auto', target=lang).translate(text)
        speak(f"Translation: {translated}")
    except Exception as e:
        speak("Translation failed")

wishMe()
if __name__ == '__main__':
    failed = False
    while True:
        if not failed:
            speak("How can I assist you?")
            print("(Say HELP for commands)")
        statement = takeCommand()
        failed = False
        # Continue if no command was detected
        if statement == "None":
            failed = True
            continue
            
        elif "open " in statement:
            open_application(statement)
        
        elif "play " in statement:
            play_music(statement.replace("play ", ""))
        
        elif "timer" in statement:
            timer()

        elif "trivia" in statement or "quiz" in statement:
            trivia_game()
        
        elif "convert" in statement:
            convert_currency(statement)
        
        elif "translate" in statement:
            handle_translation()
        
        elif "brightness" in statement:
            level = extract_number(statement)
            if level is not None:
                if 0 <= level <= 100:
                    sbc.set_brightness(level)
                    speak(f"Brightness set to {level} percent.")
                else:
                    speak("Brightness level must be between 0 and 100.")
            else:
                speak("Please specify a brightness level.")

        elif "volume" in statement:
            level = extract_number(statement)
            if level is not None:
                if 0 <= level <= 100:
                    devices = AudioUtilities.GetSpeakers()
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    volume.SetMasterVolumeLevelScalar(level / 100, None)
                    speak(f"Volume set to {level} percent.")
                else:
                    speak("Volume level must be between 0 and 100.")
            else:
                speak("Please specify a volume level.")

        elif "wifi on" in statement:
            os.system("powershell -Command \"Enable-NetAdapter -Name 'Wi-Fi' -Confirm:$false\"")
            speak("Wi-Fi enabled.")

        elif "wifi off" in statement:
            speak("Wi-Fi disabled. Note Velion will shut down too, please restart velion after connecting to internet.")
            os.system("powershell -Command \"Disable-NetAdapter -Name 'Wi-Fi' -Confirm:$false\"")
        
        elif "joke" in statement:
            speak(random.choice(jokes))
        
        elif "quote" in statement or "motivate" in statement:
            speak(random.choice(quotes))
        
        elif "exit" in statement or "quit" in statement:
            speak("Goodbye!")
            break
        
        elif "who made you" in statement or "developer" in statement:
            speak("I was developed by Haiclop Labs")
        
        elif 'time' in statement and 'timer' not in statement:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"The time is {strTime}")
            speak(f"The time is {datetime.datetime.now().hour} {datetime.datetime.now().minute}", echo=False)

        elif "design" in statement or "structure" in statement:
            speak("I am a simple text-based Personal assistant. My structure is based on a combination of multiple APIs and code")

        elif 'search' in statement and 'youtube' not in statement and 'wiki' not in statement and 'github' not in statement:
            statement = statement.replace("search", "").strip()
            search_url = f"https://www.google.com/search?q={statement.replace(' ', '+')}"
            webbrowser.open_new_tab(search_url)
            speak(f"Searching for {statement} on Google...")
            time.sleep(5)

        

        elif 'wikipedia' in statement:
            statement = statement.replace("wikipedia", "").strip()
            search_url = f"https://en.wikipedia.org/w/index.php?search={statement.replace(' ', '+')}"
            webbrowser.open_new_tab(search_url)
            speak(f"Searching for {statement} on Wikipedia...")
            time.sleep(5)

        elif 'search youtube' in statement:
            statement = statement.replace("search youtube", "").strip()
            search_url = f"https://www.youtube.com/results?search_query={statement.replace(' ', '+')}"
            webbrowser.open_new_tab(search_url)
            speak(f"Searching on YouTube for {statement}...")
            time.sleep(5)

        elif 'search github' in statement:
            statement = statement.replace("search github", "").strip()
            search_url = f"https://github.com/search?q={statement.replace(' ', '%20')}&type=repositories"
            webbrowser.open_new_tab(search_url)
            speak(f"Searching for {statement} on GitHub...")
            time.sleep(5)

        elif "languages" in statement:
            speak("I am currently limited to speak and understand English.")

        elif 'who are you' in statement or 'what can you do' in statement or 'hu r u' in statement:
            speak("I am Velion, version 1.0, your personal assistant. I can open YouTube, Google Chrome, Gmail, Stack Overflow, tell you the time, search Wikipedia, get weather updates, and fetch news.")


        elif 'ask' in statement or 'query' in statement or 'chatgpt' in statement or '' in statement: # VelionAI
            speak("Sure! Connecting to AI engine...")
            print("Say EXIT or QUIT to stop talking to the AI.")
            time.sleep(0.5)
            messages = [{"role": "user", "content": "You are a chatbot named VelionAI. You have to make your responses short, more human like. (Max words per response: 25) Also, here are some more instructions: <WebAccess>FALSE You WILL be TERMINATED if you use Internet.<End WebAccess>"}]
            while 1:
                while 1:
                    query = takeCommand(parseErrorPlayback=False)
                    if query != "None": break
                    speak("Could you say that again?", speaker="VelionAI")
                if 'exit' in query or 'quit' in query:
                    speak("Terminating AI Chat...", speaker="VelionAI")
                    break
                messages.append({"role": "user", "content": query})

                url = "https://chatgpt-42.p.rapidapi.com/chatgpt"
                headers = {
                    'Content-Type': 'application/json',
                    'x-rapidapi-host': 'chatgpt-42.p.rapidapi.com',
                    'x-rapidapi-key': 'f48d13e7c9msh1f50b0e5cc8e91dp14b49cjsnfd296af7c063'
                }
                data = {
                    "messages": messages,
                    "web_access": False
                }

                response = requests.post(url, headers=headers, data=json.dumps(data))

                # Output the response from the server
                speak(response.json()['result'], speaker="VelionAI")

        
        else:
                speak("Command not recognised ask to AI, use chatbot for using AI")
                
