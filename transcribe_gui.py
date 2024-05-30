import os
import threading
import wave
import json
import vosk
from pydub import AudioSegment
from tqdm import tqdm
import tkinter as tk
import tkinter.ttk as ttk
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

    chunk_size = 4000
    total_frames = wf.getnframes()
    with tqdm(total=total_frames, unit='frames', desc='Transcribing') as pbar:
        while True:
            data = wf.readframes(chunk_size)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                result_text += result.get("text", "") + " "
            pbar.update(len(data))
            progress_bar["value"] = wf.tell() / total_frames * 100  # Update progress bar value
            progress_bar.update()  # Force update of the progress bar in the GUI
    
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
        
        # Process in a separate thread to keep GUI responsive
        threading.Thread(target=transcribe_thread, args=(audio_path, model_path)).start()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def transcribe_thread(audio_path, model_path):
    try:
        transcript = transcribe_audio(audio_path, model_path)
        text_output.delete(1.0, tk.END)
        text_output.insert(tk.END, transcript)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def save_to_file():
    transcript = text_output.get("1.0", tk.END).strip()
    if not transcript:
        messagebox.showwarning("Warning", "No transcription to save.")
        return
    
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(transcript)
        messagebox.showinfo("Success", f"Transcription saved to {file_path}")

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

progress_bar = ttk.Progressbar(frame, orient=tk.HORIZONTAL, mode='determinate')
progress_bar.grid(row=2, column=0, columnspan=3, pady=10, sticky="ew")

button_save = tk.Button(frame, text="Save Transcription", command=save_to_file)
button_save.grid(row=3, column=0, columnspan=3, pady=10)

text_output = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=60, height=20)
text_output.grid(row=4, column=0, columnspan=3, pady=10)

root.mainloop()
