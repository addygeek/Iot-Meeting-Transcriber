import wave
import json
import os
import time
from vosk import Model, KaldiRecognizer

# ---------------------------
# CONFIGURATION
# ---------------------------
# Choose your model here
# MODEL_PATH = r"vosk-model-small-en-us-0.15"  # small 46MB model
# MODEL_PATH = r"vosk-model-en-us-0.22-lgraph"  # medium 128MB model
# MODEL_PATH = r"vosk-model-en-in-0.5"  # active model
MODEL_PATH = r"vosk-model-small-en-in-0.4"
AUDIO_PATH = "iot1.wav"
OUTPUT_FOLDER = "transcriptions"

# ---------------------------
# CHECK MODEL
# ---------------------------
if not os.path.exists(MODEL_PATH):
    raise Exception(f"Model folder not found at {MODEL_PATH}. Please check the path!")

active_model_name = os.path.basename(MODEL_PATH)
print(f"Loading Vosk model: {active_model_name}...")
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
# START TIMER
# ---------------------------
start_time = time.time()

# ---------------------------
# TRANSCRIPTION
# ---------------------------
transcript = ""
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
# END TIMER
# ---------------------------
end_time = time.time()
time_taken = end_time - start_time

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

while os.path.exists(output_file):
    output_file = os.path.join(OUTPUT_FOLDER, f"{base_name}_{file_index}{file_ext}")
    file_index += 1

# ---------------------------
# SAVE TRANSCRIPT WITH FORMAT
# ---------------------------
with open(output_file, "w", encoding="utf-8") as f:
    f.write(f"Model used: {active_model_name}\n")
    f.write(f"Time taken: {time_taken:.2f} seconds\n\n")
    f.write("Text:\n")
    f.write(transcript.strip())

print(f"\nTranscription saved to {output_file}")
print(f"Time taken for transcription: {time_taken:.2f} seconds")
