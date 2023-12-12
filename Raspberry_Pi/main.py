import socket
import re
import math
import time
from datetime import datetime, timedelta
import random
import numpy
import RPi.GPIO as GPIO
import cv2
import numpy as np
import base64

from Class_Def import *
from module import *
#from open_cv import *

HOST = '192.168.0.118'
PORT = 9000

font = cv2.FONT_HERSHEY_COMPLEX
Unit_horizon = []
Unit_vertical = []
Unit_hpass = []
Unit_vpass = []

p1=[]
p2=[]
p3=[]
p4=[]
lot = 0
hStandard = 0.0
vStandard = 0.0

count = 0
Hadjust = 0
Vadjust = 0

### open_cv 스크립트 변수들
p_list = []
dot1=[]
dot2=[]
dot3=[]
dot4=[]
imgstring = ''
temperature = 0
### open_cv 스크립트 변수들 2020-11-03 옮김
hunpassCount = 0
vunpassCount = 0
a=0
TotalunpassCount = 0
time1 = 0
time2 = 0
dateGap = 0

def opencapture(count):
    global img
    global imgstring
    cap = cv2.VideoCapture(-1)
    
    while True:
        ret, img = cap.read()  # Read 결과와 frame
        img = img[170:450, 40:600]
        cv2.imshow("Battery_live", img)
        cv2.waitKey(1)
        if not ret:
            break
        print("Image " + str(count) + "saved")
        file = '/home/pi/project/' + str(count) + '.jpg'
        #file = '/home/pi/project/' + 'CaptureTest'+'.jpg'
        cv2.imwrite(file, img)
            
        img2 = cv2.imread(file, cv2.IMREAD_COLOR)
        img3 = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
        _, threshold = cv2.threshold(img3, 150, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        p_list.clear()
        for cnt in contours:

            epsilon = 0.02 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            cv2.drawContours(img2, [approx], 0, (0, 0, 255), 1)

            n = approx.ravel()
            i = 0

            for j in n:
                if (i % 2 == 0):
                    x = n[i]
                    y = n[i + 1]
                    string = str(x) + ", " + str(y)
                    cv2.putText(img2, string, (x, y), font, 0.5, (0, 0, 255))
                    string_list = string.split(",")
                    string_list = list(map(int, string_list))
                    p_list.append(string_list)
                i = i + 1
        #time.sleep(0.5)
        if len(p_list)==4:
            cv2.imshow('Battery_(x, y)', img2)
            cv2.imwrite(file, img2)
            res = cv2.resize(img2,(762,461))
            cv2.imwrite(file, res)
            image = open(file,'rb')
            image_read = image.read()
            image_64_encode = base64.encodebytes(image_read)
            imgstring = b'<sof>' + image_64_encode + b'<eof>'
            return p_list
        else:
            p_list.clear()
            continue
        break
    
def calculate(count):   #start를 calculate로 바꿈
    global imgstring
    global hStandard
    global vStandard
    global TotalunpassCount
    global dateGap
    Result_horizon, Result_vertical = Dot_Distance(p1[count][0], p1[count][1], p2[count][0], p2[count][1], p3[count][0], p3[count][1], p4[count][0], p4[count][1])
    Unit_horizon.append(Result_horizon)
    Unit_vertical.append(Result_vertical)
    
    Result_hpass = Unit_Defect(hStandard, Result_horizon)
    Result_vpass = Unit_Defect(vStandard, Result_vertical)
    temperature = read_temp()
    #temperature = '26.5'
    if Result_hpass == 1 and Result_vpass == 1:
        led_on(led2) #green
        setServoPos1(10)
        time.sleep(1)
        setServoPos2(165)
        time.sleep(1)
    elif Result_hpass == 1 and Result_vpass == 0: #세로만 불량
        led_on(led3) #red
        setServoPos1(10)
        time.sleep(1)
        setServoPos2(125)
        TotalunpassCount+=1
        time.sleep(1)
    elif Result_hpass == 0 and Result_vpass == 1: #가로만 불량
        led_on(led3) #red
        setServoPos1(45)
        time.sleep(1)
        setServoPos2(165)
        TotalunpassCount+=1
        time.sleep(1)
    elif Result_hpass == 0 and Result_vpass == 0: #가로, 세로 둘다 불량
        led_on(led3) #red
        setServoPos1(155)
        time.sleep(1)
        setServoPos2(80)
        TotalunpassCount+=1
        time.sleep(1)
    time.sleep(0.3)
    
    #Result_pass
    Unit_hpass.append(Result_hpass)
    Unit_vpass.append(Result_vpass)
    print('TOCUnit_no'+str(count+1)+","+'Unit_horizon'+str(Result_horizon)+","+'Unit_vertical'+str(Result_vertical)+","+'Unit_hpass'+str(Result_hpass)+","+'Unit_vpass'+str(Result_vpass)+","+'TEMP'+str(temperature)+","+'Unit_date'+str(Date)+","+'GO')
    send_dp = 'TOCUnit_no'+str(count+1)+","+'Unit_horizon'+str(Result_horizon)+","+'Unit_vertical'+str(Result_vertical)+","+'Unit_hpass'+str(Result_hpass)+","+'Unit_vpass'+str(Result_vpass)+","+'TEMP'+str(temperature)+","+'Unit_date'+str(Date)+","+'GO'
    s.send(send_dp.encode('UTF-8'))
    time.sleep(0.5)
    s.send(imgstring)
    time.sleep(0.3)
    if count == (lot-1):
        #AQL_pass
        AQL_hpass = AQL_Chart(Unit_hpass, Sample_Letter(lot))
        AQL_vpass = AQL_Chart(Unit_vpass, Sample_Letter(lot))
        #Deviation
        HDeviation = Sigma(Unit_horizon)
        VDeviation = Sigma(Unit_vertical)
        #Mean
        HMean = Avg(Unit_horizon)
        VMean = Avg(Unit_vertical)
        #Cp
        HCp = PCA(HDeviation, hStandard)
        VCp = PCA(VDeviation, vStandard)
        
        Hadjust = adjust(Unit_horizon, hStandard, lot)
        Vadjust = adjust(Unit_vertical, vStandard, lot)
        
        hunpassCount, hDefectrate = CountRate(Unit_hpass, lot)
        vunpassCount, vDefectrate = CountRate(Unit_vpass, lot)
        TotalDefectrate = round(TotalunpassCount/lot * 100, 1)
        time2 = time.time()
        Gap = time2-time1
        dateGap = convert_seconds_to_kor_time(Gap)
        print('TOCAQL_hpass'+str(AQL_hpass)+","+'AQL_vpass'+str(AQL_vpass)+","+'Sigmah'+str(HDeviation)+","+'Sigmav'+str(VDeviation)+","+'Meanh'+str(HMean)+","+'Meanv'+str(VMean)+","+'Cph' + str(HCp)+","+'Cpv' + str(VCp)+ "," +'hunpassCount'+str(hunpassCount)+","+'vunpassCount'+str(vunpassCount)+","+'hDefectrate' + str(hDefectrate)+","+'vDefectrate' + str(vDefectrate)+","+'Hadjust' + str(Hadjust)+","+'Vadjust' + str(Vadjust)+","+'TotalunpassCount'+str(TotalunpassCount)+","+'TotalDefectrate' + str(TotalDefectrate)+","+'Date' + str(Date)+","+'dateGap' + str(dateGap)+","+'lot' + str(lot)+","+'Model'+str(Model))
        send_Final = 'TOCAQL_hpass'+str(AQL_hpass)+","+'AQL_vpass'+str(AQL_vpass)+","+'Sigmah'+str(HDeviation)+","+'Sigmav'+str(VDeviation)+","+'Meanh'+str(HMean)+","+'Meanv'+str(VMean)+","+'Cph'+str(HCp)+","+'Cpv'+str(VCp)+"," +'hunpassCount'+str(hunpassCount)+","+'vunpassCount'+str(vunpassCount)+","+'hDefectrate'+str(hDefectrate)+","+'vDefectrate'+str(vDefectrate)+","+'Hadjust'+str(Hadjust)+","+'Vadjust'+str(Vadjust)+","+'TotalunpassCount'+str(TotalunpassCount)+","+'TotalDefectrate'+str(TotalDefectrate)+","+'Date' + str(Date)+","+'dateGap'+str(dateGap)+","+'lot'+str(lot)+","+'Model'+str(Model)
        time.sleep(3)
        s.send(send_Final.encode('UTF-8'))
    return


if __name__ == "__main__":
    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    s.connect( ( HOST, PORT ) )
    print('Hi! I am client')
    try:
        while True:
            if a == 0:
                recv_msg = s.recv(1024).decode('UTF-8')

                if recv_msg.startswith('TOR'):
                    recv_msg = recv_msg.replace('TORDatesStand,','').split(',')
                    print(recv_msg)
                    Model = str(recv_msg[0])
                    print(Model)
                    lot = int(recv_msg[1])
                    print(lot)
                    hStandard = float(recv_msg[2])
                    print(hStandard)
                    vStandard = float(recv_msg[3])
                    print(vStandard)
                    Date = int(recv_msg[4])
                    print(Date)
                    
                    a=1
                    recv_msg = ''

            elif a == 1:
                time1 = time.time()
                setServoPos1(90)
                time.sleep(1)
                setServoPos2(80)
                time.sleep(1)
                while True:
                    main_conveyor_On(con1_port)
                    main_conveyor_On(con2_port)
                    time.sleep(2)
                    while True:
                        d1 = Sonar(sig1)
                        if d1 <= 4.5:
                            main_conveyor_Off(con1_port)
                            break
                        else:
                            continue
                    
                    led_on(led1)
                    led_off(led2)
                    led_off(led3)
                    dot1, dot2, dot3, dot4 = opencapture(count)
                    a, b, c, d = dot1234(dot1, dot2, dot3, dot4)
                    temp = [dot1, dot2, dot3, dot4]
                    for i in range(4):
                        if i == a:
                            p1.append(temp[i])
                        elif i == b:
                            p2.append(temp[i])
                        elif i == c:
                            p3.append(temp[i])
                        elif i == d:
                            p4.append(temp[i])
                    calculate(count)
                    led_off(led1)
                    count+=1
                    
                    if count == lot:
                        main_conveyor_On(con1_port)
                        time.sleep(11)
                        led_off(led2)
                        led_off(led3)
                        main_conveyor_Off(con1_port)
                        main_conveyor_Off(con2_port)
                        setServoPos1(90)
                        time.sleep(1)
                        setServoPos2(80)
                        time.sleep(1)
                        Unit_horizon = []
                        Unit_vertical = []
                        Unit_hpass = []
                        Unit_vpass = []
                        p1=[]
                        p2=[]
                        p3=[]
                        p4=[]
                        count=0
                        a=0
                        TotalunpassCount = 0
                        TotalDefectrate = 0
                        print(recv_msg)
                        break
           
    except (ValueError, KeyboardInterrupt):
        print( '[ Server Message ( Exception ) : non numeric' )
        print( '[ Server Message ( Exception ) : close client connection' )
        GPIO.cleanup()
        s.close()
    finally:        
        GPIO.cleanup()
        s.close()
