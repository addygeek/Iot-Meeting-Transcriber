"""
Audio Recorder Module
Handles microphone input and WAV file writing
"""

import pyaudio
import wave
import queue
import threading
import time
import os


class AudioRecorder:
    def __init__(self, config, session_folder, session_name):
        """
        Initialize audio recorder
        
        Args:
            config: Configuration dictionary
            session_folder: Path to session folder
            session_name: Name of session for file naming
        """
        self.config = config
        self.session_folder = session_folder
        self.session_name = session_name
        
        # Audio parameters
        self.sample_rate = config['sample_rate']
        self.channels = config['channels']
        self.block_duration_ms = config['block_duration_ms']
        
        # Calculate block size in frames
        self.chunk_size = int(self.sample_rate * self.block_duration_ms / 1000)
        
        # Audio stream and file
        self.audio = None
        self.stream = None
        self.wav_file = None
        
        # Threading
        self.audio_queue = queue.Queue()
        self.recording = False
        self.record_thread = None
        
        # Timing
        self.start_time = None
        self.frames_recorded = 0
        
        # Initialize audio
        self._init_audio()
        self._init_wav_file()
    
    def _init_audio(self):
        """Initialize PyAudio and open stream"""
        self.audio = pyaudio.PyAudio()
        
        # Get device index if specified
        device_index = None
        mic_name = self.config.get('mic_device_name')
        
        if mic_name:
            for i in range(self.audio.get_device_count()):
                info = self.audio.get_device_info_by_index(i)
                if mic_name.lower() in info['name'].lower():
                    device_index = i
                    print(f"   Using microphone: {info['name']}")
                    break
            
            if device_index is None:
                print(f"   Warning: Microphone '{mic_name}' not found, using default")
        
        # Open audio stream
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            try:
                self.stream = self.audio.open(
                    format=pyaudio.paInt16,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=self.chunk_size,
                    stream_callback=self._audio_callback
                )
                print(f"   ✓ Audio stream opened (SR: {self.sample_rate}Hz, Mono)")
                break
                
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise Exception(f"Failed to open audio stream after {max_retries} attempts: {e}")
                
                print(f"   Retry {retry_count}/{max_retries}...")
                time.sleep(1)
    
    def _init_wav_file(self):
        """Initialize WAV file for writing"""
        wav_filename = os.path.join(
            self.session_folder,
            f"{self.session_name}.wav"
        )
        
        self.wav_file = wave.open(wav_filename, 'wb')
        self.wav_file.setnchannels(self.channels)
        self.wav_file.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        self.wav_file.setframerate(self.sample_rate)
        
        print(f"   ✓ WAV file initialized: {wav_filename}")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """
        Callback function for audio stream (runs in separate thread)
        
        Args:
            in_data: Audio data bytes
            frame_count: Number of frames
            time_info: Timing information
            status: Stream status
        """
        if status:
            print(f"   ⚠️  Stream status: {status}")
        
        if self.recording:
            # Add to queue for processing
            self.audio_queue.put(in_data)
            
            # Write to WAV file
            self.wav_file.writeframes(in_data)
            self.frames_recorded += frame_count
        
        return (in_data, pyaudio.paContinue)
    
    def start(self):
        """Start recording"""
        self.recording = True
        self.start_time = time.time()
        
        if self.stream:
            self.stream.start_stream()
    
    def stop(self):
        """Stop recording and finalize files"""
        self.recording = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        
        if self.wav_file:
            self.wav_file.close()
        
        if self.audio:
            self.audio.terminate()
        
        duration = self.get_duration()
        print(f"   ✓ Recording stopped. Total duration: {duration:.1f}s")
    
    def get_audio_block(self, timeout=0.1):
        """
        Get next audio block from queue
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            bytes: Audio data or None if queue empty
        """
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_duration(self):
        """
        Get current recording duration in seconds
        
        Returns:
            float: Duration in seconds
        """
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
    
    def get_frames_recorded(self):
        """
        Get total number of frames recorded
        
        Returns:
            int: Number of frames
        """
        return self.frames_recorded