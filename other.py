import gradio as gr
import os
import subprocess
from pydub import AudioSegment
from IPython.display import Audio

def get_video_title(url):
    result = subprocess.run(["yt-dlp", "--get-title", url], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        return "Unknown Video"

def fetch(url, custom_name, ext):
    title = get_video_title(url)
    max_length = 50
    truncated_title = title[:max_length].strip()
    
    filename = f"{custom_name}.{ext}" if custom_name else f"{truncated_title}.{ext}"
    opts = {
        "wav": ["-f", "ba", "-x", "--audio-format", "wav"],
        "mp4": ["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"],
    }[ext]
    command = ["yt-dlp"] + opts + [url, "-o", filename]
    subprocess.run(command)

    return filename

def play_audio(output_audio):
    audio = AudioSegment.from_file(output_audio)
    audio.export("output.wav", format="wav")
    gr.Interface(fn=None, live=False, outputs="audio").play("output.wav")

app = gr.Interface(
    theme='Hev832/EasyAndCool',
    fn=play_audio,
    inputs=[
        gr.Textbox(label="YouTube video address", placeholder="Paste video link here..."),
        gr.Textbox(label="File name", placeholder="Defaults to video title"),
        gr.Dropdown(value="wav", label="Format")
    ],
    outputs=None,
    description="<div style='font-size:30px; text-align:center;'>YouTube Audio Player</div>"
)

app.launch(debug=True, share=True)
