import gradio as gr
import yt_dlp
import os

def downloader(video_url, audio_format, audio_name):
    # Ensure the directory exists
    os.makedirs('audios', exist_ok=True)
    
    # Use a temporary placeholder for the output file
    temp_output_path = f"audios/{audio_name}.%(ext)s"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,
        }],
        'outtmpl': temp_output_path,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])
    
    # Find the downloaded file and rename it
    temp_file = temp_output_path.replace('%(ext)s', audio_format)
    final_output_path = f"audios/{audio_name}.{audio_format}"
    os.rename(temp_file, final_output_path)
    
    return final_output_path


    

    logschart = """
    ### Changelog

    #### v1.1.0 - 2024-05-16

    ##### Added
    - **Directory Check**: Added a check to ensure the `audios` directory exists before attempting to save files to it.
      - `os.makedirs('audios', exist_ok=True)`

    ##### Changed
    - **Output Template Placeholder**: Updated `outtmpl` to use a temporary placeholder for the file extension.
      - `outtmpl: f"audios/{audio_name}.%(ext)s"`
    - **File Renaming**: Added logic to rename the temporary output file to the final desired name and extension.
      - `temp_file = temp_output_path.replace('%(ext)s', audio_format)`
      - `final_output_path = f"audios/{audio_name}.{audio_format}`
      - `os.rename(temp_file, final_output_path)`
    - **Return Correct Path**: The `downloader` function now returns the final output path to ensure Gradio can find and load the audio file correctly.
      - `return final_output_path`

    ##### Fixed
    - **File Not Found Error**: Resolved the issue where the file could not be found due to incorrect output path handling.

    ### Summary of Changes

    1. **Ensured Directory Exists**: Added code to create the `audios` directory if it doesn't exist to prevent file saving errors.
    2. **Output Path Handling**: Modified the output template to use a placeholder for the file extension, which yt-dlp will replace with the actual extension upon downloading.
    3. **File Renaming Logic**: After downloading the audio, the code now renames the file to match the desired audio name and format.
    4. **Correct File Path Return**: The correct file path is now returned from the `downloader` function, ensuring that the Gradio `gr.Audio` component can properly display and play the downloaded audio file.

    These changes collectively ensure that the audio file is downloaded correctly, renamed appropriately, and made accessible to the Gradio interface for playback.
    """


with gr.Blocks() as demo:
    gr.Markdown("# YouTube Downloader 2.0")
    with gr.Row():
        video_url = gr.Textbox(default="https://youtu.be/yQBGdXGCUbA?si=7avvqH-6OOkGWqFm", label="YouTube video link")
        audio_name = gr.Textbox(default="killshot", label="Audio name of YouTube audio")
        audio_format = gr.Radio(["wav", "flac", "mp3"], label="Select the output format")
    with gr.Row():
        output = gr.Audio(label="Output")
    with gr.Row():
        download_button = gr.Button("Download")
        download_button.click(downloader, inputs=[video_url, audio_format, audio_name], outputs=output)
    with gr.Group():
        with gr.Row():
            gr.Markdown(logschart)

demo.launch()
