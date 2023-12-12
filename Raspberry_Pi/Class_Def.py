import re
import math
import time
import random
import numpy
import datetime

def nums(x, y): #각각추출된 4개의 리스트 값들을 2개씩 더한다. 그리고 count 개념을 이용해 2개가 나오는 값을 추출하면 좌표의 위치를 알수 있다.(ex) xmin, ymin 경우 1123이나오면 1이 2개이므로 dot1 은 좌표상 왼쪽하단부분위치. 
    num={} 
    for i in (x+y):
        try:
            num[i] += 1
        except:
            num[i]=1
    renum = {v:k for k,v in num.items()}
    return renum.get(2)
    
def dot1234(dot1, dot2, dot3, dot4):#opencv 통해 좌표값 4개를 불러옴
    xlist =[]
    ylist =[]
    
    xdict = dict(dot11 = dot1[0], dot21 = dot2[0], dot31 = dot3[0], dot41 = dot4[0])  
    ydict = dict(dot12 = dot1[1], dot22 = dot2[1], dot32 = dot3[1], dot42 = dot4[1])  #딕셔너리로 x,y 각각 생성
  
    xdict = sorted(xdict.items(), key=lambda x: x[1])
    ydict = sorted(ydict.items(), key=lambda x: x[1])  #value 값을 오름차순으로 정렬
    
    xmin = (xdict[0][0])[3], (xdict[1][0])[3]   #오름차순으로 정렬된 값을 불러오는데 xmin경우 정렬된 x값 1,2번째 값 추출
    xmax = (xdict[2][0])[3], (xdict[3][0])[3]   #xmax경우 오름차순으로 정렬된 x값의 3,4 번째 값추출
    ymin = (ydict[0][0])[3], (ydict[1][0])[3]   #ymin y값의 1,2번째 추출
    ymax = (ydict[2][0])[3], (ydict[3][0])[3]   #ymax y값의 3,4번째 추출
    abcd = int(nums(xmin, ymin))-1, int(nums(xmin, ymax))-1, int(nums(xmax, ymax))-1, int(nums(xmax, ymin))-1
    return abcd

def Dot_Distance(x1, y1, x2, y2, x3, y3, x4, y4):
    distance12 = math.sqrt(math.pow(abs(x1 - x2), 2) + math.pow(abs(y1 - y2), 2))
    distance23 = math.sqrt(math.pow(abs(x2 - x3), 2) + math.pow(abs(y2 - y3), 2))
    distance34 = math.sqrt(math.pow(abs(x3 - x4), 2) + math.pow(abs(y3 - y4), 2))
    distance14 = math.sqrt(math.pow(abs(x1 - x4), 2) + math.pow(abs(y1 - y4), 2)) #4개의 꼭지점을 이용, 4개 길이 측정
    dislist = [distance12, distance23, distance34, distance14]  #길이를 리스트화
    dislist.sort()  #오름차순
    Result_horizon = numpy.mean((dislist[2], dislist[3]))  #리스트 3,4번째는 길이가 긴 horizon 길이다. 마지막으로 2개의 평균을 내어 리턴
    Result_horizon = round(Result_horizon*0.01686, 2)
    Result_vertical = numpy.mean((dislist[0], dislist[1]))    #vertical 마찬가지
    Result_vertical = round(Result_vertical*0.0171869, 2)
    return (Result_horizon, Result_vertical);

def Unit_Defect(standard, distance):    #서버로 부터 받아온 standard 통해 불량품 선별 (1->양품 0->가품)
    if (distance >= (standard * 0.90)) and (distance <= (standard * 1.10)):  
        result = 1
    else:
        result = 0
    return result

def Sample_Letter(lot):     #서버로 부터 받아온 lot 통해 sample 문자 추출 -> AQL 값 구하는데 이용
    if lot >= 1 and lot <= 8:
        letter = 'A'
    elif lot >= 9 and lot <= 15:
        letter = 'B'
    elif lot >= 16 and lot <= 25:
        letter = 'C'
    elif lot >= 26 and lot <= 50:
        letter = 'D'
    elif lot >= 51 and lot <= 90:
        letter = 'E'
    elif lot >= 91 and lot <= 150:
        letter = 'F'
    elif lot >= 151 and lot <= 280:
        letter = 'G'
    elif lot >= 281 and lot <= 500:
        letter = 'H'
    elif lot >= 501 and lot <= 1200:
        letter = 'J'
    elif lot >= 1201 and lot <= 3200:
        letter = 'K'
    elif lot >= 3201 and lot <= 10000:
        letter = 'L'
    elif lot >= 10001 and lot <= 35000:
        letter = 'M'
    elif lot >= 35001 and lot <= 150000:
        letter = 'N'
    elif lot >= 150001 and lot <= 500000:
        letter = 'P'
    elif lot >= 500001:
        letter = 'Q'
    return letter

def AQL_Chart(Unit_pass, letter):   #AQL값(공정상 합격품질수준)
    Re = 0
    sample = [] 
    sample_defect = 0
    if letter == 'A' or letter == 'B':
        sample = random.sample(Unit_pass, 3)
        Re = 1
    elif letter == 'C' or letter == 'D' or letter == 'E':
        sample = random.sample(Unit_pass, 13)
        Re = 2
    elif letter == 'F':
        sample = random.sample(Unit_pass, 20)
        Re = 3
    elif letter == 'G':
        sample = random.sample(Unit_pass, 32)
        Re = 4
    elif letter == 'H':
        sample = random.sample(Unit_pass, 50)
        Re = 6
    elif letter == 'J':
        sample = random.sample(Unit_pass, 80)
        Re = 8
    elif letter == 'K':
        sample = random.sample(Unit_pass, 125)
        Re = 11
    elif letter == 'L':
        sample = random.sample(Unit_pass, 200)
        Re = 15
    elif letter == 'M' or letter == 'N' or letter == 'P' or letter == 'Q' or letter == 'R':
        sample = random.sample(Unit_pass, 315)
        Re = 22
    for i in sample:
        if i == 0:
            sample_defect += 1
        elif i == 1:
            continue
    if sample_defect >= Re:
        AQL_pass = 0
    elif sample_defect < Re:
        AQL_pass = 1
    return AQL_pass

def Avg(Unit_horizon):  #평균
    avg = numpy.mean(Unit_horizon)
    return round(avg, 2)

def Sigma(Unit_horizon): #표준편차 -> Cp 값 구하는데 이용 
    sigma = numpy.std(Unit_horizon)
    return round(sigma, 3)

def PCA(sigma, Standard): #Cp(공정능력지수)
    USL = Standard * 1.10
    LSL = Standard * 0.90
    if sigma == 0:
        Cp = -1
    else:
        Cp = (USL - LSL) / (6 * sigma)
    return round(Cp, 2)

def CountRate(Unit_pass, lot):
    passCount = Unit_pass.count(0)
    Defectrate = round(passCount/lot * 100, 1)
    return passCount, Defectrate

def adjust(Unit_horizon, Standard, lot):
    hap = -((sum(Unit_horizon) - (Standard*lot))/lot)
    haps = round(hap, 3)
    
    return ('%+.3f' % haps)

def convert_seconds_to_kor_time(in_seconds):
    """초를 입력받아 읽기쉬운 한국 시간으로 변환"""
    t1   = datetime.timedelta(seconds=in_seconds)
    days = t1.days
    _sec = t1.seconds
    (hours, minutes, seconds) = str(datetime.timedelta(seconds=_sec)).split(':')
    hours   = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    
    result = []
    if days >= 1:
        result.append(str(days)+'일')
    if hours >= 1:
        result.append(str(hours)+'시간')
    if minutes >= 1:
        result.append(str(minutes)+'분')
    if seconds >= 1:
        result.append(str(seconds)+'초')
    return ' '.join(result)
