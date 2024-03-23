import gradio as gr
import os
import subprocess

def get_video_title(url):
     
    result = subprocess.run(["yt-dlp", "--get-title", url], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        return "Unknown Video"

def fetch(url, custom_name, ext):
    title = get_video_title(url)
    #  
    max_length = 50  # 
    truncated_title = title[:max_length].strip()
    
    filename = f"{custom_name}.{ext}" if custom_name else f"{truncated_title}.{ext}"
    opts = {
        "mp3": ["-f", "ba", "-x", "--audio-format", "mp3"],
        "wav": ["-f", "ba", "-x", "--audio-format", "wav"],

    }[ext]
    command = ["yt-dlp"] + opts + [url, "-o", filename]
    subprocess.run(command)

    return filename



with gr.Blocks() as demo:    
    used_letters_var = gr.State([])
    with gr.Column():
        gr.Markdown("# YT_DLP GRADIO DEMO")
        gr.Markdown("Please press like button to support me :]")
    with gr.Row() as row:
        with gr.Column():
            url = gr.Textbox(label="URL INPUT")
            custom_name = gr.Textbox(label="Custom Name (defalut if you want!)")
            outputs = gr.Audio(label="outputs")
        with gr.Column():
            btn = gr.Button("download!")
            

    btn.click(
        fetch, 
        [url],
        [outputs]
        )
demo.launch(debug=True, share=True)
