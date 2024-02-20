import torch, os, traceback, sys, warnings, shutil, numpy as np
import gradio as gr
import librosa
import asyncio
import rarfile
import edge_tts
import yt_dlp
import ffmpeg
import gdown
import subprocess
import wave
import soundfile as sf
from scipy.io import wavfile
from datetime import datetime
from urllib.parse import urlparse
from mega import Mega

now_dir = os.getcwd()
tmp = os.path.join(now_dir, "TEMP")
shutil.rmtree(tmp, ignore_errors=True)
os.makedirs(tmp, exist_ok=True)
os.environ["TEMP"] = tmp
from lib.infer_pack.models import (
    SynthesizerTrnMs256NSFsid,
    SynthesizerTrnMs256NSFsid_nono,
    SynthesizerTrnMs768NSFsid,
    SynthesizerTrnMs768NSFsid_nono,
)
from fairseq import checkpoint_utils
from vc_infer_pipeline import VC
from config import Config
config = Config()


def vc_single(
    sid,
    vc_audio_mode,
    input_audio_path,
    input_upload_audio,
    vocal_audio,
    tts_text,
    tts_voice,
    f0_up_key,
    f0_file,
    f0_method,
    file_index,
    index_rate,
    filter_radius,
    resample_sr,
    rms_mix_rate,
    protect
):  # spk_item, input_audio0, vc_transform0,f0_file,f0method0
    global tgt_sr, net_g, vc, hubert_model, version, cpt
    try:
        logs = []
        print(f"Converting...")
        logs.append(f"Converting...")
        yield "\n".join(logs), None
        if vc_audio_mode == "Input path" or "Youtube" and input_audio_path != "":
            audio, sr = librosa.load(input_audio_path, sr=16000, mono=True)
        elif vc_audio_mode == "Upload audio":
            selected_audio = input_upload_audio
            if vocal_audio:
                selected_audio = vocal_audio
            elif input_upload_audio:
                selected_audio = input_upload_audio
            sampling_rate, audio = selected_audio
            duration = audio.shape[0] / sampling_rate
            audio = (audio / np.iinfo(audio.dtype).max).astype(np.float32)
            if len(audio.shape) > 1:
                audio = librosa.to_mono(audio.transpose(1, 0))
            if sampling_rate != 16000:
                audio = librosa.resample(audio, orig_sr=sampling_rate, target_sr=16000)
        elif vc_audio_mode == "TTS Audio":
            if tts_text is None or tts_voice is None:
                return "You need to enter text and select a voice", None
            asyncio.run(edge_tts.Communicate(tts_text, "-".join(tts_voice.split('-')[:-1])).save("tts.mp3"))
            audio, sr = librosa.load("tts.mp3", sr=16000, mono=True)
            input_audio_path = "tts.mp3"
        f0_up_key = int(f0_up_key)
        times = [0, 0, 0]
        if hubert_model == None:
            load_hubert()
        if_f0 = cpt.get("f0", 1)
        audio_opt = vc.pipeline(
            hubert_model,
            net_g,
            sid,
            audio,
            input_audio_path,
            times,
            f0_up_key,
            f0_method,
            file_index,
            # file_big_npy,
            index_rate,
            if_f0,
            filter_radius,
            tgt_sr,
            resample_sr,
            rms_mix_rate,
            version,
            protect,
            f0_file=f0_file
        )

def download_audio(url, audio_provider):
    logs = []
    os.makedirs("dl_audio", exist_ok=True)
    if url == "":
        logs.append("URL required!")
        yield None, "\n".join(logs)
        return None, "\n".join(logs)
    if audio_provider == "Youtube":
        logs.append("Downloading the audio...")
        yield None, "\n".join(logs)
        ydl_opts = {
            'noplaylist': True,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
            }],
            "outtmpl": 'result/dl_audio/audio',
        }
        audio_path = "result/dl_audio/audio.wav"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        logs.append("Download Complete.")
        yield audio_path, "\n".join(logs)

def change_audio_mode(vc_audio_mode):
    if vc_audio_mode == "Input path":
        return (
            # Input & Upload
            gr.Textbox.update(visible=True),
            gr.Checkbox.update(visible=False),
            gr.Audio.update(visible=False),
            # Youtube
            gr.Dropdown.update(visible=False),
            gr.Textbox.update(visible=False),
            gr.Textbox.update(visible=False),
            gr.Button.update(visible=False),
            # Splitter
            gr.Dropdown.update(visible=True),
            gr.Textbox.update(visible=True),
            gr.Button.update(visible=True),
            gr.Button.update(visible=False),
            gr.Audio.update(visible=False),
            gr.Audio.update(visible=True),
            gr.Audio.update(visible=True),
            gr.Slider.update(visible=True),
            gr.Slider.update(visible=True),
            gr.Audio.update(visible=True),
            gr.Button.update(visible=True),
            # TTS
            gr.Textbox.update(visible=False),
            gr.Dropdown.update(visible=False)
        )
   # elif vc_audio_mode == "Upload audio":
   #     return (
    #        # Input & Upload
    #        gr.Textbox.update(visible=False),
   ##         gr.Checkbox.update(visible=True),
    #        gr.Audio.update(visible=True),
            # Youtube
  #          gr.Dropdown.update(visible=False),
    #        gr.Textbox.update(visible=False),
    #        gr.Textbox.update(visible=False),
    #        gr.Button.update(visible=False),
            # Splitter
 #           gr.Dropdown.update(visible=True),
  #          gr.Textbox.update(visible=True),
  #          gr.Button.update(visible=False),
   #         gr.Button.update(visible=True),
  #          gr.Audio.update(visible=False),
    #        gr.Audio.update(visible=True),
   #         gr.Audio.update(visible=True),
    #        gr.Slider.update(visible=True),
    #        gr.Slider.update(visible=True),
     #       gr.Audio.update(visible=True),
     #       gr.Button.update(visible=True),
            # TTS
     #       gr.Textbox.update(visible=False),
     $       gr.Dropdown.update(visible=False)
        )
    elif vc_audio_mode == "Youtube":
        return (
            # Input & Upload
    #        gr.Textbox.update(visible=False),
    #        gr.Checkbox.update(visible=False),
    #        gr.Audio.update(visible=False),
            # Youtube
            gr.Dropdown.update(visible=True),
            gr.Textbox.update(visible=True),
            gr.Textbox.update(visible=True),
            gr.Button.update(visible=True),
            # Splitter
    #        gr.Dropdown.update(visible=True),
    #        gr.Textbox.update(visible=True),
    #        gr.Button.update(visible=True),
   #         gr.Button.update(visible=False),
    #        gr.Audio.update(visible=True),
    #        gr.Audio.update(visible=True),
    #        gr.Audio.update(visible=True),
   #         gr.Slider.update(visible=True),
    #        gr.Slider.update(visible=True),
    #        gr.Audio.update(visible=True),
   #         gr.Button.update(visible=True),
            # TTS
 #           gr.Textbox.update(visible=False),
  #          gr.Dropdown.update(visible=False)
        )
 #   elif vc_audio_mode == "TTS Audio":
 #       return (
 #           # Input & Upload
 #           gr.Textbox.update(visible=False),
 #           gr.Checkbox.update(visible=False),
 #           gr.Audio.update(visible=False),
            # Youtube
 #           gr.Dropdown.update(visible=False),
 #           gr.Textbox.update(visible=False),
 #           gr.Textbox.update(visible=False),
 #           gr.Button.update(visible=False),
            # Splitter
  #          gr.Dropdown.update(visible=False),
  #          gr.Textbox.update(visible=False),
  #          gr.Button.update(visible=False),
  #          gr.Button.update(visible=False),
  #          gr.Audio.update(visible=False),
  #          gr.Audio.update(visible=False),
  #          gr.Audio.update(visible=False),
  #          gr.Slider.update(visible=False),
  #          gr.Slider.update(visible=False),
   #         gr.Audio.update(visible=False),
  #          gr.Button.update(visible=False),
            # TTS
   #         gr.Textbox.update(visible=True),
   #         gr.Dropdown.update(visible=True)
        )
        
with gr.Blocks() as app:
    gr.Markdown(
        "# <center> YOUTUBE DOWNLOADER\n"
    )
   
    with gr.TabItem("Inference"):

        with gr.Row():
            with gr.Column():
                vc_audio_mode = gr.Dropdown(label="Input voice", choices=["Youtube"], allow_custom_value=False, value="Youtube")
                vc_download_audio = gr.Dropdown(label="Provider", choices=["Youtube"], allow_custom_value=False, visible=False, value="Youtube", info="Select provider (Default: Youtube)")
                vc_link = gr.Textbox(label="Youtube URL", visible=True, info="Example: https://www.youtube.com/watch?v=Nc0sB1Bmf-A", placeholder="https://www.youtube.com/watch?v=...")
                vc_log_yt = gr.Textbox(label="Output Information", visible=False, interactive=True)
                vc_download_button = gr.Button("Download Audio", variant="primary", visible=True)
                vc_audio_preview = gr.Audio(label="Downloaded Audio Preview", visible=True)
        )
    app.queue().launch()