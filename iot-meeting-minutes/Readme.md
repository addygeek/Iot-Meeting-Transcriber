# Local Meeting & Lecture Summarizer

Offline meeting minutes and lecture summarization system using Vosk speech-to-text. Records audio from your microphone, transcribes it locally (no internet required), and generates summaries.

## Features

- ✅ **Fully Offline** - No internet connection required
- 🎤 **Real-time Transcription** - See text as you speak
- 📝 **Automatic Summaries** - Extractive or abstractive summarization
- 💾 **Local Storage** - All data saved on your laptop
- 🔒 **Privacy First** - Nothing leaves your machine
- ⚡ **Lightweight** - Works on standard laptops

## Requirements

- Python 3.7+
- Microphone (USB, USB-C, or 3.5mm)
- Vosk model (download separately)
- ~500MB disk space (depends on model)

## Installation

### 1. Clone or Download

```bash
# Create project directory
mkdir local_meeting_summarizer
cd local_meeting_summarizer
```

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 3. Download Vosk Model

1. Visit [Vosk Models](https://alphacephei.com/vosk/models)
2. Download a model (recommended: `vosk-model-small-en-us-0.15` for English)
3. Extract to project directory
4. Update `model_path` in `configs/recorder_config.yml`

**Recommended Models:**
- **Small (50MB)**: `vosk-model-small-en-us-0.15` - Fast, good accuracy
- **Medium (1.8GB)**: `vosk-model-en-us-0.22` - Better accuracy
- **Large (3GB)**: `vosk-model-en-us-0.22-lgraph` - Best accuracy

### 4. Configure

Edit `configs/recorder_config.yml`:

```yaml
model_path: vosk-model-small-en-us-0.15  # Update this path!
sample_rate: 16000
summarizer: textrank  # or 't5_small' for better quality
```

## Usage

### Start Recording

```bash
python3 main.py
```

The system will:
1. Check your setup (model, microphone)
2. Create a new session folder
3. Start recording and transcribing
4. Show real-time transcription in terminal

### Stop Recording

Press `Ctrl+C` to stop.

The system will:
1. Finalize the audio file
2. Save the complete transcript
3. Generate a summary
4. Display the summary in terminal

## Output Files

Each session creates a folder: `recordings/session_YYYY-MM-DD_HH-MM-SS/`

Contents:
- `session_*.wav` - Audio recording (PCM 16-bit, 16kHz, mono)
- `session_*.txt` - Full transcript with timestamps
- `session_*_summary.txt` - Generated summary
- `session_*_meta.json` - Session metadata
- `session_*_log.txt` - Event log

## Configuration Options

### Audio Settings

```yaml
sample_rate: 16000        # Hz (16000 recommended)
channels: 1               # Mono (1) or Stereo (2)
block_duration_ms: 500    # Processing block size
```

### Summarization

```yaml
summarizer: textrank      # Options:
                          # - 'textrank': Fast, extractive
                          # - 't5_small': Better quality, slower

extractive_sentences: 5   # Number of sentences in summary
```

### Microphone Selection

```yaml
mic_device_name: null     # Auto-detect (null)
# Or specify: "USB Microphone"
```

## Troubleshooting

### "No microphone detected"

**Solution:**
- Check microphone is connected
- Check system permissions
- Try a different USB port
- On Linux: Check ALSA/PulseAudio

### "Vosk model not found"

**Solution:**
- Download model from [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models)
- Extract to project directory
- Update `model_path` in config

### Poor transcription quality

**Solutions:**
- Use a better quality microphone
- Reduce background noise
- Download a larger Vosk model
- Speak clearly and at moderate pace

### "Audio device busy"

**Solution:**
- Close other apps using microphone
- Restart your audio service
- Check system audio settings

### Low performance / lag

**Solutions:**
- Use smaller Vosk model
- Use `textrank` summarizer instead of `t5_small`
- Close other applications
- Increase `block_duration_ms` in config

## Advanced Usage

### Using T5 Summarizer

For better quality summaries (requires more resources):

1. Install transformers:
```bash
pip install transformers torch
```

2. Update config:
```yaml
summarizer: t5_small
```

**Note:** First run will download T5 model (~250MB)

### Custom Microphone

List available devices:
```bash
python3 -c "import pyaudio; p = pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count())]"
```

Set in config:
```yaml
mic_device_name: "Your Microphone Name"
```

### Periodic Auto-Summary

Enable summaries during recording:
```yaml
auto_summary_interval_seconds: 300  # Every 5 minutes
```

## File Structure

```
local_meeting_summarizer/
├── main.py                          # Main controller
├── recorder.py                      # Audio recording
├── stt_engine.py                    # Vosk STT
├── transcript_aggregator.py         # Transcript management
├── summarizer.py                    # Text summarization
├── logger.py                        # Session logging
├── requirements.txt                 # Dependencies
├── configs/
│   └── recorder_config.yml          # Configuration
├── recordings/                      # Output folder
│   └── session_2025-10-28_15-45-23/
│       ├── session_*.wav
│       ├── session_*.txt
│       ├── session_*_summary.txt
│       ├── session_*_meta.json
│       └── session_*_log.txt
└── vosk-model-small-en-us-0.15/    # Vosk model (download)
```

## Tips for Best Results

1. **Microphone Quality**: Use a good quality USB microphone for best transcription
2. **Environment**: Record in quiet environment with minimal background noise
3. **Speaking**: Speak clearly at normal pace
4. **Model Size**: Balance between model size and accuracy for your needs
5. **Disk Space**: Ensure adequate space (1 hour ≈ 120MB WAV + transcript)

## Performance Guide

### Lightweight Setup (Low-end laptop)
- Model: `vosk-model-small-*` (50MB)
- Summarizer: `textrank`
- Sample rate: 16000 Hz
- Expected: Real-time transcription, instant summary

### Balanced Setup (Standard laptop)
- Model: `vosk-model-en-us-0.22` (1.8GB)
- Summarizer: `textrank`
- Sample rate: 16000 Hz
- Expected: Better accuracy, real-time processing

### High Quality Setup (Powerful laptop)
- Model: `vosk-model-en-us-0.22-lgraph` (3GB)
- Summarizer: `t5_small`
- Sample rate: 16000 Hz
- Expected: Best quality, may lag on older systems

## Security & Privacy

- **No Network**: System works completely offline
- **Local Storage**: All data stays on your machine
- **Encryption**: Consider disk encryption for sensitive meetings
- **Data Retention**: Manually delete old sessions as needed

## FAQ

**Q: Can I use this for other languages?**  
A: Yes! Download appropriate Vosk model for your language.

**Q: How accurate is the transcription?**  
A: Depends on model size, microphone quality, and speaking clarity. Expect 85-95% accuracy with good setup.

**Q: Can I edit transcripts?**  
A: Yes, all files are plain text. Edit `.txt` files with any text editor.

**Q: Does it work without internet?**  
A: Yes, completely offline after setup.

**Q: Can I record multiple speakers?**  
A: Yes, but speaker diarization (who said what) is not included in this version.

## License

This project is provided as-is for educational and personal use.

## Credits

- [Vosk](https://alphacephei.com/vosk/) - Offline speech recognition
- [NLTK](https://www.nltk.org/) - Natural language processing
- [TextRank](https://radimrehurek.com/gensim/) - Extractive summarization

## Support

For issues or questions, check:
- Vosk documentation: https://alphacephei.com/vosk/
- PyAudio issues: https://people.csail.mit.edu/hubert/pyaudio/

---

**Made for offline meeting minutes and lecture notes** 📝🎤