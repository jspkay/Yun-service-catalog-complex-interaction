## consumer.py
#  This simple code simulate a consumer of the device data collected by the server 127.0.0.1:8080
#

import requests
import time
import json
import paho.mqtt.client as mqtt


# Device Name
SERVICE_ID = "0fa02958-f1d7-11ea-adc1-0242ac120002"
# Number of second between each message of GET Device DEVICE_ID Measurements
SECOND_BTW_MESSAGES = 50

SUBSCRIPTION = {
	'uuid': SERVICE_ID,
	'endPoints': {
	},
	'description': 'I consume temperature values from deviceMQTT'
}

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
	global device
	print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
	client.subscribe(device['endPoints']['MQTT'], qos=0)

def on_message(client, userdata, message):
	topic = message.topic.split('/')
	device = topic[1]
	jsonDict = json.loads(str(message.payload.decode("utf-8")))
	print(jsonDict)
	
if __name__ == '__main__':
	# GET Subscription Info
	print(str('%d GET Subscription Info' % time.time()))
	r = requests.get('http://127.0.0.1:8081/subscription')
	print(r.content)
	dictionary = json.loads(r.content)

	print(str('%d POST Subscription Info' % time.time()))
	r = requests.post(dictionary['subscriptions']['REST']['service'],json = SUBSCRIPTION)
	print(r.status_code)

	print(str('%d GET Devices Info' % time.time()))
	r = requests.get('http://127.0.0.1:8081/devices')
	print(r.content)
	devices = json.loads(r.content)

	for i in devices.keys():
		print(str('%d GET Device Info' % time.time()))
		r = requests.get('http://127.0.0.1:8081/devices/'+devices[i]['uuid'])
		print(r.content)
		device = json.loads(r.content)

	print(device)

	client =mqtt.Client(SERVICE_ID)
	client.on_connect = on_connect
	client.on_message = on_message
	client.connect(dictionary['subscriptions']['MQTT']['device']['hostname'])
	client.loop_start()

	counter = 0
	while(True):
		time.sleep(SECOND_BTW_MESSAGES)
		print(str('%d POST Subscription Info' % time.time()))
		r = requests.post(dictionary['subscriptions']['REST']['service'],json = SUBSCRIPTION)
		print(r.status_code)
