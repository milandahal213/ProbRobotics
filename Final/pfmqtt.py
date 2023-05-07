#to start things up on a mac in terminal:  
#opt/homebrew/opt/mosquitto/sbin/mosquitto -c /opt/homebrew/etc/mosquitto/mosquitto.conf to start
#
# You can make changes to the configuration by editing:
#    /opt/homebrew/etc/mosquitto/mosquitto.conf
#
import paho.mqtt.client as mqtt #import the client1
import time
import json

val=''
def whenCalled(client, userdata, message):
    global val
    val+=str(message.payload.decode("utf-8"))


def checkvals():
    global val
    print(val)
    value=json.loads(val)
    val=''
    return value

broker = '10.245.144.196'
topic_sub = "milan/tell"
topic_pub = "milan/listen"

client = mqtt.Client("fred") # use a unique name
client.on_message = whenCalled # callback
client.connect(broker)
print('Connected to %s MQTT broker' % broker)

client.loop_start() #start the loop
client.subscribe(topic_sub)

i = 0
while True:
    getch= input()
    print("moving the robot")
    client.publish(topic_pub,'1')
    #getch= input()

    while(val.find('end')<0):
        time.sleep(0.1)
        print(val)
        pass
    print(val)
    datafromrobot=checkvals()
    print(datafromrobot)
    print("E",datafromrobot["E"])
    print("W",datafromrobot["W"])
    print("N",datafromrobot["N"])
    print("S",datafromrobot["S"])


client.loop_stop() #stop the loop