from flask import Flask , jsonify , request
from werkzeug.utils import secure_filename
import socket 


app = Flask(__name__)
host = '192.168.0.177'
port = 3004

@app.route('/zoomcommand', methods=['POST'])
def zoom():
    # print('test')
    # print(request.json['left'])
    # return jsonify(request.json)

    lenght = 0
    if request.json:
        left_crop = request.json['left']
        right_crop = request.json['right']
        top_crop = request.json['top']
        buttom_crop = request.json['bottom']
        ip = request.json['ip']
        port = request.json['port']
        path = request.json['path']
        lenght += len(left_crop)+len(right_crop)+len(top_crop)+len(buttom_crop)+3
        print(lenght)
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip,port))

    setupParameter = "SET_PARAMETER rtsp://"+ip+'/'+path+" RTSP/1.0\r\nCSeq: 1\r\nContent-length: "+str(lenght)+"\r\nContent-type: text/parameters\r\n\r\n"+top_crop+","+left_crop+","+right_crop+","+buttom_crop+"\r\n\r\n"

    s.send(bytes(setupParameter, 'utf-8'))

    s.shutdown(socket.SHUT_RDWR)
    s.close()
    lenght = 0
    # print(request.json['left'])
    return jsonify({'msg' : 'zoom success'})

if __name__ == '__main__':
    app.run(host = host,port = port,debug = False,threaded = True)