#!/usr/bin/env python
"""
Main entry point for the ebook to audiobook converter.
"""

import os
import argparse
import sys
import importlib
import numpy as np
import soundfile as sf
from pathlib import Path
from tqdm import tqdm

# Add src directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extractors import extract_text

# Check if kokoro is available
kokoro_available = importlib.util.find_spec("kokoro") is not None

if kokoro_available:
    try:
        from kokoro import KPipeline
        print("Successfully imported kokoro")
    except Exception as e:
        print(f"Error importing kokoro: {str(e)}")
        kokoro_available = False


def create_venv():
    """Create a virtual environment and install dependencies if it doesn't exist."""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print("Creating virtual environment...")
        os.system("python -m venv venv")
        
        # Determine the pip path based on platform
        pip_path = "venv/bin/pip" if os.name != "nt" else "venv\\Scripts\\pip"
        
        print("Installing dependencies...")
        os.system(f"{pip_path} install -r requirements.txt")
        
        print("Virtual environment created and dependencies installed.")
    else:
        print("Virtual environment already exists.")


def parse_arguments():
    """Parse command line arguments."""
    # Create the default output directory if it doesn't exist
    output_dir = Path("audio_output")
    output_dir.mkdir(exist_ok=True)
    
    # Default output file path
    default_output = str(output_dir / "output.mp3")
    
    parser = argparse.ArgumentParser(
        description="Convert ebooks to audiobooks using Kokoro TTS."
    )
    
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to the input ebook file (epub, mobi, or pdf)."
    )
    
    parser.add_argument(
        "--output", "-o",
        default=default_output,
        help=f"Path to the output audio file. Default: {default_output}"
    )
    
    parser.add_argument(
        "--voice", "-v",
        default="af_heart",
        help="Voice to use for TTS. Default: af_heart"
    )
    
    parser.add_argument(
        "--create-venv",
        action="store_true",
        help="Create a virtual environment and install dependencies."
    )
    
    parser.add_argument(
        "--chunk-size", "-c",
        type=int,
        default=2000,
        help="Maximum size of text chunks for processing. Default: 2000"
    )
    
    parser.add_argument(
        "--sample-rate", "-sr",
        type=int,
        default=24000,
        help="Sample rate for audio output. Default: 24000"
    )

    parser.add_argument(
        "--lang", "-l",
        default="a",
        help="Language code to use. 'a' for American English, 'b' for British English. Default: a"
    )
    
    parser.add_argument(
        "--max-chunks", "-m",
        type=int,
        default=None,
        help="Maximum number of text chunks to process. Default: 3, use 0 for unlimited"
    )
    
    return parser.parse_args()


def split_text(text, chunk_size):
    """
    Split text into smaller chunks while preserving sentence boundaries.
    
    Args:
        text (str): Text to split.
        chunk_size (int): Maximum size of each chunk.
    
    Returns:
        list: List of text chunks.
    """
    # Split text by sentences
    sentences = [s.strip() + '.' for s in text.replace('\n', ' ').split('.') if s.strip()]
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # If adding the next sentence would exceed chunk size, add current chunk to list
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            chunks.append(current_chunk)
            current_chunk = sentence
        else:
            # Add sentence to current chunk with proper spacing
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks


def convert_to_speech(text, output_file, voice="af_heart", chunk_size=2000, sample_rate=24000, lang_code="a", max_chunks=None):
    """
    Convert text to speech using kokoro KPipeline.
    
    Args:
        text (str): Text to convert to speech.
        output_file (str): Path to save the audio file.
        voice (str): Voice to use for TTS.
        chunk_size (int): Maximum size of text chunks.
        sample_rate (int): Sample rate for audio output.
        lang_code (str): Language code to use (a for American, b for British)
        max_chunks (int, optional): Maximum number of chunks to process. None for unlimited.
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        if not kokoro_available:
            print("ERROR: Kokoro TTS is not available.")
            print("Please make sure kokoro is installed and espeak-ng is available.")
            print("Run: pip install kokoro soundfile torch")
            print("And install espeak-ng for your platform.")
            return False
        
        # Split text into smaller chunks
        chunks = split_text(text, chunk_size)
        print(f"Text split into {len(chunks)} chunks for processing.")
        
        # Limit chunks if max_chunks is specified
        if max_chunks is not None and max_chunks > 0:
            chunks = chunks[:max_chunks]
            print(f"Processing limited to first {max_chunks} chunks.")
        
        # Initialize Kokoro TTS pipeline
        print("Initializing Kokoro TTS...")
        
        # Use language code from parameters
        pipeline = KPipeline(lang_code=lang_code)
        
        # Process each chunk and combine audio
        all_audio = []
        
        # Process each chunk
        print(f"Converting {len(chunks)} text chunks to speech...")
        for i, chunk in enumerate(tqdm(chunks)):
            print(f"Processing chunk {i+1}/{len(chunks)}")
            print(f"Chunk text: {chunk[:100]}..." if len(chunk) > 100 else f"Chunk text: {chunk}")
            
            try:
                # Generate audio for this chunk
                generator = pipeline(chunk, voice=voice, speed=1)
                
                # Kokoro returns (graphemes, phonemes, audio) for each audio chunk
                for j, (gs, ps, chunk_audio) in enumerate(generator):
                    all_audio.append(chunk_audio)
                    
                # Add a short pause between chunks
                pause_duration = 0.5  # half a second
                pause_samples = int(pause_duration * sample_rate)
                all_audio.append(np.zeros(pause_samples, dtype=np.float32))
                
            except Exception as e:
                print(f"Error processing chunk {i+1}: {str(e)}")
                print("Failed to convert text to speech. Exiting...")
                return False
        
        # Combine all audio chunks
        if all_audio:
            combined_audio = np.concatenate(all_audio)
            
            # Save to file
            sf.write(output_file, combined_audio, sample_rate)
            print(f"Audio saved to: {output_file}")
            return True
        else:
            print("No audio was generated.")
            return False
        
    except Exception as e:
        print(f"Error in TTS conversion: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point."""
    # Create the default output directory if it doesn't exist
    Path("audio_output").mkdir(exist_ok=True)
    
    args = parse_arguments()
    
    # Create virtual environment if requested
    if args.create_venv:
        create_venv()
    
    # Check if kokoro is available
    if not kokoro_available:
        print("ERROR: Kokoro TTS is not available.")
        print("Please make sure kokoro is installed properly:")
        print("  1. Run: pip install kokoro soundfile torch")
        print("  2. Install espeak-ng for your platform")
        sys.exit(1)
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)
    
    # Check if input file is a supported format
    file_ext = os.path.splitext(args.input)[1].lower()
    if file_ext != ".epub":
        print(f"Error: Unsupported file format '{file_ext}'. Only EPUB files are supported.")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(exist_ok=True, parents=True)
    
    try:
        # Extract text from ebook
        print(f"Extracting text from '{args.input}'...")
        text = extract_text(args.input)
        
        print(f"Extracted {len(text)} characters of text.")
        
        # Convert max_chunks value of 0 to None (for unlimited processing)
        max_chunks = None if args.max_chunks == 0 else args.max_chunks
        
        # Convert text to speech
        success = convert_to_speech(
            text=text,
            output_file=str(output_path),
            voice=args.voice,
            chunk_size=args.chunk_size,
            sample_rate=args.sample_rate,
            lang_code=args.lang,
            max_chunks=max_chunks
        )
        
        if success:
            print(f"Successfully converted '{args.input}' to '{args.output}'")
        else:
            print("Error: Failed to convert ebook to audiobook.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 