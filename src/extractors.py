"""
Text extractor for EPUB format.
"""

import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re

class BaseExtractor:
    """Base class for all text extractors."""
    
    def extract(self, file_path):
        """Extract text from a file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        return self._extract(file_path)
    
    def _extract(self, file_path):
        """Implement in subclasses."""
        raise NotImplementedError("Subclasses must implement this method")


class EpubExtractor(BaseExtractor):
    """Extract text from EPUB files."""
    
    def _extract(self, file_path):
        book = epub.read_epub(file_path)
        text = []
        
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                content = item.get_content().decode('utf-8')
                soup = BeautifulSoup(content, 'html.parser')
                text.append(soup.get_text())
        
        return '\n'.join(text)


def get_extractor(file_path):
    """Factory method to get the appropriate extractor based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.epub':
        return EpubExtractor()
    else:
        raise ValueError(f"Unsupported file format: {ext}. Only EPUB files are supported.")


def clean_text(text):
    """Clean the extracted text for better TTS results."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove page numbers and other artifacts
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
    
    # Replace common ligatures
    text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
    
    # Fix spacing after punctuation
    text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
    
    return text.strip()


def extract_text(file_path):
    """Extract and clean text from an ebook file."""
    extractor = get_extractor(file_path)
    raw_text = extractor.extract(file_path)
    return clean_text(raw_text) 