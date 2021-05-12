from Stepmotor import Stepmotor
import flask
from flask import request, jsonify
from util import *
import time
import RPi.GPIO as GPIO

app = flask.Flask(__name__)
# app.config["DEBUG"] = True

stepMotor_list = []


@app.route("/init_motor",methods=['POST'])
def init_motor():
      global stepMotor_list

      needed = ['ID','gpio']

      if param_check(request,needed) :
            res = {
                  'description' : 'param needed'
            }
            return jsonify(res) , 400

      last_known_ID = int(request.form['ID'])
      gpio_list = request.form['gpio']
      gpio_list = [int(i) for i in request.form['gpio'].split(' ')]

      id = int(len(stepMotor_list))

      if id != last_known_ID :
            print(id,last_known_ID)
            res = {
                  'description' : 'ID do not match' ,
                  'lastID' : id 
            }
            return jsonify(res) , 400

      new_motor = Stepmotor(id = id , gpio = gpio_list)

      stepMotor_list.append(new_motor)

      res = {
            'description' : 'create complete' ,
            'NewMotorID' : id 
      }

      return jsonify(res) , 201

@app.route("/runMotor",methods=['POST'])
def runMotor() :

      global stepMotor_list
      
      needed = ['ID','start_pos','stop_pos']

      if param_check(request,needed) :
            return param_needed()

      if stepMotor_list == [] :
            res = {
                  'description' : 'no motor was created'
            }
            return jsonify(res) , 400

      

      id = int(request.form['ID'])
      start_pos = int(request.form['start_pos'])
      stop_pos = int(request.form['stop_pos'])

      if len(stepMotor_list)-1 < id :
            res = {
                  'description' : 'motor id do not match' ,
                  'motor len' : len(stepMotor_list)
            }
            return jsonify(res) , 400
      
      motor = stepMotor_list[id]
      

      # if int(motor.global_pos) != start_pos :
      #       print(id,motor.global_pos)
      #       res = {
      #             'description' : 'last_post_do_not_match' ,
      #             'current_pos' : motor.global_pos 
      #       }
      #       return jsonify(res) , 400
      
      tmp_pos = int(motor.global_pos)

      motor.drive_(stop_pos-start_pos)

      res = {
            'description' : 'drive motor complete' ,
            'start_pos' : tmp_pos ,
            'stop_pos' : int(motor.global_pos) 
      }

      return jsonify(res) , 200

@app.route("/disableMotor",methods=['POST'])
def disable_moter():

      needed = ['ID']
      if param_check(request,needed):
            return param_needed()
      
      id = get_id(request)
      if id != None :
            stepMotor_list[id].disable_moter()
      
      res = {
            'description' : 'disable complete' ,
            'MotorID' : id 
      }

      return jsonify(res) , 201

@app.route("/getMotorList",methods=['GET'])
def getMotorList():
      if stepMotor_list == []:
            res = {
                  'description' : 'no motor was created'
            }
      else :
            id_list = [str(i) for i in stepMotor_list]
            res = {
                  'id_list' : ' '.join(id_list),
                  'description' : 'OK'
            }

      return jsonify(res)
            
@app.route("/test",methods=['GET'])
def test():
      motor = stepMotor_list[1]
      motor.calibate()
      res = {'test':'test Done'}
      
      return jsonify(res)

@app.route("/reCal",methods=['GET'])
def reCal():
      global stepMotor_list
      count = 0
      for i in stepMotor_list :
            i.calibate(dir = count)
            count += 1
      
      res = {'asdsa':'Done'}
      return jsonify(res)





if __name__ == "__main__":
      try :
            GPIO.setmode(GPIO.BOARD)
            # control_pins = [31,33,35,37]
            # # control_pins = [36]
            # for pin in control_pins:
            #       # print(pin)
            #       GPIO.setup(pin, GPIO.OUT)
            #       GPIO.output(pin, 0)

            # n = 0

            # for i in range(200):
            #       GPIO.output(31,0)
            #       GPIO.output(33,n)

            #       n = (n+1)%2
            #       time.sleep(0.00051)

            # while True:
            #       time.sleep(1)
            # GPIO.cleanup()
            new_motor = Stepmotor(id = 0 ,time_interval = 0.0005, gpio = [35,37],sensor_pin = 38, distance = 440)
            # print(new_motor.control_pins)
            new_motor.calibate(dir = 0)
            stepMotor_list.append(new_motor)
            new_motor = Stepmotor(id = 1 ,time_interval = 0.0005, gpio = [31,33],sensor_pin = 40,distance = 360)
            new_motor.calibate(dir = 1)
            stepMotor_list.append(new_motor)
            app.run(host='192.168.0.177',port=5001,threaded=False)
      finally :
            GPIO.cleanup()
            # if stepMotor_list != [] :
            #       for i in stepMotor_list :
            #             i.gpio_cleanUp()