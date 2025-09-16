import os
import wave
import json
import numpy as np
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
from scipy.signal import butter, lfilter

# ---------------------------
# CONFIGURATION
# ---------------------------
MODEL_PATH = r"D:\vosk-model-small-en-us-0.15"  # change to your model path
AUDIO_PATH = "iot1.wav"  # your noisy audio
OUTPUT_FOLDER = "transcriptions"

# ---------------------------
# FUNCTION: Noise Reduction (High-pass filter)
# ---------------------------
def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def highpass_filter(data, cutoff=100, fs=16000, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

# ---------------------------
# LOAD AND PREPROCESS AUDIO
# ---------------------------
# Convert to mono 16kHz WAV using pydub
audio = AudioSegment.from_file(AUDIO_PATH)
audio = audio.set_channels(1).set_frame_rate(16000)
preprocessed_path = "preprocessed.wav"
audio.export(preprocessed_path, format="wav")

# Open WAV
wf = wave.open(preprocessed_path, "rb")

# Read all frames
frames = wf.readframes(wf.getnframes())
audio_data = np.frombuffer(frames, dtype=np.int16)

# Apply high-pass filter to remove low-frequency noise
filtered_data = highpass_filter(audio_data)
filtered_data = filtered_data.astype(np.int16)

# Save filtered audio back to WAV
with wave.open(preprocessed_path, 'wb') as wf_f:
    wf_f.setnchannels(1)
    wf_f.setsampwidth(2)
    wf_f.setframerate(16000)
    wf_f.writeframes(filtered_data.tobytes())

# ---------------------------
# LOAD MODEL
# ---------------------------
if not os.path.exists(MODEL_PATH):
    raise Exception(f"Model not found at {MODEL_PATH}")
model = Model(MODEL_PATH)

# ---------------------------
# TRANSCRIPTION
# ---------------------------
wf = wave.open(preprocessed_path, "rb")
rec = KaldiRecognizer(model, wf.getframerate())

transcript = ""
while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        transcript += result['text'] + " "
    else:
        partial = json.loads(rec.PartialResult())

final_result = json.loads(rec.FinalResult())
transcript += final_result['text']

# ---------------------------
# SAVE TRANSCRIPT
# ---------------------------
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

base_name = "transcript"
file_ext = ".txt"
file_index = 1
output_file = os.path.join(OUTPUT_FOLDER, f"{base_name}{file_ext}")
while os.path.exists(output_file):
    output_file = os.path.join(OUTPUT_FOLDER, f"{base_name}_{file_index}{file_ext}")
    file_index += 1

with open(output_file, "w", encoding="utf-8") as f:
    f.write(transcript.strip())

print(f"Transcription saved to {output_file}")
