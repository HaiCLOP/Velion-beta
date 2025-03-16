import speech_recognition as sr
import pyttsx3
import re
import datetime
import cv2
import webbrowser
import time
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import requests
import subprocess
from googletrans import Translator
import os
import winreg
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from colorama import Fore, Back, Style
import random
import json

print("Loading your AI personal assistant - Velion")

# Initialize the speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Function to make the assistant speak
def speak(text, echo=True, wait=True, speaker="Velion"):
    if echo: print(Style.BRIGHT+speaker+Style.RESET_ALL+":", text)
    engine.say(text)
    try:
        if wait: engine.runAndWait()
    except Exception:
        pass

# Load data from JSON files
def load_json(file_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_dir, file_name), 'r') as file:
        return json.load(file)

# Load website mappings, jokes, riddles, and quotes
websites = load_json('websites.json')
jokes = load_json('jokes.json')
riddles = load_json('riddles.json')
quotes = load_json('quotes.json')


# Greeting function based on time of day
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



# Function to recognize user voice input
def takeCommand(parseErrorPlayback = True):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)  # Calibrate for ambient noise
        print(f"Listening...", end='\r')
        audio = r.listen(source)

        try:
            statement = r.recognize_google(audio, language='en-in')
        except sr.UnknownValueError:
            if parseErrorPlayback: speak("I'm sorry, I didn't catch that. Could you please repeat?")
            return "None"
        except sr.RequestError:
            speak("Sorry, I can't connect to the speech recognition service.")
            return "None"
        print(f"{Back.BLACK}{Style.BRIGHT}You: {Style.RESET_ALL}{statement}       ")
        return statement.lower()

def timer():
    speak("Okay! For how long should the timer be active for?")
    while 1:
        try:
            raw_time = takeCommand()
            if raw_time == 'None': continue
            raw_time = raw_time.replace('in ', '').replace('and', '')
            if 'Parsing time':
                if 'minute' in raw_time:
                    if 'minutes' in raw_time: minutes = raw_time.split('minutes')[0].split()[-1]
                    else: minutes = raw_time.split('minute')[0].split()[-1]
                    if 'a' in minutes:
                        minutes = 1
                    else:
                        minutes = int(float(minutes))
                else:
                    minutes = 0
                if 'second' in raw_time:
                    if 'seconds' in raw_time: seconds = raw_time.split('seconds')[0].split()[-1]
                    else: seconds = raw_time.split('second')[0].split()[-1]
                    if 'a' in seconds:
                        seconds = 1
                    else:
                        seconds = int(float(seconds))
                else:
                    seconds = 0
            while seconds >= 60:
                minutes += 1
                seconds -= 60
            
            if minutes == 0 and seconds == 0:
                speak("I didn't get that. Could you say that again?")
                continue
            time_in_words = ""
            if minutes > 0:
                time_in_words = f"{minutes} minutes"
            if minutes > 0 and seconds > 0:
                time_in_words += " and "
            if seconds > 0:
                time_in_words += f"{seconds} seconds"
            speak(time_in_words)
            speak("Is that correct? Say yes or no")
            while 1: # Take command
                c = takeCommand(parseErrorPlayback=False)
                if not c == 'None':
                    break
                speak("I didnt get that. Is that correct?")
            if 'y' not in c:
                speak("Okay, could you say how long again?")
                continue
            speak(f"Okay then, starting timer for {time_in_words}")
            while 1:
                if minutes <= 0 and seconds <= 0:
                    speak("Times up.")
                    return

                if minutes > 0 or seconds > 5:
                    time.sleep(4)
                    seconds -= 5
                else:
                    time.sleep(seconds)
                    seconds -= seconds
                time_in_words = ""
                if minutes > 0:
                    time_in_words = f"{minutes} minutes"
                if minutes > 0 and seconds > 0:
                    time_in_words += " and "
                if seconds > 0:
                    time_in_words += f"{seconds} seconds"
                speak(f"{time_in_words} left", wait=True)
                
                if seconds < 0 and minutes > 0:
                    seconds += 60
                    minutes -= 1
        
        except Exception:
            speak("Could you say how long again?")
def extract_number(text):
    """Extracts the first number found in a string."""
    match = re.search(r"\d+", text)
    return int(match.group()) if match else None
#Alram Mechanism
def set_alarm():
    speak("At what time would you like to set the alarm? Please tell the time in HH:MM format.")
    alarm_time = takeCommand()
    if alarm_time != "none":
        try:
            alarm_hour, alarm_minute = map(int, alarm_time.split(":"))
            speak(f"Setting the alarm for {alarm_hour}:{alarm_minute}.")
            print(f"Alarm set for {alarm_hour}:{alarm_minute}")

            while True:
                current_time = datetime.datetime.now()
                current_hour = current_time.hour
                current_minute = current_time.minute

                if current_hour == alarm_hour and current_minute == alarm_minute:
                    speak("Time to wake up! The alarm is ringing!")
                    print("Alarm is ringing!")
                    break
                time.sleep(30)  # Check every 30 seconds if it's time for the alarm
        except ValueError:
            speak("Invalid time format. Please try again using HH:MM format.")
    else:
        speak("I couldn't get the alarm time. Please try again.")

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

    






#Alram Mechanism
def set_alarm():
    speak("At what time would you like to set the alarm? Please tell the time in HH:MM format.")
    alarm_time = takeCommand()
    if alarm_time != "none":
        try:
            alarm_hour, alarm_minute = map(int, alarm_time.split(":"))
            speak(f"Setting the alarm for {alarm_hour}:{alarm_minute}.")
            print(f"Alarm set for {alarm_hour}:{alarm_minute}")

            while True:
                current_time = datetime.datetime.now()
                current_hour = current_time.hour
                current_minute = current_time.minute

                if current_hour == alarm_hour and current_minute == alarm_minute:
                    speak("Time to wake up! The alarm is ringing!")
                    print("Alarm is ringing!")
                    break
                time.sleep(30)  # Check every 30 seconds if it's time for the alarm
        except ValueError:
            speak("Invalid time format. Please try again using HH:MM format.")
    else:
        speak("I couldn't get the alarm time. Please try again.")

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



# Spotify credentials
SPOTIPY_CLIENT_ID = "a013d93c5f754101a75ac93af8d84065"
SPOTIPY_CLIENT_SECRET = "e0738d7da50c4043999cf9a8a91d64bf"

# Initialize Spotify API client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET
))

# Spotify play music function
def play_music_on_spotify(query):
    try:
        results = sp.search(q=query, type='track', limit=1)
        tracks = results['tracks']['items']

        if tracks:
            track = tracks[0]
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            spotify_url = track['external_urls']['spotify']

            speak(f"Playing {track_name} by {artist_name}.")
            webbrowser.open(spotify_url)
        else:
            speak("Sorry, I couldn't find any matching songs on Spotify.")
    except Exception as e:
        speak("There was an issue accessing Spotify.")
        print(e)

# Main program starts here
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
        
        if 'help' in statement:
            webbrowser.open_new_tab('file:///C:/Users/Student/Desktop/Arnav%208B/help.html')
            speak("Sure! Here is the list of commands.")

        if 'hello' in statement:
            speak("Hello! How can i assist you?")

        elif 'convert' in statement:
            convert_currency(statement)
        
        elif 'developers' or 'who made you' in statement:
            speak("I was developed by Haiclop Corps")
            print("I was developed by HaiCLOP Corps")

        elif statement.startswith("play "):
            song_query = statement.replace("play ", "").strip()
            play_music_on_spotify(song_query)
            continue

        elif 'open app' in statement:
            open_application(statement)

        # Website Navigation
        opened_website = False
        for item in websites:
            if f"open {item['name'].lower()}" in statement:
                speak(f"Opening {item['name']}", wait=False)
                webbrowser.open_new_tab(item['url'])
                opened_website = True
        if opened_website:
            continue

        # Timer
        elif 'timer' in statement:
            timer()

        # Jokes
        elif 'joke' in statement:
            speak(random.choice(jokes))

        # Riddles
        elif 'riddle' in statement:
            riddle = random.choice(riddles)
            speak(riddle["question"])
            time.sleep(2)
            speak(f"The answer is: {riddle['answer']}.")

        # Quotes
        elif 'motivate' in statement or 'quote' in statement:
            speak(random.choice(quotes))

        if "shutdown" in statement:
            speak("Shutting down the system.")
            os.system("shutdown /s /t 1")

        elif "restart" in statement:
            speak("Restarting the system.")
            os.system("shutdown /r /t 1")

        elif "log off" in statement:
            speak("Logging off.")
            os.system("shutdown /l")

        # Volume Control
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

        # Mute/Unmute Toggle
        elif "mute microphone" in statement or "unmute microphone" in statement or "toggle microphone" in statement:
            state = "1" if "mute" in statement else "0"
            os.system(f"nircmd.exe mutesysvolume {state} microphone")
            speak("Microphone muted." if state == "1" else "Microphone unmuted.")

        # Brightness Control
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

        # Wi-Fi Control
        elif "wifi on" in statement:
            os.system("powershell -Command \"Enable-NetAdapter -Name 'Wi-Fi' -Confirm:$false\"")
            speak("Wi-Fi enabled.")

        elif "wifi off" in statement:
            os.system("powershell -Command \"Disable-NetAdapter -Name 'Wi-Fi' -Confirm:$false\"")
            speak("Wi-Fi disabled.")


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


        
        
