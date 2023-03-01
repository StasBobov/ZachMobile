import audioop
import json
import logging
import time

import requests

import constants
import notes

import pyaudio
import wave
import speech_recognition as sr
from os import path

log = logging.getLogger('notes_loger')
log.setLevel(logging.DEBUG)
fh = logging.FileHandler("zach.log", 'a', 'utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 20
OUTPUT_FILENAME = 'note.wav'


def record():
    min_level = 4000
    wait_time = time.time() + 3
    wait_timeout = time.time() + 30
    global stream, p, frames
    p = pyaudio.PyAudio()
    stream = p.open(
        format= FORMAT,
        channels= CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer= CHUNK
    )
    print('Record')

    frames = []

    while time.time() < wait_time and time.time() < wait_timeout:
        data = stream.read(CHUNK)
        frames.append(data)
        if audioop.max(data, 2) > min_level:  # пересчитываю условия выполнения цикла в зависимости от уровня громкости
            print(audioop.max(data, 2))
            wait_time = time.time() + 3
    stop_record()


def stop_record():
    print('Stop')
    stream.stop_stream()
    stream.close()
    p.terminate()
    save()


def save():
    wf = wave.open(OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    convert_to_text()


def convert_to_text():
    AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "note.wav")
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)  # read the entire audio file
        try:
           text_result = r.recognize_google(audio)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

    note_data_for_load = {'description': text_result}
    # requests.post присваивает запросу ключ
    log.info('Sends new note data to the server')
    new_note_request = requests.post(
        'https://zach-mobile-default-rtdb.firebaseio.com/%s/notes.json?auth=%s'
        % (constants.LOCAL_ID, constants.ID_TOKEN), data=json.dumps(note_data_for_load))
    log.info(new_note_request)
