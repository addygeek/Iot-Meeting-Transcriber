#!/usr/bin/env python3
"""
Main Controller for Local Meeting & Lecture Summarizer
Handles session lifecycle, coordinates all components
"""

import sys
import os
import signal
import argparse
from datetime import datetime
from pathlib import Path
import yaml
import json

from recorder import AudioRecorder
from stt_engine import VoskSTTEngine
from transcript_aggregator import TranscriptAggregator
from summarizer import Summarizer
from logger import SessionLogger


class SessionController:
    def __init__(self, config_path='configs/recorder_config.yml'):
        """Initialize the session controller"""
        self.config = self.load_config(config_path)
        self.session_timestamp = None
        self.session_folder = None
        self.recorder = None
        self.stt_engine = None
        self.aggregator = None
        self.summarizer = None
        self.logger = None
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def load_config(self, config_path):
        """Load configuration from YAML file"""
        if not os.path.exists(config_path):
            print(f"ERROR: Configuration file not found at {config_path}")
            print("Creating default configuration...")
            self.create_default_config(config_path)
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def create_default_config(self, config_path):
        """Create default configuration file"""
        os.makedirs('configs', exist_ok=True)
        
        default_config = {
            'model_path': 'D:\PROGRAMING\7th sem 7\iot\vosk\vosk-model-small-en-in-0.4',
            'sample_rate': 16000,
            'channels': 1,
            'block_duration_ms': 500,
            'wav_format': 'PCM_16',
            'save_dir': 'recordings',
            'summarizer': 'textrank',
            'extractive_sentences': 5,
            'auto_summary_interval_seconds': 0,
            'mic_device_name': None
        }
        
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        print(f"Default configuration created at {config_path}")
        print("Please edit the 'model_path' to point to your Vosk model directory")
    
    def validate_setup(self):
        """Validate that all prerequisites are met"""
        print("=" * 60)
        print("VALIDATING SETUP")
        print("=" * 60)
        
        # Check if model exists
        model_path = self.config['model_path']
        if not os.path.exists(model_path):
            print(f"\n❌ ERROR: Vosk model not found at {model_path}")
            print("Please download a Vosk model and update the 'model_path' in config")
            print("Download from: https://alphacephei.com/vosk/models")
            return False
        
        print(f"✓ Vosk model found at: {model_path}")
        
        # Check microphone availability
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            device_count = p.get_device_count()
            
            if device_count == 0:
                print("\n❌ ERROR: No audio devices detected")
                return False
            
            print(f"\n✓ Found {device_count} audio device(s):")
            
            default_input = p.get_default_input_device_info()
            
            for i in range(device_count):
                info = p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    is_default = " [DEFAULT]" if i == default_input['index'] else ""
                    print(f"  [{i}] {info['name']}{is_default}")
            
            p.terminate()
            
        except Exception as e:
            print(f"\n❌ ERROR: Could not access audio system: {e}")
            return False
        
        # Check save directory
        save_dir = self.config['save_dir']
        os.makedirs(save_dir, exist_ok=True)
        print(f"\n✓ Save directory ready: {save_dir}")
        
        print("\n" + "=" * 60)
        print("SETUP VALIDATION PASSED")
        print("=" * 60 + "\n")
        
        return True
    
    def create_session_folder(self):
        """Create a new session folder with timestamp"""
        self.session_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        session_name = f"session_{self.session_timestamp}"
        
        save_dir = self.config['save_dir']
        self.session_folder = os.path.join(save_dir, session_name)
        
        os.makedirs(self.session_folder, exist_ok=True)
        
        print(f"📁 Session folder created: {self.session_folder}\n")
        
        return session_name
    
    def start_session(self):
        """Start a new recording session"""
        if not self.validate_setup():
            return False
        
        session_name = self.create_session_folder()
        
        # Initialize logger
        self.logger = SessionLogger(self.session_folder, session_name)
        self.logger.log("Session started")
        
        try:
            # Initialize components
            print("🎤 Initializing audio recorder...")
            self.recorder = AudioRecorder(
                self.config,
                self.session_folder,
                session_name
            )
            
            print("🧠 Initializing STT engine...")
            self.stt_engine = VoskSTTEngine(
                self.config['model_path'],
                self.config['sample_rate']
            )
            
            print("📝 Initializing transcript aggregator...")
            self.aggregator = TranscriptAggregator(
                self.session_folder,
                session_name
            )
            
            print("📊 Initializing summarizer...")
            self.summarizer = Summarizer(
                self.config['summarizer'],
                self.config['extractive_sentences']
            )
            
            # Start recording
            print("\n" + "=" * 60)
            print("🔴 RECORDING STARTED")
            print("=" * 60)
            print("Press Ctrl+C to stop recording\n")
            
            self.running = True
            self.recorder.start()
            
            # Main processing loop
            self.process_audio_stream()
            
            return True
            
        except Exception as e:
            error_msg = f"Error starting session: {e}"
            print(f"\n❌ {error_msg}")
            if self.logger:
                self.logger.log(error_msg, level="ERROR")
            return False
    
    def process_audio_stream(self):
        """Main loop to process audio and transcribe"""
        block_count = 0
        last_status_time = datetime.now()
        
        try:
            while self.running:
                # Get audio block from recorder
                audio_block = self.recorder.get_audio_block()
                
                if audio_block is None:
                    continue
                
                # Process with STT
                result = self.stt_engine.process_audio(audio_block)
                
                if result:
                    if result['type'] == 'partial':
                        # Show partial results in real-time
                        print(f"🎯 Partial: {result['text']}", end='\r')
                    
                    elif result['type'] == 'final':
                        # Add to transcript
                        print(f"\n✓ Final: {result['text']}")
                        self.aggregator.add_segment(result['text'])
                        self.logger.log(f"Transcribed: {result['text'][:50]}...")
                
                # Periodic status update
                block_count += 1
                if (datetime.now() - last_status_time).seconds >= 10:
                    duration = self.recorder.get_duration()
                    print(f"\n⏱️  Recording duration: {duration:.1f}s")
                    last_status_time = datetime.now()
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping recording...")
        except Exception as e:
            print(f"\n❌ Error during recording: {e}")
            self.logger.log(f"Error during recording: {e}", level="ERROR")
    
    def stop_session(self):
        """Stop the current session and finalize outputs"""
        if not self.running:
            return
        
        self.running = False
        
        print("\n" + "=" * 60)
        print("⏹️  FINALIZING SESSION")
        print("=" * 60 + "\n")
        
        try:
            # Stop recorder and finalize WAV
            if self.recorder:
                print("📼 Finalizing audio recording...")
                self.recorder.stop()
            
            # Get final result from STT
            if self.stt_engine:
                print("🎤 Getting final transcription...")
                final_result = self.stt_engine.get_final_result()
                if final_result and final_result.get('text'):
                    self.aggregator.add_segment(final_result['text'])
            
            # Save final transcript
            if self.aggregator:
                print("📝 Saving transcript...")
                transcript_file = self.aggregator.save_transcript()
                print(f"   ✓ Saved: {transcript_file}")
            
            # Generate summary
            if self.summarizer and self.aggregator:
                print("📊 Generating summary...")
                transcript_text = self.aggregator.get_full_transcript()
                
                if transcript_text.strip():
                    summary = self.summarizer.generate_summary(transcript_text)
                    summary_file = self.summarizer.save_summary(
                        summary,
                        self.session_folder,
                        f"session_{self.session_timestamp}"
                    )
                    print(f"   ✓ Saved: {summary_file}")
                    
                    print("\n" + "=" * 60)
                    print("📋 SUMMARY")
                    print("=" * 60)
                    print(summary)
                    print("=" * 60 + "\n")
                else:
                    print("   ⚠️  No transcript content to summarize")
            
            # Save metadata
            self.save_metadata()
            
            # Final log
            if self.logger:
                self.logger.log("Session ended normally")
                self.logger.close()
            
            print("✅ Session completed successfully!")
            print(f"📁 All files saved to: {self.session_folder}\n")
            
        except Exception as e:
            print(f"\n❌ Error during session finalization: {e}")
            if self.logger:
                self.logger.log(f"Error during finalization: {e}", level="ERROR")
    
    def save_metadata(self):
        """Save session metadata to JSON file"""
        session_name = f"session_{self.session_timestamp}"
        meta_file = os.path.join(self.session_folder, f"{session_name}_meta.json")
        
        metadata = {
            'session_name': session_name,
            'start_time': self.session_timestamp,
            'stop_time': datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
            'sample_rate': self.config['sample_rate'],
            'channels': self.config['channels'],
            'mic_device_name': self.config.get('mic_device_name', 'default'),
            'vosk_model_path': self.config['model_path'],
            'wav_file': f"{session_name}.wav",
            'transcript_file': f"{session_name}.txt",
            'summary_file': f"{session_name}_summary.txt",
            'summary_mode': self.config['summarizer'],
            'errors': self.logger.get_errors() if self.logger else []
        }
        
        with open(meta_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"💾 Metadata saved: {meta_file}")
    
    def signal_handler(self, sig, frame):
        """Handle interrupt signals gracefully"""
        print("\n\n🛑 Interrupt received, stopping session...")
        self.stop_session()
        sys.exit(0)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Local Meeting & Lecture Summarizer - Offline STT with Vosk'
    )
    parser.add_argument(
        '--config',
        default='configs/recorder_config.yml',
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("LOCAL MEETING & LECTURE SUMMARIZER")
    print("Offline STT with Vosk")
    print("=" * 60 + "\n")
    
    controller = SessionController(args.config)
    
    if controller.start_session():
        controller.stop_session()


if __name__ == "__main__":
    main()