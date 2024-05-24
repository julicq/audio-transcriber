import os
import wave
import json
import vosk
import razdel
from pydub import AudioSegment
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# Specify the path to the FFmpeg executable
AudioSegment.ffmpeg = "ffmpeg-7.0-essentials_build\bin\ffmpeg.exe"

def transcribe_audio(audio_path, model_path):
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

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            result_text += result.get("text", "") + " "
    
    result_text += json.loads(rec.FinalResult()).get("text", "")
    return result_text

def convert_to_wav(audio_path):
    if audio_path.endswith(".mp3"):
        audio = AudioSegment.from_mp3(audio_path)
        audio = audio.set_channels(1)
        temp_wav_path = audio_path.replace(".mp3", ".wav")
        audio.export(temp_wav_path, format="wav")
        return temp_wav_path
    return audio_path

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav;*.mp3")])
    if file_path:
        entry_audio_path.delete(0, tk.END)
        entry_audio_path.insert(0, file_path)

def transcribe():
    audio_path = entry_audio_path.get()
    model_path = "vosk-model-small-ru-0.22"
    try:
        audio_path = convert_to_wav(audio_path)
        transcript = transcribe_audio(audio_path, model_path)
        
        # Punctuate the transcript
        sentences = [sentence.text + "." for sentence in razdel.sentenize(transcript)]
        punctuated_text = " ".join(sentences)
        
        # Display the punctuated text in the text output widget
        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, punctuated_text)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Создание GUI
root = tk.Tk()
root.title("Audio Transcriber")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

label_audio_path = tk.Label(frame, text="Audio File Path:")
label_audio_path.grid(row=0, column=0, sticky="e")

entry_audio_path = tk.Entry(frame, width=50)
entry_audio_path.grid(row=0, column=1, padx=5, pady=5)

button_browse = tk.Button(frame, text="Browse", command=open_file)
button_browse.grid(row=0, column=2, padx=5, pady=5)

button_transcribe = tk.Button(frame, text="Transcribe", command=transcribe)
button_transcribe.grid(row=1, column=0, columnspan=3, pady=10)

text_output = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=60, height=20)
text_output.grid(row=2, column=0, columnspan=3, pady=10)

root.mainloop()
