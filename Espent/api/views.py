
import os
import time
import torch
import uuid
from django.conf import settings
from rest_framework.decorators import api_view
from django.http import HttpResponseNotFound
from scipy.io.wavfile import write
from .utils import loadespnet
from .models import Sound
from .serializers import SoundSerializerOut
from rest_framework.response import Response
from django.views.decorators.cache import never_cache
from rest_framework.views import APIView
import shutil

# Create your views here.
BASE_DIR = settings.BASE_DIR
MEDIA_ROOT = settings.MEDIA_ROOT
MEDIA_URL = settings.MEDIA_URL
MEDIA_TEMP_DIR = os.path.join(MEDIA_ROOT,'temp/')


@api_view(['GET'])
@never_cache
def test_api(request):
    return Response({'response':"You are successfully connected to the TTS API"})



@api_view(['POST'])
def text_to_speech(request):

    #Start count inference time
    start_time = time.time()
    text = request.data.get('text')
    text2speech, vocoder = loadespnet()

    # run the models
    with torch.no_grad():
        wav, c, *_ = text2speech(text)
        wav = vocoder.inference(c)


    num_generated =uuid.uuid1()
    print(' id num_generated for audio &&&&&&&&&&&&&&&&&&&&&&&&&&&')
    path = "Audio/sound_output_%02d.wav" % num_generated
    rate = 22050
    audio_numpy = wav.view(-1).cpu().numpy()

    write(path, int(rate) , audio_numpy)

    audio = Sound.objects.create(audio_join =path ,name='Sound_%02d' % num_generated, text_content=text)
    audio.converted=True
    audio.inference_time= str((time.time() - start_time))
    # voice = request.data.get('voice')
    # gender = voice.get('is_male')
    # if gender == 1:
    #     audio.is_male = True
    audio.save()
    ok=True
    print("--- %s seconds ---" % (time.time() - start_time))
    #if ok==True:
    #    response = FileResponse(audio.audio_join)
    #    return response
    serializer = SoundSerializerOut(audio)
    if ok==True:
        return Response( serializer.data )
    return Response({'response':"Sorry, we can't succeed to convert your text to sound!"})


class RetrieveAudios(APIView):

    def delete(self, request):
        folder_input = 'Audio/'
        for filename in os.listdir(folder_input):
            file_path = os.path.join(folder_input, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        return Response({'response': "Media folders were cleaned up!!"})

    def post(self, request):

        # Start count inference time
        start_time = time.time()
        text = request.data.get('text')
        text2speech, vocoder = loadespnet()

        # run the models
        with torch.no_grad():
            wav, c, *_ = text2speech(text)
            wav = vocoder.inference(c)

        num_generated = uuid.uuid1()
        print(' id num_generated for audio &&&&&&&&&&&&&&&&&&&&&&&&&&&')
        path = "Audio/sound_output_%02d.wav" % num_generated
        rate = 22050
        audio_numpy = wav.view(-1).cpu().numpy()

        write(path, int(rate), audio_numpy)

        audio = Sound.objects.create(audio_join=path, name='Sound_%02d' % num_generated, text_content=text)
        audio.converted = True
        audio.inference_time = str((time.time() - start_time))
        # voice = request.data.get('voice')
        # gender = voice.get('is_male')
        # if gender == 1:
        #     audio.is_male = True
        audio.save()
        ok = True
        print("--- %s seconds ---" % (time.time() - start_time))
        # if ok==True:
        #    response = FileResponse(audio.audio_join)
        #    return response
        serializer = SoundSerializerOut(audio)
        if ok == True:
            return Response(serializer.data)
        return Response({'response': "Sorry, we can't succeed to convert your text to sound!"})