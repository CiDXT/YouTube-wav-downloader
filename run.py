import gradio as gr
import os
import subprocess

def get_video_title(url):
    # 使用 yt-dlp 获取视频标题
    result = subprocess.run(["yt-dlp", "--get-title", url], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        return "Unknown Video"

def fetch(url, custom_name, ext):
    title = get_video_title(url)
    # 截断标题为一个合理的长度
    max_length = 50  # 调整为适当的值
    truncated_title = title[:max_length].strip()
    
    filename = f"{custom_name}.{ext}" if custom_name else f"{truncated_title}.{ext}"
    opts = {
        "wav": ["-f", "ba", "-x", "--audio-format", "wav"],
        "mp4": ["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"],
    }[ext]
    command = ["yt-dlp"] + opts + [url, "-o", filename]
    subprocess.run(command)

    return filename

interface = gr.Interface(
    fn=fetch,
    inputs=[
        gr.Textbox(label="YouTube video address", placeholder="Paste video link here..."),
        gr.Textbox(label="file name", placeholder="默认为视频标题"),
        gr.Dropdown(value="wav", label="format")
    ],
    outputs=gr.File(label="Download the file! (MP3 files available)"),
    description="<div style='font-size:30px; text-align:center;'>YouTube wav downloader</div>"
)

app.launch()