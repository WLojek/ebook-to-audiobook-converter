# Ebook to Audiobook Converter

A tool to convert EPUB ebooks to audiobooks using local Kokoro TTS.

## Features

- Extracts text from EPUB files
- Converts text to audio using Kokoro TTS locally
- Supports multiple voices and customization options
- Automatically saves audio files to the `audio_output` folder

## Requirements

- Python 3.11 recommended (compatibility issues with Python 3.13)
- espeak-ng (for text-to-speech processing)

## Setup

### Automatic Setup

The easiest way to set up is to use the provided installation script:

```bash
# Make the script executable
chmod +x install.sh
# Run the installer
./install.sh
```

This will:
- Check for Python and try to use Python 3.11 if available
- Install espeak-ng if needed
- Create a virtual environment
- Install all dependencies

### Manual Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ebook_to_audiobook_converter.git
cd ebook_to_audiobook_converter
```

2. Create and activate a virtual environment (preferably with Python 3.11):
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

If you encounter issues with kokoro installation, try:
```bash
pip install kokoro==0.7.4 soundfile torch
```

## Usage

### Quick Start

Use the provided script to convert an ebook by specifying the path to your EPUB file:

```bash
# Make the script executable first
chmod +x run_convert.sh

# Run the converter with your EPUB file
./run_convert.sh path/to/your/ebook.epub
```

The script requires an EPUB file path as its first argument and will:
1. Verify that the file exists and has the .epub extension
2. Set up the necessary environment and dependencies
3. Convert the ebook to an audiobook using the default voice (af_heart)
4. Save the output to the audio_output directory

### Advanced Usage

For more control over the conversion process, you can use the Python script directly:

```bash
# Example with custom output and voice
python src/main.py --input "path/to/your/ebook.epub" --output "audio_output/output.mp3" --voice "af_heart" --lang "a"
```

Available options:
- `--input`, `-i`: Path to the input EPUB file (required)
- `--output`, `-o`: Path to the output audio file (default: audio_output/output.mp3)
- `--voice`, `-v`: Voice to use for TTS (default: af_heart)
- `--lang`, `-l`: Language code to use ("a" for American English, "b" for British English, default: a)
- `--chunk-size`, `-c`: Maximum size of text chunks for processing (default: 2000)
- `--sample-rate`, `-sr`: Sample rate for audio output (default: 24000)
- `--create-venv`: Create a virtual environment and install dependencies

## Supported File Format

- EPUB (.epub)

## How It Works

1. The application extracts text from the EPUB ebook using ebooklib
2. The extracted text is split into manageable chunks
3. Kokoro TTS generates audio from each chunk using the selected voice and language
4. The audio chunks are combined and saved to the specified output file

## Troubleshooting

- **Installation Issues**: If you encounter errors during installation, try using Python 3.11 instead of newer versions.
- **Kokoro Installation**: If kokoro fails to install through requirements.txt, try installing it separately with `pip install kokoro==0.7.4 soundfile torch`.
- **Missing espeak-ng**: Make sure espeak-ng is installed as it's required by kokoro for text processing.
- **File Path Issues**: If your file path contains spaces, make sure to enclose it in quotes: `./run_convert.sh "path/with spaces/book.epub"`

## License

MIT 