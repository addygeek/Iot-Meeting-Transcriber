import wave
import json
import os
from vosk import Model, KaldiRecognizer

# ---------------------------
# CONFIGURATION
# ---------------------------
# MODEL_PATH = r"vosk-model-small-en-us-0.15" #small 46mb model
MODEL_PATH = r"vosk-model-en-us-0.22-lgraph"  #medum 128 mb model

AUDIO_PATH = "iot1.wav"
OUTPUT_FOLDER = "transcriptions" 

# ---------------------------
# CHECK MODEL
# ---------------------------
if not os.path.exists(MODEL_PATH):
    raise Exception(f"Model folder not found at {MODEL_PATH}. Please check the path!")

print("Loading Vosk model...")
model = Model(MODEL_PATH)
print("Model loaded successfully!")

# ---------------------------
# OPEN AUDIO FILE
# ---------------------------
if not os.path.exists(AUDIO_PATH):
    raise Exception(f"Audio file not found at {AUDIO_PATH}")

wf = wave.open(AUDIO_PATH, "rb")

# Ensure WAV file is mono PCM
if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
    raise Exception("Audio file must be WAV format, mono channel, 16-bit PCM")

# ---------------------------
# CREATE RECOGNIZER
# ---------------------------
rec = KaldiRecognizer(model, wf.getframerate())

# ---------------------------
# TRANSCRIPTION
# ---------------------------
transcript = ""  # Store full transcript
print("Starting transcription...")

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break

    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        print(result['text'])
        transcript += result['text'] + " "
    else:
        partial = json.loads(rec.PartialResult())
        print(f"Partial: {partial['partial']}")

final_result = json.loads(rec.FinalResult())
print("Final:", final_result['text'])
transcript += final_result['text']

# ---------------------------
# CREATE OUTPUT FOLDER
# ---------------------------
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# ---------------------------
# DETERMINE FILE NAME
# ---------------------------
base_name = "transcript"
file_ext = ".txt"
file_index = 1
output_file = os.path.join(OUTPUT_FOLDER, f"{base_name}{file_ext}")

# If file exists, increment number
while os.path.exists(output_file):
    output_file = os.path.join(OUTPUT_FOLDER, f"{base_name}_{file_index}{file_ext}")
    file_index += 1

# ---------------------------
# SAVE TRANSCRIPT
# ---------------------------
with open(output_file, "w", encoding="utf-8") as f:
    f.write(transcript.strip())

print(f"\nTranscription saved to {output_file}")
