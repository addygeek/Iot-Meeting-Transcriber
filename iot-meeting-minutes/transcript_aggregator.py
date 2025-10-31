"""
Transcript Aggregator Module
Collects and manages transcript segments with timestamps
"""

import os
from datetime import datetime, timedelta


class TranscriptAggregator:
    def __init__(self, session_folder, session_name):
        """
        Initialize transcript aggregator
        
        Args:
            session_folder: Path to session folder
            session_name: Name of session for file naming
        """
        self.session_folder = session_folder
        self.session_name = session_name
        
        # Transcript data
        self.segments = []
        self.start_time = datetime.now()
        
        # File path
        self.transcript_file = os.path.join(
            session_folder,
            f"{session_name}.txt"
        )
        
        # Partial save tracking
        self.last_save_time = datetime.now()
        self.save_interval = timedelta(seconds=30)  # Save every 30 seconds
    
    def add_segment(self, text, words=None):
        """
        Add a transcript segment
        
        Args:
            text: Transcribed text
            words: Optional list of word dictionaries with timestamps
        """
        if not text or not text.strip():
            return
        
        # Calculate elapsed time
        elapsed = datetime.now() - self.start_time
        timestamp = self._format_timestamp(elapsed.total_seconds())
        
        # Create segment
        segment = {
            'timestamp': timestamp,
            'elapsed_seconds': elapsed.total_seconds(),
            'text': text.strip(),
            'words': words or []
        }
        
        self.segments.append(segment)
        
        # Periodic save
        if datetime.now() - self.last_save_time >= self.save_interval:
            self._save_partial()
    
    def _format_timestamp(self, seconds):
        """
        Format seconds into HH:MM:SS
        
        Args:
            seconds: Time in seconds
            
        Returns:
            str: Formatted timestamp
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def _save_partial(self):
        """Save partial transcript to disk"""
        try:
            self._write_transcript(self.transcript_file + '.partial')
            self.last_save_time = datetime.now()
        except Exception as e:
            print(f"   Warning: Could not save partial transcript: {e}")
    
    def save_transcript(self):
        """
        Save final transcript to disk
        
        Returns:
            str: Path to saved transcript file
        """
        self._write_transcript(self.transcript_file)
        
        # Remove partial file if it exists
        partial_file = self.transcript_file + '.partial'
        if os.path.exists(partial_file):
            try:
                os.remove(partial_file)
            except:
                pass
        
        return self.transcript_file
    
    def _write_transcript(self, filepath):
        """
        Write transcript to file
        
        Args:
            filepath: Path to write to
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"Transcript: {self.session_name}\n")
            f.write(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            # Write segments
            for segment in self.segments:
                line = f"[{segment['timestamp']}] {segment['text']}\n"
                f.write(line)
            
            # Write footer
            f.write("\n" + "=" * 60 + "\n")
            f.write(f"Total segments: {len(self.segments)}\n")
            
            if self.segments:
                total_time = self.segments[-1]['elapsed_seconds']
                f.write(f"Duration: {self._format_timestamp(total_time)}\n")
    
    def get_full_transcript(self):
        """
        Get full transcript as plain text (no timestamps)
        
        Returns:
            str: Full transcript text
        """
        return ' '.join(segment['text'] for segment in self.segments)
    
    def get_timestamped_transcript(self):
        """
        Get transcript with timestamps
        
        Returns:
            list: List of dictionaries with timestamp and text
        """
        return self.segments.copy()
    
    def get_segment_count(self):
        """
        Get number of segments
        
        Returns:
            int: Number of segments
        """
        return len(self.segments)
    
    def get_word_count(self):
        """
        Get approximate word count
        
        Returns:
            int: Word count
        """
        text = self.get_full_transcript()
        return len(text.split())
    
    def clear(self):
        """Clear all segments"""
        self.segments = []
        self.start_time = datetime.now()