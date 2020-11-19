
import os
import uuid
from espnet_model_zoo.downloader import ModelDownloader
from espnet2.bin.tts_inference import Text2Speech
from parallel_wavegan.utils import download_pretrained_model
from parallel_wavegan.utils import load_model


# Model tags
fs, lang = 22050, "English"
tag = "kan-bayashi/ljspeech_tacotron2"
vocoder_tag = "ljspeech_full_band_melgan.v2"

def get_path_media(instance, filename):
    _, ext = os.path.splitext(filename)
    return 'audio/{}{}'.format(uuid.uuid4(), ext)

def get_path_media_audio_transformation(instance, filename):
    _, ext = os.path.splitext(filename)
    return 'audio_transformation/{}{}'.format(uuid.uuid4(), ext)

def loadespnet():
    fs, lang = 22050, "English"
    tag = "kan-bayashi/ljspeech_tacotron2"
    vocoder_tag = "ljspeech_full_band_melgan.v2"

    d = ModelDownloader()
    text2speech = Text2Speech(
        **d.download_and_unpack(tag),
        device="cuda",
        # Only for Tacotron 2
        threshold=0.5,
        minlenratio=0.0,
        maxlenratio=10.0,
        use_att_constraint=False,
        backward_window=1,
        forward_window=3,
        # Only for FastSpeech & FastSpeech2
        speed_control_alpha=1.0,
    )
    text2speech.spc2wav = None  # Disable griffin-lim
    # NOTE: Sometimes download is failed due to "Permission denied". That is
    #   the limitation of google drive. Please retry after serveral hours.
    vocoder = load_model(download_pretrained_model(vocoder_tag)).to("cuda").eval()
    vocoder.remove_weight_norm()

    return text2speech, vocoder


