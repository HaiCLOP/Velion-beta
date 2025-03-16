import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import time
import requests
from googletrans import Translator
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

website_maps = [
    ['YouTube', 'https://youtube.com'],
    ['Google', 'https://google.com'],
    ['Gmail', 'https://mail.google.com'],
    ['Stack Overflow', 'https://stackoverflow.com'],
    ['Chat GPT', 'https://chatgpt.com'],
    ['GitHub', 'https://github.com/HaiCLOP/Velion-Assistant'],
    ['School', 'https://www.dpsdibrugarh.org'],
    ['Facebook', 'https://www.facebook.com'],
    ['Internet Archive', 'https://archive.org'],
    ['Wayback Machine', 'http://web.archive.org'],
    ['QR code generator', 'https://new.express.adobe.com/tools/generate-qr-code'],
    ['Adobe', 'https://www.adobe.com'],
    ['Instagram', 'https://www.instagram.com'],
    ['Reddit', 'https://www.reddit.com'],
    ['Twitter', 'https://twitter.com'],
    ['LinkedIn', 'https://www.linkedin.com'],
    ['Pinterest', 'https://www.pinterest.com'],
    ['Snapchat', 'https://www.snapchat.com'],
    ['WhatsApp', 'https://www.whatsapp.com'],
    ['TikTok', 'https://www.tiktok.com'],
    ['Spotify', 'https://www.spotify.com'],
    ['Amazon', 'https://www.amazon.com'],
    ['eBay', 'https://www.ebay.com'],
    ['Netflix', 'https://www.netflix.com'],
    ['Wikipedia', 'https://www.wikipedia.org'],
    ['IMDB', 'https://www.imdb.com'],
    ['BBC', 'https://www.bbc.com'],
    ['CNN', 'https://www.cnn.com'],
    ['NY Times', 'https://www.nytimes.com'],
    ['Wired', 'https://www.wired.com'],
    ['Medium', 'https://medium.com'],
    ['Quora', 'https://www.quora.com'],
    ['Hacker News', 'https://news.ycombinator.com'],
    ['GitLab', 'https://gitlab.com'],
    ['Bitbucket', 'https://bitbucket.org'],
    ['CodePen', 'https://codepen.io'],
    ['JSFiddle', 'https://jsfiddle.net'],
    ['Jira', 'https://www.atlassian.com/software/jira'],
    ['Trello', 'https://trello.com'],
    ['Slack', 'https://slack.com'],
    ['Zoom', 'https://zoom.us'],
    ['Discord', 'https://discord.com'],
    ['Vimeo', 'https://vimeo.com'],
    ['Portfoilo', 'https://arnav-srivastava-portfolio.vercel.app'],
    ['Website', 'https://velion-assistant.vercel.app/'],
    ['Documentation', 'https://velion-assistant.vercel.app/docs'],
]




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

        elif 'convert' in statement:
            convert_currency(statement)

        elif statement.startswith("play "):
            song_query = statement.replace("play ", "").strip()
            play_music_on_spotify(song_query)
            continue

        opened_website = False
        # Website mappings
        for kw, url in website_maps:
            if "open "+kw.lower() in statement:
                speak(f"Opening {kw}", wait=False)
                webbrowser.open_new_tab(url)
                opened_website = True
        if opened_website: continue


        if 'how are you' in statement or 'how r u' in statement:
            speak("I am doing well, thank you for asking!")

        elif 'purpose' in statement:
            speak("I am a voice assistant designed to assist you with various tasks and answer your questions")
        elif 'develop' in statement:
            speak("I was developed by Arnav Srivastava and Kavyansh Khaitan of class 8 of Delhi Public School Dibrugarh")

        # Weather functionality using WeatherAPI
        elif "weather" in statement:
            api_key = "caddc69f50ea4a08bd5152014241004"  
            base_url = "http://api.weatherapi.com/v1/current.json?"

            speak("Please tell me the name of a place.")
            while True:
                city_name = takeCommand(parseErrorPlayback = False)
                if city_name != "None": break
                speak("Could you repeat that please?")
            
            complete_url = f"{base_url}key={api_key}&q={city_name}"
            response = requests.get(complete_url)
            x = response.json()
            if "error" not in x:
                current_temperature = x['current']['temp_c']
                current_humidity = x['current']['humidity']
                weather_description = x['current']['condition']['text']
                speak(f"The temperature in {city_name} is {current_temperature} degrees Celsius with {weather_description} and humidity at {current_humidity} percent.")
            else:
                speak("City not found.")

        elif 'hello' in statement or 'hi' in statement or 'hey' in statement or 'hola' in statement or 'namaste' in statement or 'bonjour' in statement:
            speak ("Hello User!, How can I help you today?")
        
        elif "translate" in statement:
            translator = Translator()
            
            speak("Please say the text you want to translate.")
            while True:
                text_to_translate = takeCommand(parseErrorPlayback=False)
                if text_to_translate != "None": 
                    break
                speak("Could you repeat that please?")
            
            speak("Which language do you want to translate to?")
            while True:
                target_language = takeCommand(parseErrorPlayback=False)
                if target_language != "None": 
                    break
                speak("Could you repeat that please?")

            try:
                language_codes = {
                    "afrikaans": "af", "albanian": "sq", "arabic": "ar", "armenian": "hy",
                    "azerbaijani": "az", "basque": "eu", "belarusian": "be", "bengali": "bn",
                    "bosnian": "bs", "bulgarian": "bg", "catalan": "ca", "cebuano": "ceb",
                    "chinese": "zh-cn", "croatian": "hr", "czech": "cs", "danish": "da",
                    "dutch": "nl", "english": "en", "esperanto": "eo", "estonian": "et",
                    "finnish": "fi", "french": "fr", "galician": "gl", "georgian": "ka",
                    "german": "de", "greek": "el", "gujarati": "gu", "haitian creole": "ht",
                    "hebrew": "iw", "hindi": "hi", "hungarian": "hu", "icelandic": "is",
                    "indonesian": "id", "irish": "ga", "italian": "it", "japanese": "ja",
                    "javanese": "jw", "kannada": "kn", "kazakh": "kk", "khmer": "km",
                    "korean": "ko", "kurdish (kurmanji)": "ku", "kyrgyz": "ky", "lao": "lo",
                    "latin": "la", "latvian": "lv", "lithuanian": "lt", "luxembourgish": "lb",
                    "macedonian": "mk", "malagasy": "mg", "malay": "ms", "malayalam": "ml",
                    "maltese": "mt", "marathi": "mr", "mongolian": "mn", "myanmar (burmese)": "my",
                    "nepali": "ne", "norwegian": "no", "persian": "fa", "polish": "pl",
                    "portuguese": "pt", "punjabi": "pa", "romanian": "ro", "russian": "ru",
                    "samoan": "sm", "scottish gaelic": "gd", "serbian": "sr", "sesotho": "st",
                    "shona": "sn", "sindhi": "sd", "sinhala": "si", "slovak": "sk",
                    "slovenian": "sl", "somali": "so", "spanish": "es", "sundanese": "su",
                    "swahili": "sw", "swedish": "sv", "tagalog": "tl", "tajik": "tg",
                    "tamil": "ta", "tatar": "tt", "telugu": "te", "thai": "th",
                    "turkish": "tr", "turkmen": "tk", "ukrainian": "uk", "urdu": "ur",
                    "uzbek": "uz", "vietnamese": "vi", "welsh": "cy", "xhosa": "xh",
                    "yiddish": "yi", "yoruba": "yo", "zulu": "zu"
                }
                
                if target_language.lower() in language_codes:
                    target_lang_code = language_codes[target_language.lower()]
                    translated_text = translator.translate(text_to_translate, dest=target_lang_code).text
                    speak(f"The translated text in {target_language} is: {translated_text}")
                else:
                    speak("Sorry, I couldn't recognize that language.")
            except Exception as e:
                speak("I encountered an error while translating.")
                print(e)



        trivia_questions = [
            {"question": "What is the capital of France?", "answer": "Paris"},
            {"question": "What is the largest planet in our solar system?", "answer": "Jupiter"},
            {"question": "Who wrote 'Romeo and Juliet'?", "answer": "William Shakespeare"},
            {"question": "What is the chemical symbol for gold?", "answer": "Au"},
            {"question": "Which planet is known as the Red Planet?", "answer": "Mars"},
            {"question": "How many continents are there?", "answer": "Seven"},
            {"question": "What is the smallest country in the world?", "answer": "Vatican City"},
            {"question": "What year did the Titanic sink?", "answer": "1912"},
            {"question": "What is the hardest natural substance on Earth?", "answer": "Diamond"},
            {"question": "Who painted the Mona Lisa?", "answer": "Leonardo da Vinci"},
            {"question": "What is the longest river in the world?", "answer": "Nile"},
            {"question": "Who discovered penicillin?", "answer": "Alexander Fleming"},
            {"question": "What is the largest mammal in the world?", "answer": "Blue Whale"},
            {"question": "What is the capital of Japan?", "answer": "Tokyo"},
            {"question": "What is the main ingredient in sushi?", "answer": "Rice"},
            {"question": "How many players are there in a soccer team?", "answer": "Eleven"},
            {"question": "Which element has the atomic number 1?", "answer": "Hydrogen"},
            {"question": "What is the capital of Australia?", "answer": "Canberra"},
            {"question": "What is the tallest mountain in the world?", "answer": "Mount Everest"},
            {"question": "Who invented the telephone?", "answer": "Alexander Graham Bell"},
            {"question": "What is the currency of the United States?", "answer": "Dollar"},
            {"question": "What is the square root of 100?", "answer": "10"},
            {"question": "What is the hardest rock?", "answer": "Diamond"},
            {"question": "Which planet is known for its rings?", "answer": "Saturn"},
            {"question": "What is the main language spoken in Brazil?", "answer": "Portuguese"},
            {"question": "Who was the first President of the United States?", "answer": "George Washington"},
            {"question": "What is the capital of Canada?", "answer": "Ottawa"},
            {"question": "What is the largest desert in the world?", "answer": "Sahara"},
            {"question": "What is the freezing point of water?", "answer": "0 degrees Celsius"},
            {"question": "What is the largest bone in the human body?", "answer": "Femur"},
            {"question": "Who wrote the 'Iliad'?", "answer": "Homer"},
            {"question": "What is the chemical formula for table salt?", "answer": "NaCl"},
            {"question": "What is the most widely spoken language in the world?", "answer": "Mandarin Chinese"},
            {"question": "Which animal is known as the 'King of the Jungle'?", "answer": "Lion"},
            {"question": "What is the capital of Italy?", "answer": "Rome"},
            {"question": "What is the speed of light?", "answer": "299,792 kilometers per second"},
            {"question": "Which gas do plants absorb from the atmosphere?", "answer": "Carbon Dioxide"},
            {"question": "What is the largest organ in the human body?", "answer": "Skin"},
            {"question": "Who painted the ceiling of the Sistine Chapel?", "answer": "Michelangelo"},
            {"question": "What is the capital of Germany?", "answer": "Berlin"},
            {"question": "What is the most populated country in the world?", "answer": "China"},
            {"question": "What is the currency of Japan?", "answer": "Yen"},
            {"question": "Which planet is closest to the Sun?", "answer": "Mercury"},
            {"question": "What is the most abundant gas in the Earth's atmosphere?", "answer": "Nitrogen"},
            {"question": "Who is known as the 'Father of Computers'?", "answer": "Charles Babbage"},
            {"question": "What is the main ingredient in chocolate?", "answer": "Cocoa"},
            {"question": "What is the tallest building in the world?", "answer": "Burj Khalifa"},
            {"question": "Who discovered gravity?", "answer": "Isaac Newton"},
            {"question": "What is the capital of Spain?", "answer": "Madrid"},
            {"question": "What is the fastest land animal?", "answer": "Cheetah"},
            {"question": "Which ocean is the largest?", "answer": "Pacific Ocean"},
            {"question": "What is the chemical symbol for silver?", "answer": "Ag"},
            {"question": "How many teeth does an adult human have?", "answer": "32"},
            {"question": "What is the capital of India?", "answer": "New Delhi"},
            {"question": "Which gas is most commonly used in balloons?", "answer": "Helium"},
            {"question": "What is the process of converting a liquid into a gas called?", "answer": "Evaporation"},
            {"question": "What is the hardest natural mineral?", "answer": "Diamond"},
            {"question": "What is the most widely used programming language?", "answer": "Python"},
            {"question": "What is the capital of Egypt?", "answer": "Cairo"},
            {"question": "Which animal is known for its ability to change color?", "answer": "Chameleon"},
            {"question": "What is the longest bone in the human body?", "answer": "Femur"},
            {"question": "What is the main gas in the air we breathe?", "answer": "Nitrogen"},
            {"question": "Who was the first woman to fly solo across the Atlantic?", "answer": "Amelia Earhart"},
            {"question": "What is the primary function of red blood cells?", "answer": "Transport oxygen"},
            {"question": "What is the capital of Russia?", "answer": "Moscow"},
            {"question": "What is the main ingredient in a smoothie?", "answer": "Fruit"},
            {"question": "Who wrote the 'Divine Comedy'?", "answer": "Dante Alighieri"},
            {"question": "What is the chemical formula for water?", "answer": "H2O"},
            {"question": "Which planet has the most moons?", "answer": "Jupiter"},
            {"question": "What is the capital of South Africa?", "answer": "Pretoria"},
            {"question": "What is the primary source of energy for the Earth?", "answer": "Sun"},
            {"question": "What is the largest land animal?", "answer": "Elephant"},
            {"question": "What is the capital of the United Kingdom?", "answer": "London"},
            {"question": "What is the largest continent?", "answer": "Asia"},
            {"question": "Who invented the light bulb?", "answer": "Thomas Edison"},
            {"question": "What is the main ingredient in hummus?", "answer": "Chickpeas"},
            {"question": "What is the largest volcano in the world?", "answer": "Mauna Loa"},
            {"question": "Which element has the atomic number 6?", "answer": "Carbon"},
            {"question": "What is the capital of Greece?", "answer": "Athens"},
            {"question": "What is the longest river in South America?", "answer": "Amazon"},
            {"question": "Who is the author of 'Harry Potter'?", "answer": "J.K. Rowling"},
            {"question": "What is the currency of the United Kingdom?", "answer": "Pound"},
            {"question": "What is the fastest marine animal?", "answer": "Black Marlin"},
            {"question": "What is the primary ingredient in pesto?", "answer": "Basil"},
            {"question": "Who painted 'Starry Night'?", "answer": "Vincent van Gogh"},
            {"question": "What is the capital of China?", "answer": "Beijing"},
            {"question": "What is the largest island in the world?", "answer": "Greenland"},
            {"question": "What is the most widely spoken second language in the world?", "answer": "English"},
            {"question": "What is the capital of Sweden?", "answer": "Stockholm"},
            {"question": "What is the main ingredient in pancakes?", "answer": "Flour"},
            {"question": "Which animal is known for its intelligence and problem-solving skills?", "answer": "Dolphin"},
            {"question": "What is the capital of Thailand?", "answer": "Bangkok"},
            {"question": "What is the tallest waterfall in the world?", "answer": "Angel Falls"},
            {"question": "What is the most spoken language in the world?", "answer": "Mandarin Chinese"},
            {"question": "What is the name of the fairy in Peter Pan?", "answer": "Tinkerbell"},
            {"question": "What is the primary function of the heart?", "answer": "Pump blood"},
            {"question": "What is the capital of Mexico?", "answer": "Mexico City"},
            {"question": "What is the main ingredient in a Caesar salad?", "answer": "Romaine lettuce"},
            {"question": "What is the hardest natural mineral?", "answer": "Diamond"},
            {"question": "What is the capital of Argentina?", "answer": "Buenos Aires"},
            {"question": "What is the fastest bird in the world?", "answer": "Peregrine falcon"},
            {"question": "What is the most widely consumed fruit in the world?", "answer": "Banana"},
            {"question": "What is the chemical symbol for iron?", "answer": "Fe"},
            {"question": "Who was the first man to walk on the moon?", "answer": "Neil Armstrong"},
            {"question": "What is the capital of Portugal?", "answer": "Lisbon"},
            {"question": "What is the name of the largest ocean on Earth?", "answer": "Pacific Ocean"},
            {"question": "What is the smallest planet in our solar system?", "answer": "Mercury"},
            {"question": "What is the capital of Turkey?", "answer": "Ankara"},
            {"question": "What is the main ingredient in a fruit salad?", "answer": "Fruit"},
            {"question": "Who wrote 'Pride and Prejudice'?", "answer": "Jane Austen"},
            {"question": "What is the capital of the Netherlands?", "answer": "Amsterdam"},
            {"question": "What is the largest fish in the ocean?", "answer": "Whale shark"},
            {"question": "What is the chemical symbol for oxygen?", "answer": "O"},
            {"question": "What is the capital of Australia?", "answer": "Canberra"}, 
            {"question": "What is the capital of India?", "answer": "New Delhi"},
            {"question": "What is the capital of the United States?", "answer": "Washington, D.C."},
            {"question": "What is the capital of Brazil?", "answer": "Brasília"},
            {"question": "What is the capital of Russia?", "answer": "Moscow"},
            {"question": "What is the capital of China?", "answer": "Beijing"},
            {"question": "What is the capital of Japan?", "answer": "Tokyo"},
            {"question": "What is the capital of South Korea?", "answer": "Seoul"},
            {"question": "What is the capital of South Africa?", "answer": "Pretoria"},
            {"question": "What is the capital of Nigeria?", "answer": "Abuja"},
            {"question": "What is the capital of Egypt?", "answer": "Cairo"},
            {"question": "What is the capital of France?", "answer": "Paris"},
            {"question": "What is the capital of Germany?", "answer": "Berlin"},
            {"question": "What is the capital of Italy?", "answer": "Rome"},
            {"question": "What is the capital of Spain?", "answer": "Madrid"},
            {"question": "What is the capital of the United Kingdom?", "answer": "London"},
            {"question": "What is the capital of Canada?", "answer": "Ottawa"},
            {"question": "What is the capital of Australia?", "answer": "Canberra"},
            {"question": "What is the capital of Argentina?", "answer": "Buenos Aires"},
            {"question": "What is the capital of Brazil?", "answer": "Brasília"},
            {"question": "What is the capital of Chile?", "answer": "Santiago"},
            {"question": "What is the capital of Colombia?", "answer": "Bogotá"},
            {"question": "Who Created Me?", "answer": "Arnav "},
        ]

        # Trivia game function
        def trivia_game():
            speak("Welcome to the trivia game! Let's get started. Say 'quit' or 'exit' to stop the game.")
            
            selected_questions = random.sample(trivia_questions, 10)  # Select 10 random questions
            score = 0

            for item in selected_questions:
                speak(item["question"])
                user_answer = takeCommand(parseErrorPlayback=False)  # Assume this function captures the user's answer

                # Handle no answer detected
                if user_answer is None:
                    speak("Can you repeat that?")
                    user_answer = takeCommand(parseErrorPlayback=False)  # Ask again for the answer

                # Check for exit command
                if user_answer and ("quit" in user_answer.lower() or "exit" in user_answer.lower()):
                    speak("Exiting the trivia game. Thanks for playing!")
                    break

                # Check if the answer is correct
                if user_answer and user_answer.lower() == item["answer"].lower():
                    speak("Correct!")
                    score += 1
                else:
                    speak(f"Wrong! The correct answer is {item['answer']}.")

            speak(f"Game over! You scored {score} out of {len(selected_questions)}.")

        # Example of how to call the trivia game function
        if "trivia" in statement:
            trivia_game()



        elif 'ask' in statement or 'query' in statement or 'chatbot' in statement or 'velionai' in statement: # VelionAI
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

        elif 'time' in statement and 'timer' not in statement:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"The time is {strTime}")
            speak(f"The time is {datetime.datetime.now().hour} {datetime.datetime.now().minute}", echo=False)

        elif 'who are you' in statement or 'what can you do' in statement or 'hu r u' in statement:
            speak("I am Velion, version 1.0, your personal assistant. I can open YouTube, Google Chrome, Gmail, Stack Overflow, tell you the time, search Wikipedia, get weather updates, and fetch news.")

        elif "who made you" in statement or "who created you" in statement or "who invented you" in statement:
            speak("I was built by Arnav Srivastava and Kavyansh Khaitan.")

        elif "design" in statement or "structure" in statement:
            speak("I am a simple text-based Personal assistant. My structure is based on a combination of multiple APIs and code")

        elif "languages" in statement:
            speak("I am currently limited to speak and understand English.")

        elif "umang" in statement:
            speak("Umang is a place to showcase your talent in front of the world. This mega exhibition is hosted at Delhi Public School Dibrugarh.")

        elif "delhi public school dibrugarh" in statement or "dps dibrugarh" in statement:
            speak("DPS Dibrugarh is a renowned school emphasizing academic excellence and character development. It offers a supportive environment and encourages extracurricular activities and community service.")

        elif "programming language" in statement:
            speak("Python is one of the only programming languages used in my development.")

        elif 'news' in statement:
            speak("Here are some headlines from the Times of India, happy reading", wait=False)
            webbrowser.open_new_tab("https://timesofindia.indiatimes.com/home/headlines")
            time.sleep(6)

        elif 'meaning of life' in statement:
            speak("Life is the existence of an individual human being or animal.")
        
        elif 'version' in statement:
            speak("I am based on Python 3.11, I am 1.0 version of velion")            

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

        elif 'joke' in statement:
            jokes = [
                "Why don't skeletons fight each other...? They don't have the guts!",
                "What did one ocean say to the other ocean...? Nothing, they just waved.",
                "Why don't eggs tell jokes...? Because they might crack up!",
                "How does a penguin build its house...? Igloos it together!",
                "Why did the math book look sad...? Because it had too many problems.",
                "What do you call fake spaghetti...? An impasta.",
                "Whats orange and sounds like a parrot...? A carrot!",
                "Why did the scarecrow win an award...? Because he was outstanding in his field!",
                "What do you call cheese that isn't yours...? Nacho cheese.",
                "Why did the computer go to the doctor...? It had a virus!",
                "What did one wall say to the other wall...? I'll meet you at the corner.",
                "Why can't you hear a pterodactyl go to the bathroom...? Because the “P” is silent!",
                "Why don't skeletons ever use cell phones...? They don't have the nerve.",
                "What's a skeleton's least favorite room in the house...? The living room!",
                "What did the big flower say to the little flower...? Hey, bud!"
            ]
            speak(random.choice(jokes))

        elif 'riddle' in statement:
            riddles = [
                "What has keys but can't open locks....? A piano.",
                "I speak without a mouth and hear without ears. I have no body, but I come alive with the wind. What am I....? An echo.",
                "The more of this there is, the less you see. What is it....? Darkness.",
                "What comes once in a minute, twice in a moment, but never in a thousand years....? The letter 'M.'",
                "I can be cracked, I can be made, I can be told, I can be played. What am I....? A joke.",
                "What has a heart that doesn't beat.....? An artichoke.",
                "What can travel around the world while staying in the corner....? A stamp.",
                "I'm tall when I'm young, and I'm short when I'm old. What am I....? A candle.",
                "What gets wetter the more it dries....? A towel.",
                "What can you break, even if you never pick it up or touch it....? A promise.",
                "What has a head, a tail, but no body....? A coin.",
                "What is always in front of you but can't be seen....? The future.",
                "What has a ring but no finger....? A phone.",
                "I'm not alive, but I grow; I don't have lungs, but I need air; I don't have a mouth, but water kills me. What am I....? Fire.",
                "What begins with T, ends with T, and has T in it....? A teapot."
            ]
            speak(random.choice(riddles))

        elif 'motivate' in statement or 'motivation' in statement:
            quotes = [
                "The only way to do great work is to love what you do. - Steve Jobs",
                "Success is not the key to happiness. Happiness is the key to success. - Albert Schweitzer",
                "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
                "Believe you can and you're halfway there. - Theodore Roosevelt",
                "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
                "Your limitation—it's only your imagination.",
                "Push yourself, because no one else is going to do it for you.",
                "Great things never come from comfort zones.",
                "Dream it. Wish it. Do it.",
                "Success doesn’t just find you. You have to go out and get it."
            ]
            speak(random.choice(quotes))

        elif 'book' in statement or 'recommend' in statement:
            books = [
                "The Alchemist by Paulo Coelho",
                "The Little Prince by Antoine de Saint-Exupéry",
                "To Kill a Mockingbird by Harper Lee",
                "1984 by George Orwell",
                "Harry Potter and the Philosopher's Stone by J.K. Rowling",
                "The Lord of the Rings by J.R.R. Tolkien",
                "Pride and Prejudice by Jane Austen",
                "The Great Gatsby by F. Scott Fitzgerald",
                "The Catcher in the Rye by J.D. Salinger",
                "Animal Farm by George Orwell",
                "The Hobbit by J.R.R. Tolkien",
                "The Da Vinci Code by Dan Brown",
                "The Kite Runner by Khaled Hosseini",
            ]
            speak(random.choice(books))

        elif 'timer' in statement:
            timer()

        elif 'repeat' in statement:
            speech = statement.replace('repeat', "")
            speak(speech)

        elif 'quit' in statement or 'exit' in statement or 'bye' in statement or 'goodbye' in statement or 'stop' in statement or 'shut down' in statement or 'negative' in statement or 'terminate' in statement:
            speak("Goodbye")
            exit()

        elif "meow" in statement:
            speak("Meow Meow Meow Meow Meow Meow Meow Meow!")

        elif "bark" in statement:
            speak("Woof Woof Woof Woof Woof Woof Woof Woof Woof!")

        elif "I love u" in statement or "love u" in statement or "I like u" in statement or "like u" in statement or "I adore u" in statement or "adore u" in statement:
            speak("As an AI, I am flattered. But I am here to assist you with your needs.")

        


        elif "log off" in statement or "sign out" in statement:
            speak("Ok, your PC will log off in 10 seconds. Please exit all applications.")
            print("Demo Mode: Shutdown Disabled")
            print('subprocess.call(["shutdown", "/l"])')
