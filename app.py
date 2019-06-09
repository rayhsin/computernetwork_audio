
from flask import Flask, render_template, Response,send_from_directory ,request
from camera import camera_stream
from threading import Thread,currentThread
import os
import traceback
import time
app = Flask(__name__)

#..........
#
#..........
import argparse
import tempfile
import queue
import sys
from audio import audio_stream


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    '-l', '--list-devices', action='store_true',
    help='show list of audio devices and exit')
parser.add_argument(
    '-d', '--device', type=int_or_str,
    help='input device (numeric ID or substring)')
parser.add_argument(
    '-r', '--samplerate', type=int, help='sampling rate')
parser.add_argument(
    '-c', '--channels', type=int, default=2, help='number of input channels')
parser.add_argument(
    'filename', nargs='?', metavar='FILENAME',
    help='audio file to store recording to')
parser.add_argument(
    '-t', '--subtype', type=str, help='sound file subtype (e.g. "PCM_24")')
parser.add_argument(
    '-b', '--blocksize', type=int, default=2048,help='block size (default: %(default)s)')
parser.add_argument(
    '-q', '--buffersize', type=int, default=20,
    help='number of blocks used for buffering (default: %(default)s)')
args = parser.parse_args()

q = queue.Queue(maxsize=args.buffersize)

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(indata)

def genHeader(sampleRate, bitsPerSample, channels):
    datasize = 2000*10**6
    o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE",'ascii')                                              # (4byte) File type
    o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
    o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
    o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2,'little')                                    # (2byte)
    o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
    o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
    o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
    return o

#..........
STOP = False
#..........

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/myaudio')
def myaudio():
    """Video streaming home page."""
    return render_template('index_back.html')


def gen_frame():
    """Video streaming generator function."""
    while True:
        frame = camera_stream()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') # concate frame one by one and show result
def record():
    rec = currentThread()
    while getattr(rec, "do_run", True):
        with sd.InputStream(samplerate=args.samplerate, device=args.device,
                            channels=args.channels, callback=callback):
            print("record start!")
            while True:
                pass

def gen_audio():
    # wav_header = genHeader(args.samplerate,args.blocksize,args.channels)
    
    # frame = audio_stream(args.filename,samplerate=args.samplerate, device=args.device,
    #                     channels=args.channels, callback=callback, queue = q)
    
    file_number=0
    FILENAME = "./sound/"
    wri = currentThread()
    while getattr(wri, "do_run", True):
        FILENAME_N = FILENAME+str(file_number) +".wav"
        if os.path.exists(os.getcwd()+"/sound/"+str(file_number) +".wav"):
            os.remove(os.getcwd()+"/sound/"+str(file_number) +".wav")

        with sf.SoundFile(FILENAME_N, mode='x', samplerate=args.samplerate,
                          channels=args.channels, subtype=args.subtype) as file:
            # print('#' * 80)
            # print('press Ctrl+C to stop the recording')
            # # print('#' * 80)
            DURATION = 200
            for i in range(DURATION):
                file.write(q.get())
        print(file_number," finished!")
        file_number = file_number+1
        if file_number is 10:
            file_number =0

    # yield (wav_header+frame)
    # return (b'--frame\r\n'
    #        b'Content-Type: audio/wav\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    # gen_audio()

    return Response(gen_frame(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/audio')
def audio():

    return Response()


@app.route('/music/<path:filename>')
def download_file(filename):
    print("///Request**********************************")
    print(request.headers)
    # print(str(request.data))
    print("**********************************")
    resp = send_from_directory('./sound/', filename)
    # resp['Content-Length'] = '105840156'
    return resp


if __name__ == '__main__':
    try:
        import sounddevice as sd
        import soundfile as sf
        import numpy  # Make sure NumPy is loaded before it is used in the callback
        assert numpy  # avoid "imported but unused" message (W0611)

        if args.list_devices:
            print(sd.query_devices())
            parser.exit(0)
        if args.samplerate is None:
            device_info = sd.query_devices(args.device, 'input')
            # soundfile expects an int, sounddevice provides a float:
            args.samplerate = int(device_info['default_samplerate'])
        if args.filename is None:
            args.filename = tempfile.mktemp(prefix='delme_rec_unlimited_',
                                            suffix='.wav', dir='')
        print(os.getcwd())
        wri = Thread(target = gen_audio)
        rec = Thread(target = record)
        rec.start()
        wri.start()
        time.sleep(5)
        app.run(host='localhost', threaded=True)

    except KeyboardInterrupt:
        print('\nRecording finished: ' + repr(args.filename))
        wri.do_run = False
        rec.do_run = False
        wri.join()
        rec.join()
        parser.exit(0)
    except Exception as e:
        parser.exit(type(e).__name__ + ': ' + str(e))




