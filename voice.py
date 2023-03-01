import audioop
import time
import pyaudio
import wave


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 20
OUTPUT_FILENAME = 'output.wav'


def record():
    min_level = 3600
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

