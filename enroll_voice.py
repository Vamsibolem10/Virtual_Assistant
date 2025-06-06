
import sounddevice as sd
import numpy as np
import librosa
import pickle

DURATION = 4  # seconds

def record_voice():
    print("Recording your voice for enrollment...")
    recording = sd.rec(int(DURATION * 44100), samplerate=44100, channels=1)
    sd.wait()
    audio = np.squeeze(recording)
    return audio

def extract_features(audio):
    mfcc = librosa.feature.mfcc(y=audio, sr=44100, n_mfcc=13)
    return np.mean(mfcc.T, axis=0)

if __name__ == "__main__":
    audio = record_voice()
    features = extract_features(audio)
    with open("voiceprint.pkl", "wb") as f:
        pickle.dump(features, f)
    print("Voice enrolled successfully.")
