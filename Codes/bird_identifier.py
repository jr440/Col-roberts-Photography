import sounddevice as sd
import numpy as np
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from datetime import datetime
import scipy.io.wavfile as wav
import os

# --- Settings ---
RECORD_SECONDS = 5        # Duration of each recording clip
SAMPLE_RATE = 48000       # 48kHz sample rate (required by BirdNET)
WAVE_OUTPUT_FILENAME = "temp_recording.wav"

# Set location to Kununurra for more accurate results
LAT = -15.77 
LON = 128.74

def list_audio_devices():
    print("\nAvailable audio input devices:")
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"{i}: {device['name']}")
def log_detection(detection):
    with open("bird_detections.csv", "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp},{detection['common_name']},{detection['confidence']}\n")
def record_audio():
    """Records a short audio clip from the microphone using sounddevice."""
    print("🎙️  Recording for", RECORD_SECONDS, "seconds...")
    
    # Record audio from the default microphone
    recording_data = sd.rec(int(RECORD_SECONDS * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    
    print("✅ Recording finished.")
    
    # Save the recorded data as a WAV file
    wav.write(WAVE_OUTPUT_FILENAME, SAMPLE_RATE, recording_data)

def identify_birds():
    """Analyzes the recorded audio file using BirdNET."""
    try:
        analyzer = Analyzer()
        recording = Recording(
            analyzer,
            WAVE_OUTPUT_FILENAME,
            lat=LAT,
            lon=LON,
            date=datetime.now(),
            min_conf=0.3, # Minimum confidence to report a detection
        )
        recording.analyze()

        if recording.detections:
            print("\n--- 🐦 Bird Detections ---")
            for d in recording.detections:
                print(f"{d['common_name']}: {round(d['confidence'] * 100, 2)}% confidence")
                log_detection(d)
            print("------------------------\n")
        else:
            print("\nNo birds identified in the last clip.\n")

    except Exception as e:
        print(f"An error occurred during analysis: {e}")

    # After identification is complete
    if os.path.exists(WAVE_OUTPUT_FILENAME):
        os.remove(WAVE_OUTPUT_FILENAME)
# --- Main Loop ---
if __name__ == "__main__":
    try:
        list_audio_devices()
        while True:
            record_audio()
            identify_birds()
    except KeyboardInterrupt:
        print("\nExiting program.")
