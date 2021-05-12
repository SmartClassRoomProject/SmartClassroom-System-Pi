# -*- coding: utf-8 -*-
"""Generate samples with Gstreamer 'appsrc' element in 'push' mode"""

# source is https://gist.github.com/thomasfillon/a63553d85f010bc75b86

# equivalent effect:
# gst-launch-1.0 filesrc location=bird-calls.wav ! wavparse \
# ! audioconvert ! audioresample ! alsasink

# gst-launch-1.0 filesrc location=file.pcm ! audio/x-raw,format=S16BE,channels=2,rate=48000 \
# ! audioconvert ! audioresample ! autoaudiosink


#tcpclientsrc port=5678 host=localhost do-timestamp=true ! application/x-rtp-stream,media=audio,clock-rate=48000,encoding-name=VORBIS ! rtpstreamdepay ! rtpvorbisdepay ! decodebin ! audioconvert ! audioresample ! audio.


#gst-launch-1.0 tcpclientsrc port=5678 host=localhost do-timestamp=true ! "application/x-rtp-stream,media=audio, clock-rate=44100, encoding-name=(string)L16, encoding-params=1, channels=1, payload=96" ! rtpstreamdepay ! rtpL16depay ! audioconvert ! audioresample ! autoaudiosink
import sys
import gi

gi.require_version('Gst', '1.0')
gi.require_version('Gtk', "3.0")
from gi.repository import GObject, GLib, Gst

import numpy as np
import threading
import matplotlib.pyplot as plt

# import librosa
from scipy.io.wavfile import read
# Initialize gobject in a threading environment
# GObject.threads_init()
Gst.init(None)
# Threading is needed to "push" buffer outside the gstreamer mainloop
mainloop_thread = threading.Thread()
mainloop = GLib.MainLoop()
mainloop_thread.mainloop = mainloop
mainloop_thread.run = mainloop_thread.mainloop.run


from Audio import RemoteAudio 
import requests
import time

class Appsrc():

    PIPELINE_SIMPLE = "appsrc name=appsrc ! audio/x-raw ,format=S32LE,channels=1,layout=interleaved,rate=44100 ! audioconvert ! audioresample ! queue ! rtpL24pay ! rtpstreampay ! tcpserversink port=5678 host=192.168.0.177"
    # PIPELINE_SIMPLE = "appsrc name=appsrc ! audio/x-raw ,format=S32BE,channels=1,layout=interleaved,rate=44100 ! audioconvert ! audioresample ! autoaudiosink"
    
    # PIPELINE_SIMPLE = "appsrc name=appsrc ! audio/x-raw-int,rate=44100,chanels=1,width=16 ! tcpclientsink port=5678"
    # PIPELINE_SIMPLE = "appsrc name=appsrc ! audio/x-raw ,format=S32BE,channels=1,layout=interleaved,rate=44100 ! audioconvert ! alawenc ! rtppcmapay ! rtpstreampay ! tcpserversink port=5678"
    # PIPELINE_SIMPLE = "appsrc name=appsrc is-live=true do-timestamp=true ! audio/x-raw,format=S32BE,channels=1,layout=interleaved,rate=44100 ! audioconvert !queue ! audioresample ! vorbisenc ! rtpvorbispay config-interval=1 ! rtpstreampay ! tcpserversink port=5678"
    # PIPELINE_SIMPLE = 'appsrc name=appsrc is-live=true do-timestamp=true ! audio/x-raw,format=S32BE,channels=1,layout=interleaved,rate=44100 ! audioconvert !queue ! audioresample !vorbisenc ! rtpvorbispay config-interval=1 ! rtpstreampay ! tcpserversink port=5678'
    # PIPELINE_SIMPLE = "appsrc name=appsrc ! audio/x-raw,format=S32LE,channels=1,rate=44100,layout=interleaved ! audioconvert ! audioresample ! filesink location=output2.raw"
    # PIPELINE_SIMPLE = "appsrc name=appsrc ! audio/x-raw,format=S32BE,channels=1,rate=44100,layout=interleaved ! audioconvert ! audioresample ! lamemp3enc ! filesink location=test.mp3"

    def __init__(self):
        self.pipeline = Gst.parse_launch(self.PIPELINE_SIMPLE)

        self.buffer_intSize = 44100
        self.DT = self.buffer_intSize / 44100.0
        # self.DT -=  self.DT/5
        # self.buffer_intSize = 128 // 4
        self.buffer_size = self.buffer_intSize*4  # byte
        self.dt = 1.0/44100
        self.prev_time = None
        self.sum_time = 0
        self.num_sum = 0
        self.array = None

        self.prev_time = time.time()
        self.extra = 0


        self.npts = self.buffer_size
        self.remoteAudio = RemoteAudio(self.buffer_intSize)

        self.needs_update = None
        self.the_buf = 0

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message::eos", self._on_eos_cb)
        bus.connect("message::error", self._on_error_cb)

        # appsrc = Gst.ElementFactory.make('appsrc', 'appsrc')
        self.appsrc = self.pipeline.get_by_name("appsrc")
        self.appsrc.connect('need-data', self._on_need_buffer)

        self.buffer = None
        self.buffer = Gst.Buffer.new_allocate(None, self.buffer_size, None)
        self.needs_update = True
        self.pts = 0

    def start(self):
        """ zut """
        self.pipeline.set_state(Gst.State.PLAYING)

    def stop(self):
        """ flute """
        self.pipeline.set_state(Gst.State.PAUSED)

    def _on_need_buffer(self, source, arg0):
        """ Fichtre """
        # duration = self.dt*(10**9)

        # now = time.time()
        # elapsed_time = now - self.prev_time
        # if now - self.prev_time < self.DT:
        #     # print('none',elapsed_time)
        #     buf = np.vstack([0])

        #     self.buffer.fill(0,buf.tobytes())
        #     source.emit("push-buffer", self.buffer)    
        #     return 


 
        
        # print('norm',elapsed_time,self.extra)
        
        buf = np.vstack(self.remoteAudio.remote_read())
        # self.array = buf
        self.buffer.fill(0, buf.tobytes())
        # self.buffer.duration = duration
        # self.pts += duration
        # self.buffer.pts = self.pts
        source.emit("push-buffer", self.buffer)
        # self.prev_time = time.time()
        # print('ddd')
        
    def _on_eos_cb(self, bus, msg):
        """Calback on End-Of-Stream message"""
        # mainloop.quit()
        self.pipeline.set_state(Gst.State.NULL)

    def _on_error_cb(self, bus, msg):
        """Calback on Error message"""
        err, debug_info = msg.parse_error()
        print("Error received from element %s: %s" % (msg.src.get_name(),
                                                      err))
        print("Debugging information: %s" % debug_info)
        # mainloop.quit()

    def get_data(self):
        """ Return the internal buffer"""
        return (self.buffer_size//4,self.npts, self.dt, self.array)


if __name__ == "__main__":
    Gst.init(sys.argv)
    appsrc = Appsrc()

    loop = GLib.MainLoop()
    appsrc.start()
    try:
        res = requests.get('http://192.168.0.218:8081/pcm_run')
        loop.run()
    except KeyboardInterrupt:
        loop.quit()
        res = requests.get('http://192.168.0.218:8081/pcm_stop')
    finally :
        
        # bufsz, npts, dt, resu = appsrc.get_data()
        # # resu = resu/(2**31 - 1)

        # x = np.linspace(0, bufsz, bufsz, endpoint=False)*dt
        # print(x)

        # # compare with output.raw
        # wav = np.fromfile('output2.raw', dtype='<i4', count=bufsz)
        # # wav = wav / (2**31 - 1)

        # plt.subplot(2, 1, 1)
        # markers_on = np.linspace(0, npts, 10, endpoint=False).astype('i4')
        # # plt.plot(x, resu[:bufsz], '-bD', markevery=markers_on)
        # plt.plot(x, resu[:bufsz]) 
        # plt.ylabel("Before Appsrc")
        # plt.subplot(2, 1, 2)
        # plt.plot(x, wav)
        # plt.ylabel("Sent to audio Laew")
        # plt.show()

        appsrc.stop()
        
    

