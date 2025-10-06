# stt_vosk.py
import sounddevice as sd
import queue
import json
import numpy as np
from vosk import Model, KaldiRecognizer
import threading

class WakeSleepVosk:
    def __init__(self, wake_word="hi", sleep_word="bye", model_path="vosk-model-en-in-0.5"):
        self.wake_word = wake_word.lower()
        self.sleep_word = sleep_word.lower()
        self.active = False
        self.running = True
        self.q = queue.Queue()

        # Load Vosk model
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.transcript_buffer = []

    def audio_callback(self, indata, frames, time, status):
        self.q.put(bytes(indata))

    def start_stream(self):
        self.stream = sd.InputStream(
            samplerate=16000,
            channels=1,
            dtype='int16',
            callback=self.audio_callback
        )
        self.stream.start()
        threading.Thread(target=self.listener_loop, daemon=True).start()

    def listener_loop(self):
        print("Listening for wake word...")
        while self.running:
            if not self.q.empty():
                data = self.q.get()
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").lower()
                    if text.strip() == "":
                        continue

                    # Wake word detection
                    if self.wake_word in text and not self.active:
                        print(f"Wake word '{self.wake_word}' detected! Starting transcription...")
                        self.active = True

                    # Sleep word detection
                    elif self.sleep_word in text and self.active:
                        print(f"Sleep word '{self.sleep_word}' detected! Stopping transcription...")
                        self.active = False

                    # Collect transcript if active
                    if self.active:
                        self.transcript_buffer.append(text)
                        print("Transcript:", text)

    def get_transcripts(self):
        buffer_copy = self.transcript_buffer.copy()
        self.transcript_buffer = []
        return buffer_copy

    def stop(self):
        self.running = False
        self.stream.stop()
        self.stream.close()
