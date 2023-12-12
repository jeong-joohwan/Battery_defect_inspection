import RPi.GPIO as GPIO
import time
import sys
import os
import glob

GPIO.setmode( GPIO.BCM )
GPIO.setwarnings(False)

con1_port = 16
con2_port = 20

led1 = 12
led2 = 14
led3 = 15

sig1 = 23
sig2 = 26

pulse_start = 0
pulse_end = 0

servo1 = 7
servo2 = 8

SERVO_MAX_DUTY = 12   # 서보의 최대(180도) 위치의 주기
SERVO_MIN_DUTY = 3


GPIO.setup(servo1, GPIO.OUT)
GPIO.setup(servo2, GPIO.OUT)
pwm1 = GPIO.PWM(servo1, 50)
pwm2 = GPIO.PWM(servo2, 50)
pwm1.start(0)
pwm2.start(0)

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def led_init ( led1, led2, led3 ):
    GPIO.setup( led1, GPIO.OUT )
    GPIO.setup( led2, GPIO.OUT )
    GPIO.setup( led3, GPIO.OUT )

def led_on(led_pin):
    GPIO.output(led_pin,True)
    
def led_off(led_pin):
    GPIO.output(led_pin,False)


def conveyor_init():
    GPIO.setup(con1_port, GPIO.OUT)
    GPIO.setup(con2_port, GPIO.OUT)

def main_conveyor_On(port):
    GPIO.output(port, False)
    
def main_conveyor_Off(port):
    GPIO.output(port, True)
    

def Sonar(sig):
    global pulse_start
    global pulse_end
    while True:
        GPIO.setup(sig, GPIO.OUT)
        GPIO.output(sig, False)
        time.sleep(0.5)

        GPIO.output(sig, True)
        time.sleep(0.00001)

        GPIO.output(sig, False)
            
        GPIO.setup(sig, GPIO.IN)
        while GPIO.input(sig) == False:
            pulse_start = time.time()

        while GPIO.input(sig) == True:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration*17000
        print("Distance:{:2f}cm".format(distance))

        return distance

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return round(temp_c, 1)

def setServoPos1(angle) :
    if angle > 180 or angle < 0 :
        return False
    duty = SERVO_MIN_DUTY+(angle*(SERVO_MAX_DUTY-SERVO_MIN_DUTY)/180.0)
    #print("angle: {} to {}(duty)".format(angle, duty))
    pwm1.ChangeDutyCycle(duty)

def setServoPos2(angle) :
    if angle > 180 or angle < 0 :
        return False
    duty = SERVO_MIN_DUTY+(angle*(SERVO_MAX_DUTY-SERVO_MIN_DUTY)/180.0)
    #print("angle: {} to {}(duty)".format(angle, duty))
    pwm2.ChangeDutyCycle(duty)

conveyor_init()
led_init ( led1, led2, led3 )
