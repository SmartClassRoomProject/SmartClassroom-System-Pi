
import RPi.GPIO as GPIO
import time

class Stepmotor : 

      def __init__(self,id = 0,gpio = [],time_interval = 0.005,stepPerRound = 200,sensor_pin = 40 ,distance = 0):
            GPIO.setmode(GPIO.BOARD)
            self.update_interval = 100 #100step 1 update
            self.stepPerRound = int(stepPerRound)
            self.time_interval = time_interval
            self.id = id
            self.sensor_pin = sensor_pin
            self.distance = distance
            # print(self.sensor_pin)
            GPIO.setup(self.sensor_pin,GPIO.IN)

            self.halfstep_seq = [
                  [1,0,0,0],
                  [1,1,0,0],
                  [0,1,0,0],
                  [0,1,1,0],
                  [0,0,1,0],
                  [0,0,1,1],
                  [0,0,0,1],
                  [1,0,0,1]
            ]
            # self.fullstep_seq = [
            #       [1,0,0,0],
            #       [0,0,0,1],
            #       [0,1,0,0],
            #       [0,0,1,0]
            # ]

            self.fullstep_seq = [
                  [1,0,0,0],
                  [0,1,0,0],
                  [0,0,1,0],
                  [0,0,0,1]
            ]

            self.control_pins = gpio
            self.global_pos = 0.0 # theta

            for pin in self.control_pins:
                  # print(pin)
                  GPIO.setup(pin, GPIO.OUT)
                  GPIO.output(pin, 0)

      def set_param(self,gpio = None,time_interval = None,stepPerRound = None,update_interval = None):
            self.control_pins = gpio if gpio != None else self.control_pins
            self.time_interval = time_interval if time_interval != None else self.time_interval
            self.stepPerRound = float(stepPerRound) if stepPerRound != None else self.stepPerRound
            self.update_interval = update_interval if update_interval != None else  self.update_interval
            # self.gpio = gpio if gpio != None
            out = 'Gpio ' + str(self.control_pins) + '\n'
            out += 'Time interval ' + str(self.time_interval) + '\n'
            out += 'Step Per Round ' + str(self.stepPerRound) + '\n'
            out += 'Update interval ' + str(self.update_interval) + '\n'
            print(out)
            return out


      def drive_forward(self,num_step): # 2,048 x 2 per round

            
            progress = 0
            current_full = int(self.global_pos) 
            GPIO.output(self.control_pins[0],0)
            for step in range(num_step):

                  progress += 1
                  if progress % 100 == 0:
                        print('progess : ',progress*100/num_step,'%',sep = '')

                  GPIO.output(self.control_pins[1],abs(current_full%2))

                  current_full += 1
                  time.sleep(self.time_interval)
                  
                  
            self.global_pos += int(num_step)
            # print('progess : 100%')
            return 'done_half_step_forward'

      def drive_backward(self,num_step): # 2,048 x 2 per round
            
            progress = 0
            current_full = int(self.global_pos) 
            GPIO.output(self.control_pins[0],1)
            for step in range(num_step):

                  progress += 1
                  if progress % 100 == 0:
                        print('progess : ',progress*100/num_step,'%',sep = '')

                  current_full -= 1
                  GPIO.output(self.control_pins[1],abs(current_full%2))
                  time.sleep(self.time_interval)
                  
                  
            
            self.global_pos -= int(num_step)
            # print('progess : 100%')
            return 'done_half_step_backward'

      def drive_(self,step):
            # step = (float(theta)*self.stepPerRound*2) / 360.0 # T x step / 360
            # self.disable_moter()
            # time.sleep(.01)
            print('drive half step : ',step,sep = '')
            if int(step) > 0 :
                  self.drive_forward(int(step))
                  # self.drive_fullstep_forward(abs(int(step)))
            else :
                  self.drive_backward(abs(int(step)))
                  # self.drive_fullstep_backward(abs(int(step)))

            self.disable_moter()

            return 'done drive_\n'

      def calibate(self,dir=0):
            # while True:
            #       print(GPIO.input(self.sensor_pin))
            #       time.sleep(0.01)
            count = 0
            while not GPIO.input(self.sensor_pin) :
                  # print(GPIO.input(self.sensor_pin))
                  if dir == 0:
                        self.drive_forward(1)
                  else :
                        self.drive_backward(1)
                  count += 1 
                  time.sleep(self.time_interval)
            
            print(count)
            if dir == 0:
                  self.drive_backward(self.distance)
            else :
                  self.drive_forward(self.distance)
            # self.drive_backward(self.distance)

      def disable_moter(self):
            for pin in self.control_pins:
                  GPIO.output(pin,0)

      def gpio_cleanUp(self):
            GPIO.cleanup()

      def __str__(self):
            return str(self.id)


if __name__ == '__main__':
      try :
            motor = Stepmotor(gpio = [7,11,13,15],time_interval=0.001)
            # motor.drive_halfstep(4096)
            motor.set_param()
            motor.drive_theta(10000)
            motor.disable_moter()
            GPIO.cleanup()

      except KeyboardInterrupt :
            GPIO.cleanup()
      
