import wave
import json
from vosk import Model, KaldiRecognizer

model = Model("vosk-model-small-en-us-0.15")
wf = wave.open("iot1.wav", "rb")

rec = KaldiRecognizer(model, wf.getframerate())

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        print(json.loads(rec.Result()))
print(json.loads(rec.FinalResult()))
