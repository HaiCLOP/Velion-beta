import os
import json
import time
import random
import speech_recognition as sr
import pyttsx3
import datetime
import requests
import webbrowser
import subprocess
from colorama import Fore, Back, Style

# Initialize the speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

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

# Function to make the assistant speak (skip <think> blocks)
def speak(text, echo=True, wait=True, speaker="Velion"):
    # Remove <think> blocks from the text
    text_without_think = ""
    inside_think = False
    for line in text.splitlines():
        if "<think>" in line:
            inside_think = True
        if "</think>" in line:
            inside_think = False
            continue
        if not inside_think:
            text_without_think += line + "\n"

    # Print and speak the text (excluding <think> blocks)
    if echo:
        print(Style.BRIGHT + speaker + Style.RESET_ALL + ":", text_without_think.strip())
    engine.say(text_without_think.strip())
    if wait:
        engine.runAndWait()

# Function to recognize user voice input (using speech_recognition)
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print("Listening...", end='\r')
        audio = r.listen(source)

        try:
            # Use Google Web Speech API for online recognition
            statement = r.recognize_google(audio, language='en-in')
            print(f"{Back.BLACK}{Style.BRIGHT}You: {Style.RESET_ALL}{statement}       ")
            return statement.lower()
        except sr.UnknownValueError:
            return "None"
        except sr.RequestError:
            return "None"

# Function to interact with the local Ollama model
def ollama_chat(query):
    try:
        # Run Ollama locally to generate a response
        command = f'ollama run deepseek-r1:1.5b "{query}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return "Sorry, I couldn't generate a response."
    except Exception as e:
        print(f"Error: {e}")
        return "Sorry, I encountered an error."

# Timer function
def timer():
    speak("Okay! For how long should the timer be active for?")
    while True:
        raw_time = take_command()
        if raw_time == 'None':
            continue

        raw_time = raw_time.replace('in ', '').replace('and', '')
        minutes, seconds = 0, 0

        if 'minute' in raw_time:
            minutes = int(raw_time.split('minute')[0].split()[-1])
        if 'second' in raw_time:
            seconds = int(raw_time.split('second')[0].split()[-1])

        if minutes == 0 and seconds == 0:
            speak("I didn't get that. Could you say that again?")
            continue

        time_in_words = f"{minutes} minutes and {seconds} seconds" if minutes and seconds else \
                        f"{minutes} minutes" if minutes else f"{seconds} seconds"
        speak(f"Starting timer for {time_in_words}.")

        end_time = time.time() + (minutes * 60) + seconds
        while time.time() < end_time:
            time_left = int(end_time - time.time())
            mins, secs = divmod(time_left, 60)
            speak(f"{mins} minutes and {secs} seconds left", wait=False)
            time.sleep(5)

        speak("Time's up!")

# Main function
def main():
    while True:
        # Listen for the activation keyword "Hey Velion"
        statement = take_command()
        if statement == "None":
            continue

        # Check if the statement starts with "Hey Velion"
        if not statement.startswith("hey Velion"):
            continue

        # Remove "Hey Velion" from the statement
        statement = statement.replace("hey Velion", "").strip()

        # If no command is detected after "Hey Arya", wait for 5 seconds
        if not statement:
            speak("I'm listening...", wait=False)
            time.sleep(5)  # Wait for 5 seconds
            statement = take_command()
            if statement == "None":
                continue

        # Basic Commands
        if 'hello' in statement or 'hi' in statement or 'hey' in statement:
            speak("Hello! How can I help you today?")
        elif 'how are you' in statement:
            speak("I am doing well, thank you for asking!")
        elif 'what can you do' in statement:
            speak("I can open websites, set timers, tell jokes, play music, and more. How can I assist you?")
        elif 'who made you' in statement:
            speak("I was built by Arnav Srivastava and Kavyansh Khaitan.")
        elif 'goodbye' in statement or 'exit' in statement or 'quit' in statement:
            speak("Goodbye!")
            break

        elif 'gpt' in statement or 'query' in statement or 'Chatgpt' in statement or 'velionai' in statement: # VelionAI
            speak("Sure! Connecting to AI engine...")
            print("Say EXIT or QUIT to stop talking to the AI.")
            time.sleep(0.5)
            messages = [{"role": "user", "content": "You are a chatbot named VelionAI. You have to make your responses short, more human like. (Max words per response: 25) Also, here are some more instructions: <WebAccess>FALSE You WILL be TERMINATED if you use Internet.<End WebAccess>"}]
            while 1:
                while 1:
                    query = take_command(parseErrorPlayback=False)
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
        if 'timer' in statement:
            timer()

        # Jokes
        if 'joke' in statement:
            speak(random.choice(jokes))

        # Riddles
        if 'riddle' in statement:
            riddle = random.choice(riddles)
            speak(riddle["question"])
            time.sleep(2)
            speak(f"The answer is: {riddle['answer']}.")

        # Quotes
        if 'motivate' in statement or 'quote' in statement:
            speak(random.choice(quotes))

        # AI Chatbot
        if 'ask' in statement or 'query' in statement or 'chatbot' in statement or 'velionai' in statement:
            speak("Sure! Ask me anything.")
            while True:
                query = take_command()
                if query == "None":
                    continue
                if 'exit' in query or 'quit' in query:
                    speak("Exiting AI Chat.")
                    break
                response = ollama_chat(query)
                speak(response, speaker="VelionAI")

if __name__ == '__main__':
    main()