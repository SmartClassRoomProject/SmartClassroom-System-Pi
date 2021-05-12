import requests
from flask import Flask , request , jsonify
import cv2
import time
import socket
import os , re
from uuid import getnode as get_mac
from multiprocessing.dummy import Pool
import json

accList = ['nose', 'leftEye', 'rightEye', 'leftEar', 'rightEar', 'leftShoulder', 'rightShoulder', 'leftElbow', 'rightElbow', 'leftWrist', 'rightWrist', 'leftHip', 'rightHip', 'leftKnee', 'rightKnee', 'leftAnkle', 'rightAnkle']
# image = {'image': open('./images/single.jpeg','rb')}
stream = True
app = Flask(__name__)
host = '192.168.0.177'
# host = 'localhost'
port = 3000
stream = False
url_pose_service = 'http://161.246.5.161:8101/'
url_class_service = 'http://161.246.5.161:8102/'
url_camera_control_service = 'ip'
url_zoom_service = 'ip'
active_stream = {}
with open('connection.txt') as json_file :
    data = json.load(json_file)
    for c in data : 
        active_stream[c] = data[c]

### hand check func
def check_Service() :
    def get_pose() :
        res = requests.get(url_pose_service)
        return 'connect'
    def get_class() :
        res = requests.get(url_class_service)
        return 'connect'
    
    def get_camera_control() :
        res = requests.get(url_camera_control_service)
        return 'connect'

    def get_zoom() :
        res = requests.get(url_zoom_service)
        result.append(res.json())
        return 'connect'

    try :
        get_pose()
        get_class()
        # get_camera_control()
        # get_zoom()
        return True
    except :
        return False

### function request
def purge(dir, pattern):
    for f in os.listdir(dir):
        if re.search(pattern, f):
            os.remove(os.path.join(dir, f))

def req_Pose(image) :
    url = url_pose_service + 'upload-images'
    # url = 'http://localhost:3001/upload-images'
    res = requests.post(url,files = image)
    return res.json()

def req_Class(pose) :
    url = url_class_service + 'prediction'
    # url = 'http://localhost:3002/prediction'
    formData = { 'data' : pose }
    res = requests.post(url,json = formData)
    return res.json()

def req_Zoom(classification) :
    url = 'http://192.168.0.177:3004/zoomcommand'
    ip = '192.168.0.177'
    port = 8554
    path = 'test'
    if classification == 'right_hand' :
        top = 0
        left = 270
        right = 50
        bottom = 200
        msg = 'zoom_right'
    elif classification == 'left_hand' :
        top = 0
        left = 50
        right = 270
        bottom = 200
        msg = 'zoom_left'
    elif classification == 'raise_hand' :
        top = 0
        left = 0
        right = 0
        bottom = 0
        msg = 'tracking'
    elif classification == 'spread_arms' :
        top = 0
        left = 0
        right = 0
        bottom = 0
        msg = 'zoom_out'
    else :
        msg = 'not_zoom'

    if msg != 'not_zoom' :
        formData = {
            "top" : str(top),
            "left" : str(left),
            "right" : str(right),
            "bottom" : str(bottom),
            "ip" : ip,
            "port" : port,
            "path" : path
        }
        res = requests.post(url,json = formData)
    return msg

def process_zoom(classification) :
    print('classification = ' + classification[0])
    res_zoom = req_Zoom(classification[0])
    return res_zoom
### API ###
@app.route('/',methods = ['POST'])
def active() :
    if request.json['mac_address'] not in active_stream :
        data = {}
        ip_address = request.remote_addr
        data['mac_address'] = request.json['mac_address']
        data['ip'] = ip_address
        data['room'] = request.json['room']
        data['status'] = 'active'
        data['stream_url'] = request.json['url']
        active_stream[str(request.json['mac_address'])] = data
        print(active_stream)
        with open('connection.txt','w') as outfile :
            json.dump(active_stream,outfile)
    else :
        active_stream[request.json['mac_address']]['status'] = 'active'
    
    return jsonify(active_stream)

@app.route('/', methods = ['GET'])
def setup_stream() :
    # req = request.json
    # data_form = {"ip" : req[ip] , }
    # active_stream[req['room']] = 'active'
    check = check_Service()
    print(check)
    if check :
        global stream
        stream = True
        purge('./','frame')
        return jsonify("Ready")
    else :
        return jsonify("Service Not Ready")

@app.route('/start',methods = ['POST'])
def start_stream() :
    # ip = '192.168.0.177'
    # room = '811'
    mac_address = str(request.json['mac_address'])
    ip = request.remote_addr
    info = active_stream[mac_address]
    room = info['room']
    url = info['stream_url']
    classification_result = []
    try :
        time.sleep(5)
        # Connection with RTSP from Raspberry PI
        s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip,8554))
        print('connect!')
        
        # Use Camera from Computer
        # vid = cv2.VideoCapture(0)
        
        # Use Camera from Raspberry PI
        vid = cv2.VideoCapture(url)
        # time.sleep(4)
        count = 0
        all_out = []
        # while 1 :
        #     ret,frame = vid.read()
        #     cv2.imwrite("frame%d.jpg" % count,frame)
        #     count += 1
        while active_stream[mac_address]['status'] == 'streaming':
            try :
                ret, frame = vid.read()
                if ret == True:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    # cv2.imshow('frame',gray)
                    if count%4 == 0:
                        cv2.imwrite("./uploads/frame_"+str(mac_address)+"_%d.jpg" % count,frame)
                        img = {"image" : open("./uploads/frame_"+str(mac_address)+'_'+str(count)+".jpg",'rb')}
                        # img = {"image" : cv2.read(frame)}
                        pose = req_Pose(img)
                        if pose['msg'] == 'nobody' :
                            print('Nobody in frame')
                            classification_result = []
                            all_out = []
                            time.sleep(0.1)
                        elif pose['msg'] == 'detected' :
                            # print(pose['pose']['nose_score'])
                            point = pose['pose']
                            all_out.append(point)
                        if len(all_out) == 3 :
                            # print(all_out)
                            res_class = req_Class(all_out)

                            all_out = []
                            classification_result.append(res_class['prediction'])
                            formData = {}
                            formData['points'] = point
                            formData['classification_result'] = res_class['prediction']
                            print(res_class['prediction'])
                            req_control = requests.post('http://192.168.0.177:5002/control',json = formData )
                            # print(req_control.text)
                            # print(res_class['prediction'])
                        elif len(all_out) > 3 :
                            all_out = []
                            classification_result = []
                        # print('classification list : ' + classification_result)
                        if len(classification_result) >= 1 :
                            # req_control = requests.post('http://192.168.0.177:5001/control')
                            # print(zoom_result)
                            classification_result = []
                    # purge('./uploads/','frame_'+mac_address)
                    count += 1
                else:
                    break
            except Exception as error:
                status = check_status()
                res_set_error = requests.get('http://192.168.0.177:3005/error')
                print(error)
        # purge('./uploads/','frame_'+mac_address)
        vid.release()
        # cv2.destroyAllWindows()
        return jsonify('Connection End.')
    except :
        purge('./','frame')
        print('fail')
        res_set_error = requests.get('http://192.168.0.177:3005/error')
        return jsonify('fail')

@app.route('/startstream',methods = ['POST'])
def start() :
    mac_address = str(request.json['mac_address'])
    print(active_stream)
    if mac_address in active_stream :
        active_stream[mac_address]['status'] = 'streaming'
        if check_Service() :
            purge('./uploads/','frame_'+mac_address)
            return jsonify({'msg':'Ready for Stream'})
        else :
            return jsonify({'msg':'Error'})
    else :
        return 'fail'
# @app.after_request
# def after_stream_request(response):
    
#     return response
@app.route('/endstream',methods = ['POST'])
def end_stream() :
    mac_address = str(request.json['mac_address'])
    # global stream
    # stream = False
    ip = request.remote_addr
    active_stream[mac_address]['status'] = 'active'
    return jsonify('End.')

@app.route('/classification',methods = ['POST'])
def classification():
    if request.files :
        file = request.files['image']
        file.save('./uploads/'+file.filename)
        img = {"image" : open('./uploads/'+file.filename,'rb')}
        pose = req_Pose(img)
        if pose['msg'] == 'nobody' :
            print('Nobody in frame')
            return jsonify({"msg" : "Nobody in Picture"})
        elif pose['msg'] == 'detected' :
            # print(pose['pose']['nose_score'])
            if pose['pose']['nose_score'] != 0 :
                out = []
                for i in accList :
                    out.append(pose['pose'][i])
                for i in accList :
                    out.append(pose['pose'][i + '_score'])
                out.append(pose['pose']['W_EBleft'])
                out.append(pose['pose']['W_EBright'])
                all_out = []
                for i in range(5):
                    all_out.append(out)
                result = req_Class(all_out)
                if result['result'] != 'fail' :
                    print(result['prediction'])
                    return jsonify(result)
                else :
                    print('fail classification')
                    return jsonify(result)
            else :
                print('stand_back')
                return jsonify({"prediction" : "stand_back"})
    else :
        return jsonify({'msg' : 'No such files'})

@app.route('/status',methods = ['GET'])
def check_status():
    for i in active_stream :
        url = 'http://' + str(active_stream[i]['ip']) + ':3003/'
        try :
            res = requests.get(url).json()
            # print(res)
            if res['msg'] == 'success' :
                if active_stream[i]['status'] != 'streaming' :
                    active_stream[i]['status'] = 'active'
            else :
                active_stream[i]['status'] = 'offline'
        except :
            active_stream[i]['status'] = 'offline'
    with open('connection.txt','w') as outfile :
        json.dump(active_stream,outfile)
    return jsonify(active_stream)

if(__name__ == '__main__'):
    app.run( host = host, port = port, debug = True, threaded = True)