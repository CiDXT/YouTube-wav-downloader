import gradio as gr
import yt_dlp


def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': '%(title)s.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return "audio downloaded as '%(title)s.wav'"


with gr.Blocks(theme="Hev832/soft", title="yt-dlp") as demo:    
    used_letters_var = gr.State([])
    with gr.Column():
        gr.Markdown("# YT_DLP GRADIO DEMO")
        gr.Markdown("Please press stars ⭐ button on github to support me :]")
    with gr.Row() as row:
        with gr.Column():
            url = gr.Textbox(label="URL INPUT")
            
        with gr.Column():
            btn = gr.Button("download!")
            outputs = gr.Audio(label="outputs")

    btn.click(
        download_audio, 
        [url],
        [outputs]
        )
demo.launch(debug=True, share=True)
