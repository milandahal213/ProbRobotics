import time
import machine
import ubinascii
 
from secrets import Tufts_Wireless as wifi
#from secrets import virus as wifi
import mqtt_CBR


topic_sub = 'Two/listen'
topic_pub = 'Two/tell'
client_id= ubinascii.hexlify(machine.unique_id())
                                          
mqtt_CBR.connect_wifi(wifi)
led = machine.Pin(2, machine.Pin.OUT)  # 6 for 2040

class MQ():
    def __init__(self, broker, name):
        client_id= ubinascii.hexlify(machine.unique_id())
        self.c=mqtt_CBR.mqtt_client(client_id, broker, self.whenCalled)
        
        self.topic_sub= name +'/listen'
        self.topic_pub = name +'/tell'
        self.c.subscribe(self.topic_sub)

    def whenCalled(self, topic, msg):
        print("start",(topic.decode(), msg.decode()),"end")
        

    def send(self,msg):
        self.c.publish(self.topic_pub, msg)
        
    def on(self):
        led.value(0)
        
    def off(self):
        led.value(1)
   

    def check(self):
        self.c.check()
        

