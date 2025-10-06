# stt_vosk.py
import sounddevice as sd
import queue
import json
import threading
from vosk import Model, KaldiRecognizer
import numpy as np

class WakeSleepVosk:
    def __init__(self, model_path="vosk-model-en-in-0.5", samplerate=16000, chunk_size=8000):
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, samplerate)
        self.q = queue.Queue()
        self.master_transcript = []   # all text from start
        self.session_buffer = []      # text only for current active session
        self.active = False           # whether STT is actively sending
        self.running = False
        self.samplerate = samplerate
        self.chunk_size = chunk_size
        self.stream = None

        # Wake/sleep words
        self.wake_words = ["hi", "hey", "hai"]
        self.sleep_words = ["bye", "by", "goodbye"]

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(f"Audio status: {status}")
        self.q.put((indata * 32767).astype(np.int16).tobytes())

    def start_stream(self):
        self.running = True
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=1,
            dtype="float32",
            callback=self.audio_callback,
            blocksize=self.chunk_size
        )
        self.stream.start()
        threading.Thread(target=self.listener_loop, daemon=True).start()
        print("Microphone stream started...")

    def stop_stream(self):
        self.running = False
        if self.stream:
            self.stream.stop()
            self.stream.close()

    def listener_loop(self):
        print("Listener loop started...")
        while self.running:
            if not self.q.empty():
                data = self.q.get()
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").lower().strip()
                    if not text:
                        continue
                    tokens = text.replace(".", "").replace(",", "").split()

                    # Detect wake word
                    if any(word in tokens for word in self.wake_words):
                        if not self.active:
                            print(f"Wake word detected ({tokens}) -> Transcription resumed.")
                            self.active = True
                        continue

                    # Detect sleep word
                    if any(word in tokens for word in self.sleep_words):
                        if self.active:
                            print(f"Sleep word detected ({tokens}) -> Transcription paused.")
                            self.active = False
                        continue

                    # Handle active or inactive state
                    if self.active:
                        self.session_buffer.append(text)
                        self.master_transcript.append(text)
                        print("Transcript:", text)
                    else:
                        # Still listen silently (ignore until next wake word)
                        print("(Silenced) Heard:", text)

    def get_transcripts(self):
        """Return only new session transcripts since last poll."""
        if self.session_buffer:
            buffer_copy = self.session_buffer[:]
            self.session_buffer = []
            return buffer_copy
        return []

    def get_full_transcript(self):
        """Return full conversation history."""
        return " ".join(self.master_transcript)

    def terminate(self):
        self.stop_stream()
