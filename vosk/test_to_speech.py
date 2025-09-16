import pyttsx3
import wave

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)  # speaking speed
engine.setProperty("voice", engine.getProperty("voices")[0].id)  # default voice

# Save spoken text to WAV file
filename_tts = "iot1.wav"
engine.save_to_file("Hello, my name is Aditya, We are going to present a Iot Device that can summarize meetings and lectures and present you in summarise key points", filename_tts)
engine.runAndWait()

filename_tts
