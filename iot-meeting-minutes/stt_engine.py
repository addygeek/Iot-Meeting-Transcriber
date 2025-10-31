"""
Vosk STT Engine Module
Handles speech-to-text transcription using Vosk
"""

import json
from vosk import Model, KaldiRecognizer


class VoskSTTEngine:
    def __init__(self, model_path, sample_rate):
        """
        Initialize Vosk STT engine
        
        Args:
            model_path: Path to Vosk model directory
            sample_rate: Audio sample rate (must match recorder)
        """
        self.model_path = model_path
        self.sample_rate = sample_rate
        
        # Load Vosk model
        print(f"   Loading Vosk model from: {model_path}")
        try:
            self.model = Model(model_path)
            print(f"   ✓ Vosk model loaded successfully")
        except Exception as e:
            raise Exception(f"Failed to load Vosk model: {e}")
        
        # Create recognizer
        self.recognizer = KaldiRecognizer(self.model, sample_rate)
        self.recognizer.SetWords(True)  # Enable word-level timestamps
        
        # Stats
        self.partial_count = 0
        self.final_count = 0
    
    def process_audio(self, audio_data):
        """
        Process audio data and return transcription result
        
        Args:
            audio_data: Raw audio bytes (16-bit PCM)
            
        Returns:
            dict: Result dictionary with 'type' and 'text' keys
                  type: 'partial' or 'final'
                  text: Transcribed text
                  words: List of word dictionaries (for final results)
        """
        if not audio_data:
            return None
        
        # Feed audio to recognizer
        if self.recognizer.AcceptWaveform(audio_data):
            # Final result available
            result = json.loads(self.recognizer.Result())
            
            if result.get('text', '').strip():
                self.final_count += 1
                return {
                    'type': 'final',
                    'text': result['text'],
                    'words': result.get('result', [])
                }
        else:
            # Partial result
            result = json.loads(self.recognizer.PartialResult())
            
            if result.get('partial', '').strip():
                self.partial_count += 1
                return {
                    'type': 'partial',
                    'text': result['partial']
                }
        
        return None
    
    def get_final_result(self):
        """
        Get any remaining final result from recognizer
        
        Returns:
            dict: Final result or None
        """
        try:
            result = json.loads(self.recognizer.FinalResult())
            
            if result.get('text', '').strip():
                return {
                    'type': 'final',
                    'text': result['text'],
                    'words': result.get('result', [])
                }
        except Exception as e:
            print(f"   Warning: Error getting final result: {e}")
        
        return None
    
    def reset(self):
        """Reset recognizer state"""
        self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
        self.recognizer.SetWords(True)
    
    def get_stats(self):
        """
        Get transcription statistics
        
        Returns:
            dict: Statistics
        """
        return {
            'partial_results': self.partial_count,
            'final_results': self.final_count
        }