from spike import PrimeHub, LightMatrix, Button, StatusLight, ForceSensor, MotionSensor, Speaker, ColorSensor, App, DistanceSensor, Motor, MotorPair
from spike.control import wait_for_seconds, wait_until, Timer
from math import *
import math
import random

hut = PrimeHub()
from spike import MotorPair
motor_pair = MotorPair('B', 'A')
DistMotor=Motor('D')
DistMotor.set_stall_detection(True)
Dist= DistanceSensor('F')
hut.light_matrix.show_image('SAD')
motor_pair.start(speed=0)

hut.light_matrix.show_image('HAPPY')
import hub
import time
C=hub.port.C
C.mode(hub.port.MODE_FULL_DUPLEX)
time.sleep(0.2)
C.baud(115200)
speed=0
#change these two items before starting
ip='10.245.144.196'
#ip='10.0.0.141'
def waittill(keyword):
    ret=''
    ret=C.read(1)
    while not ret.find(keyword)>0:
        ret+=C.read(1)
    return ret

def setupMQTT():
    print("resetting")
    C.write('\x03')
    C.write('\r\n')
    waittill(b'>>>')
    C.write('import main\r\n')
    waittill(b'>>>')
    C.write('a=main.MQ("'+ip+'","milan")\r\n')
    time.sleep(0.5)
    C.write('\r\n')
    waittill(b'>>>')
    return True

def check():
    C.write('a.check()\r\n')
    ret=waittill(b'>>>')
    if ret.find(b'start')>0:
        print(ret)
    val=ret
    #print("waiting")
    return(val)

def sendmsg(msg):
    C.write('a.send(\''+msg+'\')\r\n')
    waittill(b'>>>')
    print("sent")

def getData():
    stepAngle=90
    Pos=[0,0,0,0]
    for i in range(4):
        time.sleep(0.5)
        Pos[i]=Dist.get_distance_cm()
        if(Pos[i] is None):
            Pos[i]=200
        DistMotor.run_for_degrees(stepAngle)
        if DistMotor.was_stalled():
            DistMotor.run_for_rotations(-1)
    DistMotor.run_for_degrees(stepAngle *(-4))
    if DistMotor.was_stalled():
        DistMotor.run_for_degrees(stepAngle *(4))


    return(Pos)


def setmotorsready(angle):
    #angle=180-hut.motion_sensor.get_yaw_angle()
    print("turning to this angle",angle)
    DistMotor.run_to_position(angle)

def run(val):

    index= val.find(b'\') end')
    val=val[index-1:index]
      
    if(val==b'0'):
        print("okay")
        pass

    if(val==b'1'):
        hut.speaker.beep(60, 0.3)
        print("inside")


  
        print("data sent")
        #make it return the tilt 

    elif(val==b'2'):
        hut.speaker.beep(60, 1)
        print("secondcase")   
        speed=random.randint(0,10)
        motor_pair.move_tank(speed, 'cm', left_speed=50, right_speed=50)
   

        distances=[]
        for i in range(24):
            DistMotor.run_to_position(i*15)
            dis=Dist.get_distance_cm()
            if(dis is None):
                dis=200
            distances.append(dis)
        temp=1000
        small=0
        for i in range(24):
            dis=distances[i]
            if(dis<temp):
                small=i
                temp=dis
        print(distances)
        data=[]

        for i in range(4):
            ss=(small+6*i)%24
            print(ss)
            data.append(distances[ss])
        DistMotor.run_for_rotations(-1)

        Y=hut.motion_sensor.get_yaw_angle()+180
        A=small*15
        direction=(Y+A)%360
        
        #data=getData()

        if(direction>45 and direction <=135):
            print("West")
            sendmsg('{"W":' +str(data[0]))
            sendmsg(',"N":' +str(data[1]))
            sendmsg(',"E":' +str(data[2]))
            sendmsg(',"S":' +str(data[3]))

        elif(direction>135 and direction <=225):
            print("North")
            sendmsg('{"N":' +str(data[0]))
            sendmsg(',"E":' +str(data[1]))
            sendmsg(',"S":' +str(data[2]))
            sendmsg(',"W":' +str(data[3]))
        elif(direction>225 and direction <=315):
            print("East")
            sendmsg('{"E":' +str(data[0]))
            sendmsg(',"S":' +str(data[1]))
            sendmsg(',"W":' +str(data[2]))
            sendmsg(',"N":' +str(data[3]))
        elif(direction>315 or direction <=45):
            print("South")
            sendmsg('{"S":' +str(data[0]))
            sendmsg(',"W":' +str(data[1]))
            sendmsg(',"N":' +str(data[2]))
            sendmsg(',"E":' +str(data[3]))

        sendmsg(',"v":' + str(speed))
        #sendmsg(',"d":' + str(dirVal* 8.1 * math.pi / 2))
        sendmsg(',"st":"end"}')
        print("data sent")
        #make it return the tilt
   
    elif(val==b'3'):
        C.write('a.on()\r\n')
        waittill(b'>>>')
        print("on")
    
    elif(val==b'4'):
        C.write('a.off()\r\n')
        
        waittill(b'>>>')
        print("off")




print("starting")
if(setupMQTT()):
    print("setup done")
    hut.speaker.beep(50, 0.3)
setmotorsready(0)


while True:
    val=check()
    run(val)
    time.sleep(0.3)
    #alignAngle=180-yaw
    #DistMotor.run_to_position(alignAngle)
    #setmotorsready(alignAngle)
    


print("done")
