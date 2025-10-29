"""
Summarizer Module
Generates summaries using TextRank (extractive) or T5 (abstractive)
"""

import os
from datetime import datetime
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class Summarizer:
    def __init__(self, mode='textrank', num_sentences=5):
        """
        Initialize summarizer
        
        Args:
            mode: 'textrank' for extractive or 't5_small' for abstractive
            num_sentences: Number of sentences for extractive summary
        """
        self.mode = mode
        self.num_sentences = num_sentences
        
        # Download required NLTK data
        self._download_nltk_data()
        
        # Initialize based on mode
        if mode == 't5_small':
            self._init_t5()
        
        print(f"   ✓ Summarizer initialized (mode: {mode})")
    
    def _download_nltk_data(self):
        """Download required NLTK data"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            print("   Downloading NLTK punkt tokenizer...")
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            print("   Downloading NLTK stopwords...")
            nltk.download('stopwords', quiet=True)
    
    def _init_t5(self):
        """Initialize T5 model for abstractive summarization"""
        try:
            from transformers import T5Tokenizer, T5ForConditionalGeneration
            
            print("   Loading T5 model (this may take a moment)...")
            self.t5_tokenizer = T5Tokenizer.from_pretrained('t5-small')
            self.t5_model = T5ForConditionalGeneration.from_pretrained('t5-small')
            print("   ✓ T5 model loaded")
            
        except ImportError:
            print("   Warning: transformers not installed. Install with: pip install transformers")
            print("   Falling back to TextRank mode")
            self.mode = 'textrank'
        except Exception as e:
            print(f"   Warning: Could not load T5 model: {e}")
            print("   Falling back to TextRank mode")
            self.mode = 'textrank'
    
    def generate_summary(self, text):
        """
        Generate summary of the text
        
        Args:
            text: Input text to summarize
            
        Returns:
            str: Summary text
        """
        if not text or len(text.strip()) < 50:
            return "Text too short to summarize."
        
        if self.mode == 'textrank':
            return self._textrank_summary(text)
        elif self.mode == 't5_small':
            return self._t5_summary(text)
        else:
            return self._textrank_summary(text)
    
    def _textrank_summary(self, text):
        """
        Generate extractive summary using TextRank algorithm
        
        Args:
            text: Input text
            
        Returns:
            str: Extractive summary
        """
        # Tokenize into sentences
        sentences = sent_tokenize(text)
        
        if len(sentences) <= self.num_sentences:
            return text
        
        # Create TF-IDF matrix
        try:
            vectorizer = TfidfVectorizer(
                stop_words='english',
                lowercase=True,
                max_features=1000
            )
            
            tfidf_matrix = vectorizer.fit_transform(sentences)
            
            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
            
            # Calculate scores (sum of similarities)
            scores = similarity_matrix.sum(axis=1)
            
            # Get top sentences
            ranked_indices = np.argsort(scores)[::-1]
            top_indices = sorted(ranked_indices[:self.num_sentences])
            
            # Build summary maintaining original order
            summary_sentences = [sentences[i] for i in top_indices]
            summary = ' '.join(summary_sentences)
            
            return summary
            
        except Exception as e:
            print(f"   Warning: TextRank failed: {e}")
            # Fallback: return first N sentences
            return ' '.join(sentences[:self.num_sentences])
    
    def _t5_summary(self, text):
        """
        Generate abstractive summary using T5 model
        
        Args:
            text: Input text
            
        Returns:
            str: Abstractive summary
        """
        try:
            # Prepare input
            input_text = "summarize: " + text
            
            # Tokenize
            inputs = self.t5_tokenizer.encode(
                input_text,
                return_tensors='pt',
                max_length=512,
                truncation=True
            )
            
            # Generate summary
            summary_ids = self.t5_model.generate(
                inputs,
                max_length=150,
                min_length=40,
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True
            )
            
            # Decode summary
            summary = self.t5_tokenizer.decode(
                summary_ids[0],
                skip_special_tokens=True
            )
            
            return summary
            
        except Exception as e:
            print(f"   Warning: T5 summarization failed: {e}")
            print("   Falling back to TextRank...")
            return self._textrank_summary(text)
    
    def save_summary(self, summary, session_folder, session_name):
        """
        Save summary to file
        
        Args:
            summary: Summary text
            session_folder: Path to session folder
            session_name: Session name for filename
            
        Returns:
            str: Path to saved summary file
        """
        summary_file = os.path.join(
            session_folder,
            f"{session_name}_summary.txt"
        )
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"Summary: {session_name}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Mode: {self.mode}\n")
            f.write("=" * 60 + "\n\n")
            
            # Write summary
            f.write(summary)
            
            # Write footer
            f.write("\n\n" + "=" * 60 + "\n")
        
        return summary_file
    
    def get_summary_stats(self, original_text, summary):
        """
        Get statistics about the summary
        
        Args:
            original_text: Original text
            summary: Summary text
            
        Returns:
            dict: Statistics
        """
        orig_words = len(original_text.split())
        summ_words = len(summary.split())
        
        orig_sentences = len(sent_tokenize(original_text))
        summ_sentences = len(sent_tokenize(summary))
        
        compression_ratio = summ_words / orig_words if orig_words > 0 else 0
        
        return {
            'original_words': orig_words,
            'summary_words': summ_words,
            'original_sentences': orig_sentences,
            'summary_sentences': summ_sentences,
            'compression_ratio': compression_ratio
        }