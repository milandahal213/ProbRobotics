#to start things up on a mac in terminal:  
#opt/homebrew/opt/mosquitto/sbin/mosquitto -c /opt/homebrew/etc/mosquitto/mosquitto.conf to start
#
# You can make changes to the configuration by editing:
#    /opt/homebrew/etc/mosquitto/mosquitto.conf
#
'''
broker = '10.245.144.196'
topic_sub = "milan/tell"
topic_pub = "milan/listen"
'''
import paho.mqtt.client as mqtt #import the client1
import time
import json



class MQ:
    def __init__(self,broker,name):
        self.broker=broker
        self.topic_sub=name+'/tell'
        self.topic_pub=name+'/listen'
        self.val=''
        self.client=mqtt.Client("uniquename") # use a unique name
        self.client.on_message = self.whenCalled # callback
        self.client.connect(self.broker)
        print('Connected to %s MQTT broker' % self.broker)
        self.start()

    def whenCalled(self, client, userdata, message):
        print("whencalled called")
        self.val+=str(message.payload.decode("utf-8"))


    def robot_distances(self):
        while(self.val.find('end')<0): #keep waiting for complete set of messages (with end)
            time.sleep(0.1)
        value=json.loads(self.val)
        self.val=''
        return value


    def start(self):        
        self.client.loop_start() #start the loop
        self.client.subscribe(self.topic_sub)


    def stop(self):
        self.client.loop_stop() #stop the loop


    def send(self, msg):
        print("called")
        print(self.topic_pub)
        print(msg)
        self.client.publish(self.topic_pub,msg)