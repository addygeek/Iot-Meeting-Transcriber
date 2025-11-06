"""
Session Logger Module
Handles logging of events and errors during recording sessions
"""

import os
from datetime import datetime


class SessionLogger:
    def __init__(self, session_folder, session_name):
        """
        Initialize session logger
        
        Args:
            session_folder: Path to session folder
            session_name: Name of session for file naming
        """
        self.session_folder = session_folder
        self.session_name = session_name
        
        # Log file path
        self.log_file = os.path.join(
            session_folder,
            f"{session_name}_log.txt"
        )
        
        # Error tracking
        self.errors = []
        
        # Open log file
        self.file_handle = open(self.log_file, 'w', encoding='utf-8')
        
        # Write header
        self._write_header()
    
    def _write_header(self):
        """Write log file header"""
        self.file_handle.write("=" * 60 + "\n")
        self.file_handle.write(f"Session Log: {self.session_name}\n")
        self.file_handle.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.file_handle.write("=" * 60 + "\n\n")
        self.file_handle.flush()
    
    def log(self, message, level="INFO"):
        """
        Log a message
        
        Args:
            message: Message to log
            level: Log level (INFO, WARNING, ERROR)
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] [{level}] {message}\n"
        
        self.file_handle.write(log_line)
        self.file_handle.flush()
        
        # Track errors
        if level == "ERROR":
            self.errors.append({
                'timestamp': timestamp,
                'message': message
            })
    
    def get_errors(self):
        """
        Get list of errors
        
        Returns:
            list: List of error dictionaries
        """
        return self.errors.copy()
    
    def close(self):
        """Close log file"""
        if self.file_handle and not self.file_handle.closed:
            self.file_handle.write("\n" + "=" * 60 + "\n")
            self.file_handle.write(f"Session ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.file_handle.write(f"Total errors: {len(self.errors)}\n")
            self.file_handle.write("=" * 60 + "\n")
            self.file_handle.close()