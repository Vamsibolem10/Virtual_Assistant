# Jarvis AI Desktop Voice Assistant

Jarvis is a Python-powered desktop AI assistant that responds to your voice commands and performs a wide range of tasks including application control, email handling, voice authentication, weather/news updates, and more — all hands-free.

## Features

- Voice-controlled assistant with wake word: "Hey Jarvis"
- Voice authentication using MFCC + Cosine Similarity
- Read and send emails via voice
- Get real-time weather updates
- Read top news headlines
- Take notes and read saved notes
- Set alarms and check time/date/calendar
- Take screenshots and webcam photos
- Google search and file finder
- Read PDFs aloud
- Check battery status
- Ask AI anything (uses OpenAI GPT API)
- Tell jokes and riddles
- Math quiz game
- Memory-safe: only voice-authenticated users can access

## Tech Stack

- Python 3.8+
- OpenAI GPT-3.5-Turbo
- SpeechRecognition + pyttsx3
- SoundDevice + Librosa + Scikit-learn (Voice Recognition)
- PyAutoGUI, OS, subprocess
- imaplib, smtplib (Email Services)
- OpenWeatherMap & NewsAPI
- OpenCV for webcam access

## Setup Instructions

# Install Dependencies
pip install -r requirements.txt

# Add your Credential's
openai.api_key = "YOUR_OPENAI_KEY"
weather_api_key = "YOUR_OPENWEATHER_KEY"
news_api_key = "YOUR_NEWSAPI_KEY"
gmail_user = "your_email"
gmail_password = "your_gmail_app_password"
 
# Enroll your voice
python enroll_voice.py

# Run Jarvis
python ai_assistant_advanced_updated.py
