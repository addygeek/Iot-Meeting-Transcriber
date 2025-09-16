import sys
import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

# Load Model
model = Model("vosk-model-small-en-us-0.15")  # path to your model
rec = KaldiRecognizer(model, 16000)

# Start Recording
with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
    print("Listening... Press Ctrl+C to stop.")
    while True:
        data = q.get()
        if rec.AcceptWaveform(data):
            print(json.loads(rec.Result()))
        else:
            print(json.loads(rec.PartialResult()))
