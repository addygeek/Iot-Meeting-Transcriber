# Quick Installation Guide

## Step-by-Step Setup

### 1. Create Project Structure

```bash
# Create main directory
mkdir local_meeting_summarizer
cd local_meeting_summarizer

# Create subdirectories
mkdir configs
mkdir recordings
```

### 2. Copy Files

Place all the Python files in the `local_meeting_summarizer` directory:
- `main.py`
- `recorder.py`
- `stt_engine.py`
- `transcript_aggregator.py`
- `summarizer.py`
- `logger.py`
- `requirements.txt`

Place configuration in `configs` directory:
- `configs/recorder_config.yml`

### 3. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

**Dependencies installed:**
- pyaudio (microphone access)
- vosk (speech-to-text)
- nltk (natural language processing)
- scikit-learn (summarization)
- numpy (numerical operations)
- PyYAML (configuration)

### 4. Download Vosk Model

**Option A: Small Model (Recommended for testing)**

```bash
# Download small English model (~50MB)
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip

# Extract
unzip vosk-model-small-en-us-0.15.zip

# Verify
ls vosk-model-small-en-us-0.15/
```

**Option B: Manual Download**

1. Visit: https://alphacephei.com/vosk/models
2. Download `vosk-model-small-en-us-0.15.zip`
3. Extract to `local_meeting_summarizer/` directory

**Other Languages:**
- Spanish: `vosk-model-small-es-0.42`
- German: `vosk-model-small-de-0.15`
- French: `vosk-model-small-fr-0.22`
- [See all models](https://alphacephei.com/vosk/models)

### 5. Configure

Edit `configs/recorder_config.yml`:

```yaml
model_path: vosk-model-small-en-us-0.15  # Match your model name
sample_rate: 16000
summarizer: textrank
```

### 6. Test Your Setup

```bash
# List audio devices
python3 -c "import pyaudio; p = pyaudio.PyAudio(); print('\nAvailable Audio Devices:'); [print(f'  [{i}] {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count()) if p.get_device_info_by_index(i)['maxInputChannels'] > 0]; p.terminate()"

# Test Vosk model
python3 -c "from vosk import Model; m = Model('vosk-model-small-en-us-0.15'); print('✓ Vosk model loaded successfully')"
```

### 7. Run First Recording

```bash
python3 main.py
```

You should see:
```
============================================================
LOCAL MEETING & LECTURE SUMMARIZER
Offline STT with Vosk
============================================================

============================================================
VALIDATING SETUP
============================================================

✓ Vosk model found at: vosk-model-small-en-us-0.15

✓ Found X audio device(s):
  [0] Built-in Microphone [DEFAULT]
  ...

✓ Save directory ready: recordings

============================================================
SETUP VALIDATION PASSED
============================================================

📁 Session folder created: recordings/session_2025-10-28_15-45-23

🎤 Initializing audio recorder...
   Using microphone: Built-in Microphone
   ✓ Audio stream opened (SR: 16000Hz, Mono)
   ✓ WAV file initialized: recordings/session_.../session_....wav
🧠 Initializing STT engine...
   Loading Vosk model from: vosk-model-small-en-us-0.15
   ✓ Vosk model loaded successfully
📝 Initializing transcript aggregator...
📊 Initializing summarizer...
   ✓ Summarizer initialized (mode: textrank)

============================================================
🔴 RECORDING STARTED
============================================================
Press Ctrl+C to stop recording
```

### 8. Speak and Test

- Say something like: "Hello, this is a test recording."
- You should see partial transcriptions appear in real-time
- Press `Ctrl+C` to stop

### 9. Check Output

```bash
# View your session folder
ls -la recordings/session_*/

# Read transcript
cat recordings/session_*/session_*.txt

# Read summary
cat recordings/session_*/session_*_summary.txt
```

## Common Installation Issues

### Issue: "ModuleNotFoundError: No module named 'pyaudio'"

**Solution:**

**On Ubuntu/Debian:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**On Mac:**
```bash
brew install portaudio
pip install pyaudio
```

**On Windows:**
```bash
pip install pipwin