import RPi.GPIO as GPIO
from flask import Flask,jsonify,request
import time
import requests

app = Flask(__name__)
host = '192.168.0.177'
port = 3005
camera_mode = 0
pin = [26,19,32,23,24]
GPIO.setmode(GPIO.BOARD)
for i in pin :
      GPIO.setup(i,GPIO.OUT)

def onLED(pin) :
      pass

@app.route('/display',methods = ['POST'])
def display() :
      try :
            global camera_mode
            mode = request.json['mode']
            for i in pin :
                  GPIO.output(i,0)
            
            camera_mode = mode
            print(camera_mode)
            GPIO.output(pin[camera_mode],1)
            return jsonify({
                  "msg" : "success",
                  "mode" : camera_mode
            })
      except Exception as e :
            print(e)
            GPIO.output(pin[4],1)
            return jsonify({'msg' : 'fail'})

@app.route('/reset',methods = ['GET'])
def reset():
      try :
            global camera_mode
            camera_mode = 0
            GPIO.cleanup()
            GPIO.setmode(GPIO.BOARD)
      except Exception as error :
            GPIO.output(pin[4],1)

@app.route('/error',methods = ['GET'])
def set_error() :
      try :
            for i in pin :
                  GPIO.output(i,0)
            GPIO.output(pin[4],1)
            return 'success'
      except Exception as error :
            for i in pin :
                  GPIO.output(i,0)
            GPIO.output(pin[4],1)
            return 'success'

if __name__ == "__main__":
      
      # GPIO.setmode(GPIO.BOARD)
      # pin = [32,19,26,24,23]
      # action = [2,1,0,6,5]
      # for i in pin:
      #       GPIO.setup(i,GPIO.OUT)
      #       GPIO.output(i, 1)
      #       time.sleep(1)
      # while True :
      #       time.sleep(1)
      # GPIO.cleanup()
      app.run( host = host, port = port, debug = True)