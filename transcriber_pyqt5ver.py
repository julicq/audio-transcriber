import os
import wave
import json
import vosk
from pydub import AudioSegment
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog, QMessageBox, QProgressBar, QWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Specify the path to the FFmpeg executable
AudioSegment.ffmpeg = "ffmpeg-7.0-essentials_build/bin/ffmpeg.exe"

class TranscribeThread(QThread):
    finished = pyqtSignal(str)
    update_progress = pyqtSignal(int)

    def __init__(self, audio_path, model_path):
        super().__init__()
        self.audio_path = audio_path
        self.model_path = model_path

    def run(self):
        try:
            wav_path = self.convert_to_wav(self.audio_path)
            transcript = self.transcribe_audio(wav_path, self.model_path)
            self.finished.emit(transcript)
        except Exception as e:
            self.finished.emit(f"Error: {str(e)}")

    def convert_to_wav(self, audio_path):
        if audio_path.endswith(".mp3"):
            audio = AudioSegment.from_mp3(audio_path)
            audio = audio.set_channels(1)  # Convert stereo to mono
            temp_wav_path = audio_path.replace(".mp3", ".wav")
            audio.export(temp_wav_path, format="wav")
            return temp_wav_path
        return audio_path

    def transcribe_audio(self, audio_path, model_path):
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model path not found: {model_path}")
        
        model = vosk.Model(model_path)
        wf = wave.open(audio_path, "rb")

        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            raise ValueError("Audio file must be WAV format mono PCM.")
        
        rec = vosk.KaldiRecognizer(model, wf.getframerate())
        result_text = ""

        chunk_size = 4000
        total_frames = wf.getnframes()
        for i in range(0, total_frames, chunk_size):
            data = wf.readframes(chunk_size)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                result_text += result.get("text", "") + " "
            progress = min(i * 100 // total_frames, 100)  # Ensure progress doesn't exceed 100%
            self.update_progress.emit(progress)
        
        result_text += json.loads(rec.FinalResult()).get("text", "")
        
        # Emit progress 100% if not already emitted
        if progress < 100:
            self.update_progress.emit(100)

        return result_text

class AudioTranscriberApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Transcriber")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.label_audio_path = QLabel("Audio File Path:")
        layout.addWidget(self.label_audio_path)

        self.entry_audio_path = QLineEdit()
        layout.addWidget(self.entry_audio_path)

        self.button_browse = QPushButton("Browse")
        self.button_browse.clicked.connect(self.open_file)
        layout.addWidget(self.button_browse)

        self.button_transcribe = QPushButton("Transcribe")
        self.button_transcribe.clicked.connect(self.transcribe)
        layout.addWidget(self.button_transcribe)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.text_output = QTextEdit()
        layout.addWidget(self.text_output)

        self.button_save = QPushButton("Save Transcription")
        self.button_save.clicked.connect(self.save_transcription)
        layout.addWidget(self.button_save)

        self.central_widget = QWidget()
        self.central_widget.setLayout(layout)
        self.setCentralWidget(self.central_widget)

        # Initially disable buttons
        self.button_transcribe.setEnabled(False)
        self.button_save.setEnabled(False)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.wav *.mp3)")
        if file_path:
            self.entry_audio_path.setText(file_path)
            # Enable Transcribe button
            self.button_transcribe.setEnabled(True)

    def transcribe(self):
        audio_path = self.entry_audio_path.text()
        model_path = "vosk-model-small-ru-0.22"
        self.thread = TranscribeThread(audio_path, model_path)
        self.thread.finished.connect(self.transcription_finished)
        self.thread.update_progress.connect(self.update_progress)
        self.thread.start()
        # Disable Browse and Transcribe buttons during transcription
        self.button_browse.setEnabled(False)
        self.button_transcribe.setEnabled(False)

    def transcription_finished(self, transcript):
        self.text_output.setPlainText(transcript)
        # Enable all buttons after transcription is finished
        self.button_browse.setEnabled(True)
        self.button_transcribe.setEnabled(True)
        self.button_save.setEnabled(True)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def save_transcription(self):
        transcript = self.text_output.toPlainText()
        if not transcript:
            QMessageBox.warning(self, "Warning", "No transcription to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Transcription", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(transcript)
            QMessageBox.information(self, "Success", f"Transcription saved to {file_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioTranscriberApp()
    window.show()
    sys.exit(app.exec_())