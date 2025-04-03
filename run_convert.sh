#!/bin/bash
# Script to run the ebook to audiobook converter
# Usage: ./run_convert.sh <input_file.epub>

# Check if a file was provided
if [ -z "$1" ]; then
    echo "Error: No input file specified."
    echo "Usage: ./run_convert.sh <path_to_file.epub>"
    echo "Only EPUB (.epub) files are supported."
    exit 1
fi

# Input file from command line argument
INPUT_FILE="$1"

# Check if the file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file '$INPUT_FILE' does not exist."
    exit 1
fi

# Check if the file has a supported extension
if [[ ! "$INPUT_FILE" =~ \.epub$ ]]; then
    echo "Error: Unsupported file format. Only EPUB (.epub) files are supported."
    exit 1
fi

# First, ensure we have all dependencies by running the install script
echo "Setting up environment and dependencies..."
bash install.sh

# Check if installation was successful
if [ $? -ne 0 ]; then
    echo "Error: Installation failed. Please check the output above for more details."
    exit 1
fi

# Run the converter with the specified input
echo "Converting '${INPUT_FILE}' to audio using Kokoro TTS with the af_heart voice..."
echo "This may take a few minutes depending on the size of the ebook."
source ./venv/bin/activate

python3 src/main.py --input "${INPUT_FILE}" --voice af_heart

# Check if conversion was successful
if [ $? -ne 0 ]; then
    echo "Error: Conversion failed. Please check the output above for more details."
    exit 1
else
    echo "Conversion process completed successfully. The audio file is in the audio_output directory."
fi 