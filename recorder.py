import serial
import tkinter as tk
import pandas as pd
import threading
import time
import random
from urllib.request import urlopen
from PIL import Image, ImageTk

# ---- CONFIG ----
SERIAL_PORT = "COM3"  # Change based on your setup
BAUD_RATE = 115200
USE_SIMULATION = True  # Set to False if using real Arduino

# ---- VARIABLES ----
recording = False
data = []
gesture_name = "Hello"
uid = ""

sentences = ["Hello", "Yes", "No", "Thank you", "I need help", "Goodbye", "Sorry", "Stop", "Come here", "Wait"]
sentence_index = 0

# Image URLs for each gesture
image_urls = {
    "Hello": "https://res.cloudinary.com/spiralyze/image/upload/f_auto,w_auto/BabySignLanguage/DictionaryPages/hello-flash-card-jpg.jpeg/",
    "Yes": "https://www.lifeprint.com/asl101/pages-signs/y/yes.htm",
    "No": "https://www.lifeprint.com/asl101/pages-signs/n/no.htm",
    "Thank you": "https://www.lifeprint.com/asl101/pages-signs/t/thank-you.htm",
    "I need help": "https://www.lifeprint.com/asl101/pages-signs/h/help.htm",
    "Goodbye": "https://www.babysignlanguage.com/dictionary/b/bye-bye/?v=7516fd43adaa",
    "Sorry": "https://www.lifeprint.com/asl101/pages-signs/s/sorry.htm",
    "Stop": "https://mavink.com/explore/Stop-Sign-Language",
    "Come here": "https://www.howdoyousign.com/american-sign-language-dictionary/come%20here",
    "Wait": "https://www.lifeprint.com/asl101/pages-signs/w/wait.htm"
}

# ---- CSV FILE ----
CSV_FILE = "gesture_data.csv"
columns = ["UID", "Gesture", "Flex1", "Flex2", "Flex3", "Flex4", "Flex5", "GyroX", "GyroY", "GyroZ"]

# ---- SERIAL READING ----
if not USE_SIMULATION:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

def generate_fake_data():
    """Simulates flex sensor and gyroscope data."""
    return f"FLEX,{random.randint(200, 800)},{random.randint(200, 800)},{random.randint(200, 800)},{random.randint(200, 800)},{random.randint(200, 800)},GYRO,{random.uniform(-1, 1):.2f},{random.uniform(-1, 1):.2f},{random.uniform(-1, 1):.2f}"

def read_serial():
    """Reads real or simulated serial data."""
    global recording, data
    while True:
        if recording:
            if USE_SIMULATION:
                line = generate_fake_data()
            else:
                line = ser.readline().decode('utf-8').strip()
            
            if line.startswith("FLEX"):
                data.append(line)
                print(line)  # Debugging
        time.sleep(0.1)

# ---- CSV SAVING ----
def save_to_csv():
    global data, uid, gesture_name
    if not data or not uid:
        return

    df = pd.DataFrame([x.split(",")[1:] for x in data], columns=columns[2:])
    df.insert(0, "UID", uid)
    df.insert(1, "Gesture", gesture_name)

    try:
        existing_df = pd.read_csv(CSV_FILE)
        df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        pass  # No existing file, create new one

    df.to_csv(CSV_FILE, index=False)
    print(f"Data saved for {gesture_name} (UID: {uid})")

# ---- UI FUNCTIONS ----
def start_recording(event=None):
    global recording, data
    data = []
    recording = True
    status_label.config(text="Recording...")

def stop_recording(event=None):
    global recording
    recording = False
    status_label.config(text=f"Stopped. {len(data)} entries captured.")
    save_to_csv()

def next_sentence():
    global sentence_index, gesture_name
    sentence_index = (sentence_index + 1) % len(sentences)
    gesture_name = sentences[sentence_index]
    sentence_label.config(text=f"Gesture: {gesture_name}")
    fetch_image(gesture_name)

def set_uid():
    global uid
    uid = uid_entry.get().strip()
    if uid:
        status_label.config(text=f"UID set: {uid}")

# ---- IMAGE FETCHING ----
def fetch_image(gesture):
    try:
        url = image_urls.get(gesture, "")
        if url:
            img = Image.open(urlopen(url))
            img = img.resize((150, 150))
            img = ImageTk.PhotoImage(img)
            image_label.config(image=img)
            image_label.image = img
        else:
            image_label.config(text="No Image Found")
    except:
        image_label.config(text="No Image Found")

# ---- UI SETUP ----
root = tk.Tk()
root.title("Gesture Recorder")
root.geometry("400x500")

# UID Entry
tk.Label(root, text="Enter UID:", font=("Arial", 14)).pack()
uid_entry = tk.Entry(root, font=("Arial", 14))
uid_entry.pack()
tk.Button(root, text="Set UID", command=set_uid).pack()

# Gesture Selection
sentence_label = tk.Label(root, text=f"Gesture: {gesture_name}", font=("Arial", 18))
sentence_label.pack(pady=10)
btn_next = tk.Button(root, text="Next Gesture", command=next_sentence)
btn_next.pack(pady=5)

# Image Display
image_label = tk.Label(root, text="Fetching image...", font=("Arial", 12))
image_label.pack()
fetch_image(gesture_name)

# Recording Controls
btn_start = tk.Button(root, text="Start Recording", command=start_recording)
btn_start.pack(pady=5)
btn_stop = tk.Button(root, text="Stop Recording", command=stop_recording)
btn_stop.pack(pady=5)
status_label = tk.Label(root, text="Waiting...", font=("Arial", 14))
status_label.pack(pady=10)

# Key Bindings
root.bind("<Return>", start_recording)
root.bind("<Escape>", stop_recording)

# Start serial thread
thread = threading.Thread(target=read_serial, daemon=True)
thread.start()

root.mainloop()
