import sounddevice as sd
import queue
import json
import threading
import numpy as np
from vosk import Model, KaldiRecognizer
import time

class WakeSleepVosk:
    def __init__(self, model_path="vosk-model-en-in-0.5", samplerate=16000, chunk_size=8000):
        self.model_path = model_path
        self.model = None
        self.recognizer = None
        self.q = queue.Queue()
        self.transcript_buffer = []
        self.active = False
        self.running = False
        self.samplerate = samplerate
        self.chunk_size = chunk_size
        self.stream = None

        # Wake listener (always on)
        self.wake_model = Model(model_path)
        self.wake_recognizer = KaldiRecognizer(self.wake_model, samplerate)
        self.wake_words = ["hi", "hey", "hai"]
        self.sleep_words = ["bye", "goodbye", "by"]

    # ---------------- AUDIO INPUT ---------------- #
    def audio_callback(self, indata, frames, time, status):
        if status:
            print(f"Audio status: {status}")
        self.q.put((indata * 32767).astype(np.int16).tobytes())

    # ---------------- MAIN STREAM ---------------- #
    def start_listener(self):
        """Start continuous audio stream for both wake and STT listening."""
        if self.running:
            return
        self.running = True
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=1,
            dtype="float32",
            callback=self.audio_callback,
            blocksize=self.chunk_size,
        )
        self.stream.start()
        threading.Thread(target=self.loop, daemon=True).start()
        print("Microphone stream started...")

    # ---------------- LOOP LOGIC ---------------- #
    def loop(self):
        """Unified loop handling both wake detection and conditional STT."""
        print("Listener loop started...")
        while self.running:
            if self.q.empty():
                time.sleep(0.05)
                continue

            data = self.q.get()

            # If inactive, only listen for wake word
            if not self.active:
                if self.wake_recognizer.AcceptWaveform(data):
                    result = json.loads(self.wake_recognizer.Result())
                    text = result.get("text", "").lower()
                    if any(w in text.split() for w in self.wake_words):
                        print("Wake word detected:", text)
                        self.activate_stt()
                continue

            # If active, run full STT recognizer
            if self.recognizer and self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                text = result.get("text", "").lower()
                if not text:
                    continue

                tokens = text.replace(".", "").split()

                # Detect sleep command
                if any(w in tokens for w in self.sleep_words):
                    print("Sleep word detected:", text)
                    self.deactivate_stt()
                    continue

                self.transcript_buffer.append(text)
                print("Transcript:", text)

    # ---------------- STATE CONTROL ---------------- #
    def activate_stt(self):
        """Start or resume the main STT model dynamically."""
        if not self.model:
            print("Loading main Vosk model...")
            self.model = Model(self.model_path)
            self.recognizer = KaldiRecognizer(self.model, self.samplerate)
        self.active = True
        print("STT Activated ✅")

    def deactivate_stt(self):
        """Unload STT to save resources."""
        self.active = False
        self.recognizer = None
        self.model = None
        print("STT Deactivated 💤")

    def get_transcripts(self):
        if self.transcript_buffer:
            temp = self.transcript_buffer[:]
            self.transcript_buffer = []
            return temp
        return []

    def stop(self):
        self.running = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
