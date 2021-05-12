import requests
from flask import Flask , request , jsonify
import time
from datetime import datetime

app = Flask(__name__)

camera_mode = 3
# Mode 0 = NONE AND RESET ZOOM // STAND FACING AND SPREAD ARMS
# Mode 1 = ZOOM LEFT (LEFT OF BOARD)
# Mode 2 = ZOOM RIGHT (RIGHT OF BOARD)
# Mode 3 = TRACKING // RAISE HANDS
# Mode 4 = Error
# Mode 5 = WRITTING RIGHT BORAD (ZOOM RIGHT)
# Mode 6 = WRITTING LEFT BOARD (ZOOM LEFT)


MID_FRAME_X = 1280/2
MID_FRAME_Y = 720/2
current_pos_x = 0
current_pos_y = 0
prev_time_x = 0
sumError_x = 0
prev_error_x = 0
Kp_x = .4
Ki_x = 0
Kd_x = 0
prev_time_y = 0
sumError_y = 0
prev_error_y = 0
Kp_y = .1
Ki_y = 0
Kd_y = 0
ts_x = 5
ts_y = 2

def req_Pose() :
    url = 'http://localhost:5000/upload-images'
    img = {"image" : open("frame"+"0"+".jpg",'rb')}
    print(img)
    res = requests.post(url,files = img)
    return res.json()



def PID(target , value ,axis):
    if axis == 'X' :
        global prev_time_x
        global sumError_x
        global prev_error_x
        global Kp_x
        global Ki_x
        global Kd_x
        global ts_x

        current_time = datetime.now()

        if prev_time_x == 0 :
            prev_time_x = datetime.now()
            current_time = datetime.now()

        time_diff = current_time - prev_time_x
        time_diff = time_diff.total_seconds() * 1000
        
        error = target - value
        sumError_x = error * time_diff
        rateError = (error - prev_error_x)/time_diff
        adjust = error * Kp_x + Ki_x * sumError_x + Kd_x * rateError


        print('error',error)
        print('time_diff',time_diff)
        print('rateError',rateError)

        prev_time_x = current_time
        prev_error_x = error
        print('aJJJJJ',adjust)
        if  -ts_x <= adjust and adjust <= ts_x :
            return 0
        return adjust
    if axis == 'Y' :
        global prev_time_y
        global sumError_y
        global prev_error_y
        global Kp_y
        global Ki_y
        global Kd_y
        global ts_y
        current_time = datetime.now()

        if prev_time_y == 0 :
            prev_time_y = datetime.now()
            current_time = datetime.now()

        time_diff = current_time - prev_time_y
        time_diff = time_diff.total_seconds() * 1000
        
        error = target - value
        sumError_y = error * time_diff
        rateError = (error - prev_error_y)/time_diff
        adjust = error * Kp_y + Ki_y * sumError_y + Kd_y * rateError


        print('error',error)
        print('time_diff',time_diff)
        print('rateError',rateError)
        
        prev_time_y = current_time
        prev_error_y = error
        if  -ts_y <= adjust and adjust <= ts_y :
            return 0
        return adjust

def tracking(mid_point_x,mid_point_y):
    global current_pos_x
    global current_pos_y

    aj_x = PID(MID_FRAME_X,mid_point_x,'X')
    aj_y = PID(MID_FRAME_Y,mid_point_y,'Y')
    print('XXXX',aj_x)
    formData_x = {
        "ID" : 0 ,
        'start_pos' : current_pos_x ,
        'stop_pos' : current_pos_x + int(aj_x)
    }
    formData_y = {
        "ID" : 1 ,
        'start_pos' : current_pos_y ,
        'stop_pos' : current_pos_y + int(aj_y)
    }
    res_x = requests.post('http://192.168.0.177:5001/runMotor',data = formData_x)
    res_y = requests.post('http://192.168.0.177:5001/runMotor',data = formData_y)
    print(res_x.json())
    print(res_y.json())

    if 'stop_pos' in res_x.json() :
        current_pos_x = res_x.json().get('stop_pos')
    if 'stop_pos' in res_y.json() :
        current_pos_y = res_y.json().get('stop_pos')

    return jsonify('done')

def req_Zoom(command) :
    url = 'http://192.168.0.177:3004/zoomcommand'
    ip = '192.168.0.177'
    port = 8554
    path = 'test'
    if command == 1:
        top = 0
        left = 450
        right = 50
        bottom = 200
        msg = 'zoom_left'
    elif command == 2:
        top = 0
        left = 50
        right = 450
        bottom = 200
        msg = 'zoom_right'
    elif command == 0 :
        top = 0
        left = 0
        right = 0 
        bottom = 0
        msg = 'zoom_out'
    elif command == 3 :
        msg = 'tracking'

    if command != 3 :
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

def displayMode(camera_mode):
    data = {
        "mode" : camera_mode
    }
    res_display = requests.post('http://192.168.0.177:3005/display',json = data)
    # print(res_display.text)
    return jsonify({'msg' : res_display.text})
@app.route("/control",methods=['POST'])
def control():
    try :
        global camera_mode
        points = request.json['points']
        # print(request.json)
        leftShoulder_x = float(points['leftShoulder_x'])
        leftShoulder_y = float(points['leftShoulder_y'])

        # leftShoulder_x = float(request.form['leftShoulder_x'])
        # leftShoulder_y = float(request.form['leftShoulder_y'])

        rightShoulder_x = float(points['rightShoulder_x'])
        rightShoulder_y = float(points['rightShoulder_y'])

        # rightShoulder_x = float(request.form['rightShoulder_x'])
        # rightShoulder_y = float(request.form['rightShoulder_y'])


        mid_point_x = (leftShoulder_x + rightShoulder_x) / 2
        mid_point_y = (leftShoulder_y + rightShoulder_y) / 2

        classification_result = request.json['classification_result']
        if camera_mode == None :
            camera_mode = 0
            req_Zoom(0)
        elif camera_mode == 0 or camera_mode == 3:
            # pass
            if classification_result == 'left_hand' :
                camera_mode = 1
                req_Zoom(1)
                #zoom left
            elif classification_result == 'right_hand' :
                camera_mode = 2
                req_Zoom(2)
                #zoom right
            elif classification_result == 'w_righthand_rightboard' or classification_result == 'w_lefthand_rightboard' :
                camera_mode = 5
                req_Zoom(2)
                #zoom right
            elif classification_result == 'w_righthand_leftboard' or classification_result == 'w_lefthand_leftboard' :
                camera_mode = 6
                req_Zoom(1)
                #zoom left
            elif classification_result == 'raise_hand' :
                req_Zoom(0)
                camera_mode = 3
                #tracking
            elif classification_result == 'spread_arms' :
                camera_mode = 0

                res_zoom = req_Zoom(0)
                res_reset = requests.get('http://192.168.0.177:5001/reCal')
                #zoom out
            # res_zoom = req_Zoom(camera_mode)
        elif camera_mode != 0 :
            if classification_result == 'spread_arms' :
                camera_mode = 0

                res_zoom = req_Zoom(0)
                formData_x = {
                    "ID" : 0 ,
                    'start_pos' : current_pos_x ,
                    'stop_pos' : 0
                }
                formData_y = {
                    "ID" : 1 ,
                    'start_pos' : current_pos_y ,
                    'stop_pos' : 0
                }
                # res_x = requests.post('http://192.168.0.177:5001/runMotor',data = formData_x)
                # res_y = requests.post('http://192.168.0.177:5001/runMotor',data = formData_y)
                #zoom out
            elif classification_result == 'raise_hand' :
                req_Zoom(0)
                camera_mode = 3
        displayMode(camera_mode)
        print(camera_mode)
        if camera_mode == 3 :
            res = tracking(mid_point_x,mid_point_y)
        return 'success'
    except Exception as e:
        camera_mode = 4
        displayMode(camera_mode)
        print(e)
        return 'error'

def goLeft():
    pass

def goRight():
    pass
 

if __name__ == '__main__' :

    
    app.run(host='192.168.0.177',port=5002,threaded=False,debug = False)

    # global prev_time

    # res = req_Pose()

    # leftShoulder_x = res['leftShoulder_x']
    # leftShoulder_y = res['leftShoulder_y']

    # rightShoulder_x = res['rightShoulder_x']
    # rightShoulder_y = res['rightShoulder_y']


    # mid_point_x = (leftShoulder_x + rightShoulder_x) / 2
    # mid_point_y = (leftShoulder_y + rightShoulder_y) / 2

     
    # current_time = datetime.now()
    # prev_time = current_time

    
