import sys
import gi
import requests
from flask import Flask , jsonify , request
from werkzeug.utils import secure_filename
from uuid import getnode as get_mac

app = Flask(__name__)
host = '192.168.0.177'
port = 3003
room = '811'
server_ip = 'http://192.168.0.177'
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject , GLib
mac = get_mac()
stream = True
loop = GLib.MainLoop()
Gst.init(None)

@app.route('/',methods = ['GET'])
def handcheck() :
    return jsonify({'msg' : 'success'})

@app.route('/streamrtsp', methods=['POST'])
def stream():
    class MyFactory(GstRtspServer.RTSPMediaFactory):
        def __init__(self,desc_str):
            GstRtspServer.RTSPMediaFactory.__init__(self)
            self.desc=desc_str

        def do_create_element(self,url):
            print(self.desc)
            self.bin =  Gst.parse_launch(self.desc)
            return self.bin 

    class GstServer(object):
        def __init__(self):
            self.server = GstRtspServer.RTSPServer()
            self.server.attach(None)
            self.server.connect('client-connected',self.do_client_connected)

        def add_source(self,path,desc_str):
            self.f = MyFactory(desc_str)
            self.f.set_shared(True)
            m = self.server.get_mount_points()
            m.add_factory(path, self.f)

        def do_client_connected(self, serverCtx, client):
            print("-->******************")
            print("Client is connected")
            print(client)
            client.connect("set-parameter-request", self.do_set_parameter_request)
            print("-->******************")

        def do_set_parameter_request(self, client, serverCtx):
            print("-->******************")
            print("Client is set parameter request")
            print("Request is:")
            result, data = serverCtx.request.get_body()
            params = data.decode("utf-8").split("\x00")[0].split(",")
            print(params)
            # if params[0] == "zoom":
            print("Valid set parameter")
            # print(params[0])
            # print(params[1])
            # print(params[2])
            # print(params[3])

            crop_video = self.f.bin.get_by_name('crop-video')
            crop_video.set_property('top',int(params[0]))
            crop_video.set_property('left',int(params[1]))
            crop_video.set_property('right',int(params[2]))
            crop_video.set_property('bottom',int(params[3]))
            # print(params[0], ":", params[1])
            print("--> zoom done! ******************")


    s_src = 'v4l2src device=/dev/video0 ! video/x-raw,rate=30,width=1280,height=720 ! videocrop name=crop-video ! videoconvert ! video/x-raw,format=I420'
    # s_src2 = 'v4l2src device=/dev/video0 ! video/x-raw,rate=30,width=1280,height=720 ! videocrop name=crop-video ! videoconvert ! video/x-raw,format=I420'
    # s_src1 = 'alsasrc device=plughw:0,0  ! audio/x-raw,channels=1,rate=48000 ! audioconvert ! opusenc ! rtpopuspay  name=pay1 pt=97'

    s_h264 = "x264enc tune=zerolatency"

    #pipeline_str = "( {s_src} ! queue max-size-buffers=1 name=q_enc ! {s_h264} ! rtph264pay name=pay0 pt=96 )".format(**locals())
    str2 = "( {s_src} ! queue max-size-buffers=1 name=q_enc ! {s_h264} ! rtph264pay name=pay0 pt=96 )".format(**locals())
    # audio="( {s_src1})".format(**locals())

    s = GstServer()
    s.add_source('/test',str2)
    # s.add_source('/audio',audio)

    if request.json:
        command = request.json['command']
        print(command)    
    
    if command == 'start' : 
        print('Server Started')
        res = requests.post(server_ip+':3000/startstream',json = {'mac_address' : mac}).json()
        print(res)
        if res['msg'] == 'Ready for Stream' :
            try :
                requests.post(server_ip+':3000/start',json = {'mac_address' : mac} ,timeout = 0.01)
            except requests.exceptions.ReadTimeout :
                loop.run()
        else :
            print('Error')
    
    if command == 'stop' :
        requests.post(server_ip+':3000/endstream',json = {'mac_address' : mac})
        loop.quit()
    
    loop.quit()
    return jsonify('End Stream.')
        
@app.route('/end',methods = ['GET'])
def end():
    requests.post(server_ip+':3000/endstream',json = {'mac_address' : mac})
    loop.quit()
    return jsonify({'msg':'End'})

if __name__ == '__main__':
    data = { 'url' : 'rtsp://'+host+':8554/test', 'room' : room , 'mac_address' : mac}
    res = requests.post(server_ip+':3000/',json = data)
    # print(res.text)
    app.run(host = host,port = port,debug = True)#,threaded=True)

    