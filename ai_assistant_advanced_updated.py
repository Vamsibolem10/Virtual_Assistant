import speech_recognition as sr
import pyttsx3
import openai
import os
import subprocess
import pyautogui
import keyboard
import requests
import time
import sounddevice as sd
import numpy as np
import librosa
import pickle
import imaplib
import email
from email.header import decode_header
import webbrowser
import psutil
import cv2
import random
import PyPDF2
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from email.mime.text import MIMEText
import smtplib

# CONFIG
openai.api_key = "API KEY"
weather_api_key = "API KEY"
news_api_key = "API KEY"
gmail_user = "MAIL ID"
gmail_password = "MAIL APP PASSWORD"

engine = pyttsx3.init()
engine.setProperty("rate", 180)

def speak(text):
    print("Jarvis:", text)
    engine.say(text)
    engine.runAndWait()

def listen_command(timeout=5):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source, timeout=timeout, phrase_time_limit=8)
    try:
        return r.recognize_google(audio).lower()
    except Exception:
        return ""

def get_ai_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response.choices[0].message.content.strip()

def open_app(name):
    try:
        os.system(f"start {name}")
    except Exception as e:
        speak(f"Could not open {name}: {str(e)}")

def close_app(name):
    try:
        os.system(f"taskkill /f /im {name}.exe")
    except Exception as e:
        speak(f"Could not close {name}: {str(e)}")

def search_google(query):
    speak("Searching Google...")
    os.system(f"start https://www.google.com/search?q={query}")

def get_weather():
    city = "Visakhapatnam"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"
    data = requests.get(url).json()
    if data.get("main"):
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        speak(f"The weather in {city} is {desc} with {temp} degrees Celsius.")
    else:
        speak("Couldn't fetch weather.")

def get_news():
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={news_api_key}"
    data = requests.get(url).json()
    articles = data.get("articles", [])[:5]
    if not articles:
        speak("No news articles found.")
        return
    for i, article in enumerate(articles):
        speak(f"News {i+1}: {article['title']}")

def take_note():
    speak("What should I note?")
    note = listen_command()
    with open("notes.txt", "a") as f:
        f.write(f"{datetime.now()}: {note}\n")
    speak("Note saved.")

def read_notes():
    if os.path.exists("notes.txt"):
        with open("notes.txt", "r") as f:
            content = f.read()
        speak("Here are your notes:")
        speak(content)
    else:
        speak("No notes found.")

def send_email():
    speak("Whom should I send the email to? Please say the full email address.")
    recipient = listen_command()

    if "@" not in recipient or "." not in recipient:
        speak("That doesn't sound like a valid email address. Please try again.")
        return

    speak("What is the subject of the email?")
    subject = listen_command()

    speak("What is the message?")
    message = listen_command()

    try:
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = gmail_user
        msg["To"] = recipient

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.send_message(msg)
        server.quit()

        speak("Email sent successfully!")
    except Exception as e:
        speak(f"Failed to send email. Error: {str(e)}")

def tell_joke():
    joke = get_ai_response("Tell me a funny joke.")
    speak(joke)

def set_alarm():
    speak("At what time? Say for example: 7 30 for 7:30.")
    alarm_time = listen_command()
    try:
        hour, minute = map(int, alarm_time.split())
        speak(f"Alarm set for {hour}:{minute}.")
        while True:
            now = datetime.now()
            if now.hour == hour and now.minute == minute:
                speak("Wake up! Alarm ringing.")
                pyautogui.alert("Alarm!", "Jarvis", timeout=5000)
                break
            time.sleep(10)
    except Exception:
        speak("Couldn't set the alarm.")

def show_time():
    now = datetime.now()
    speak(f"It is {now.strftime('%H:%M on %A, %B %d')}")

def take_screenshot():
    filename = f"screenshot_{int(time.time())}.png"
    pyautogui.screenshot(filename)
    speak(f"Screenshot saved as {filename}")

def extract_features(audio):
    mfcc = librosa.feature.mfcc(y=audio, sr=44100, n_mfcc=13)
    return np.mean(mfcc.T, axis=0)

def record_for_authentication(duration=3):
    speak("Authenticating your voice...")
    recording = sd.rec(int(duration * 44100), samplerate=44100, channels=1)
    sd.wait()
    return np.squeeze(recording)

def is_authorized_user():
    try:
        with open("voiceprint.pkl", "rb") as f:
            enrolled_features = pickle.load(f)
    except FileNotFoundError:
        speak("No enrolled voice found.")
        return False

    test_audio = record_for_authentication()
    test_features = extract_features(test_audio)

    similarity = cosine_similarity(
        [enrolled_features], [test_features]
    )[0][0]

    print(f"Voice similarity: {similarity:.2f}")
    return similarity > 0.80

def read_unread_emails():
    speak("Checking your unread emails...")
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(gmail_user, gmail_password)
        mail.select("inbox")
        status, response = mail.search(None, 'UNSEEN')
        unread_msg_nums = response[0].split()
        if not unread_msg_nums:
            speak("You have no unread emails.")
            return
        speak(f"You have {len(unread_msg_nums)} unread emails. Reading them now.")
        for e_id in unread_msg_nums[:5]:
            status, msg_data = mail.fetch(e_id, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    from_ = msg.get("From")
                    speak(f"Email from {from_}, subject: {subject}")
    except Exception as e:
        speak(f"Error reading emails: {str(e)}")

def find_files(query):
    speak(f"Searching for files matching {query} on your PC...")
    try:
        home = os.path.expanduser("~")
        matches = []
        for root, dirs, files in os.walk(home):
            for file in files:
                if query.lower() in file.lower():
                    matches.append(os.path.join(root, file))
                    if len(matches) >= 5:
                        break
            if len(matches) >= 5:
                break
        if matches:
            speak("I found these files:")
            for m in matches:
                speak(m)
        else:
            speak("No matching files found.")
    except Exception as e:
        speak(f"Error searching files: {str(e)}")

def read_pdf_text():
    speak("Please say the full path of the PDF file.")
    path = listen_command(timeout=10)
    if not os.path.isfile(path):
        speak("File does not exist.")
        return
    try:
        with open(path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            speak("Reading PDF content now.")
            speak(text[:1000])
    except Exception as e:
        speak(f"Failed to read PDF: {str(e)}")

def battery_status():
    battery = psutil.sensors_battery()
    if battery:
        percent = battery.percent
        plugged = battery.power_plugged
        status = "charging" if plugged else "not charging"
        speak(f"Battery is at {percent} percent and is currently {status}.")
    else:
        speak("Couldn't get battery status.")

def open_camera_and_take_photo():
    speak("Opening camera to take photo.")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        speak("Cannot open camera.")
        return
    ret, frame = cap.read()
    if ret:
        filename = f"photo_{int(time.time())}.png"
        cv2.imwrite(filename, frame)
        speak(f"Photo saved as {filename}")
    else:
        speak("Failed to capture photo.")
    cap.release()
    cv2.destroyAllWindows()

riddles = [
    ("What has keys but can't open locks?", "A piano"),
    ("What can travel around the world while staying in the same spot?", "A stamp"),
    ("What has hands but can't clap?", "A clock"),
]

def tell_riddle():
    riddle, answer = random.choice(riddles)
    speak(riddle)
    speak("Try to answer!")
    user_ans = listen_command(timeout=7)
    if answer.lower() in user_ans:
        speak("Correct! Well done.")
    else:
        speak(f"The answer is: {answer}")

def show_date_time_calendar():
    now = datetime.now()
    speak(f"Today is {now.strftime('%A, %B %d, %Y')}. The time is {now.strftime('%H:%M:%S')}.")

def math_quiz():
    speak("Let's start a quick math quiz. I will ask 3 questions.")
    score = 0
    for i in range(3):
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        op = random.choice(["+", "-", "*"])
        if op == "+":
            ans = a + b
        elif op == "-":
            ans = a - b
        else:
            ans = a * b
        speak(f"Question {i+1}: What is {a} {op} {b}?")
        try:
            user_ans = int(listen_command(timeout=5))
            if user_ans == ans:
                speak("Correct!")
                score += 1
            else:
                speak(f"Wrong, the answer is {ans}.")
        except Exception:
            speak(f"Could not understand your answer. The correct answer is {ans}.")
    speak(f"Quiz finished. You scored {score} out of 3.")

def perform_action(cmd):
    cmd = cmd.lower()
    if "open" in cmd:
        app_name = cmd.replace("open", "").strip()
        open_app(app_name)
    elif "close" in cmd:
        app_name = cmd.replace("close", "").strip()
        close_app(app_name)
    elif "search" in cmd:
        query = cmd.replace("search", "").strip()
        search_google(query)
    elif "weather" in cmd:
        get_weather()
    elif "news" in cmd:
        get_news()
    elif "note" in cmd:
        take_note()
    elif "read notes" in cmd:
        read_notes()
    elif "email" in cmd and "read" in cmd:
        read_unread_emails()
    elif "email" in cmd:
        send_email()
    elif "joke" in cmd:
        tell_joke()
    elif "alarm" in cmd:
        set_alarm()
    elif "time" in cmd or "date" in cmd or "calendar" in cmd:
        show_date_time_calendar()
    elif "screenshot" in cmd:
        take_screenshot()
    elif "shutdown" in cmd:
        os.system("shutdown /s /t 1")
    elif "restart" in cmd:
        os.system("shutdown /r /t 1")
    elif "type" in cmd:
        text = cmd.replace("type", "").strip()
        pyautogui.write(text)
    elif "find file" in cmd or "search file" in cmd:
        query = cmd.replace("find file", "").replace("search file", "").strip()
        find_files(query)
    elif "read pdf" in cmd:
        read_pdf_text()
    elif "battery" in cmd:
        battery_status()
    elif "take photo" in cmd or "open camera" in cmd:
        open_camera_and_take_photo()
    elif "riddle" in cmd:
        tell_riddle()
    elif "quiz" in cmd or "math quiz" in cmd:
        math_quiz()
    else:
        answer = get_ai_response(cmd)
        speak(answer)

def wake_word_listener():
    while True:
        print("Say 'Hey Jarvis' to wake me up...")
        cmd = listen_command(timeout=3)
        if "hey jarvis" in cmd:
            if is_authorized_user():
                speak("Access granted. How can I assist you?")
                while True:
                    command = listen_command()
                    if any(stop_word in command for stop_word in ["stop", "bye", "exit", "quit"]):
                        speak("Goodbye!")
                        break
                    if command.strip() == "":
                        continue
                    perform_action(command)
            else:
                speak("Access denied. Unauthorized voice.")

if __name__ == "__main__":
    speak("Jarvis AI Assistant loaded. Say 'Hey Jarvis' to start.")
    wake_word_listener()
