#to start things up on a mac in terminal:  
#opt/homebrew/opt/mosquitto/sbin/mosquitto -c /opt/homebrew/etc/mosquitto/mosquitto.conf to start
#
# You can make changes to the configuration by editing:
#    /opt/homebrew/etc/mosquitto/mosquitto.conf
#
import paho.mqtt.client as mqtt #import the client1
import time

def whenCalled(client, userdata, message):
    print("received " ,str(message.payload.decode("utf-8")))
    print("from topic ",message.topic)

broker = '192.168.86.31'
topic_sub = "ESP/tell"
topic_pub = "ESP/listen"

client = mqtt.Client("fred") # use a unique name
client.on_message = whenCalled # callback
client.connect(broker)
print('Connected to %s MQTT broker' % broker)

client.loop_start() #start the loop
client.subscribe(topic_sub)

i = 0
while True:
    print("Publishing message to topic",topic_pub)
    client.publish(topic_pub,"iteration %d" % i)
    time.sleep(10) # wait for a little
		i+=1
client.loop_stop() #stop the loop