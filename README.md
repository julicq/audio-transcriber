# Audio Transcriber

## Overview
The Audio Transcriber is a simple Python program designed to transcribe audio files into text. It utilizes the Vosk speech recognition library for transcription and supports both WAV and MP3 audio formats. The transcribed text is displayed in a graphical user interface (GUI) where users can easily transcribe audio files and view the text output.

## Features
- Transcribe audio files (WAV and MP3) into text.
- Graphical user interface (GUI) for easy interaction.
- Support for Russian language transcription.
- Automatic sentence punctuation for Russian text.

## Installation
1. Clone or download the repository to your local machine.
2. Install the required Python libraries by running:
    ```
    pip install -r requirements.txt
    ```
3. Ensure you have FFmpeg installed and added to your system PATH for MP3 support.

## Usage
1. Run the program by executing the `audio_transcriber.py` script.
2. In the GUI, click the "Browse" button to select an audio file (WAV or MP3) for transcription.
3. Click the "Transcribe" button to start the transcription process.
4. The transcribed text will be displayed in the text output area of the GUI.
5. You can copy the transcribed text or save it to a file for further use.

## Dependencies
- [Vosk](https://github.com/alphacep/vosk-api): Speech recognition library.
- [Pydub](https://github.com/jiaaro/pydub): Audio processing library.
- [NLTK](https://www.nltk.org/): Natural Language Toolkit for sentence tokenization.
- [Razdel](https://github.com/natasha/razdel): Russian sentence segmentation library.

## Contributing
Contributions are welcome! If you'd like to contribute to the project, please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
