import paho.mqtt.client as mqtt
import requests
import random
import time
import json
import serial

# Serial interface
ser = object()
INIT_BYTE = b'\xff'
EXIT_BYTE = b'\xfe'
ESCP_BYTE = 0xfd


# Client Name
DEVICE_ID = '5cfd92ab-29cb-4d2a-b777-c2fe574cd470'
# Broker IP
HOST_NAME = '192.168.163.99:8081'
# Number of second between each message of POST Measurements
SECOND_BTW_MESSAGES = 2

# Variable to calculate the actual temperature of the room
MEAN_TEMPERATURE = 21.0
DEVIATION = 5.0

SUBSCRIPTION = {
	'uuid': DEVICE_ID,
	'endPoints': {
			'MQTT': 'devices/'+DEVICE_ID
	},
	'availableResources':[
		'temperature'
	]
}


# Dictionary for Measurement JSON
MESSAGE = {
	"bn": "mqtt 127.0.0.1:1883 " + DEVICE_ID, 
	"e": []
}
MEASURE = { 
	"n": "temperature", 
	"u": "Celsius", 
	"t": 0, 
	"v": 0.0 
}

def sendSerial(msg):
	print("Sending serial...", end=" ")
	l = len(msg)
	print("length is " +str(l), end=" ")
	msg = msg
	print("message: ", end="'")
	print(msg, end=" ");
	ser.write(INIT_BYTE)
	ser.write(l.to_bytes(2, 'little'))
	for c in msg:
		if c == EXIT_BYTE:
			ser.write(ESCP_BYTE)
		#print(c.encode())
		ser.write(c.encode())
	ser.write(EXIT_BYTE)
	print("' Done")
		

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
	global dictionary
	print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
	client.subscribe(dictionary['subscriptions']['MQTT']['device']['topic']+'/'+DEVICE_ID, qos=0)
	client.subscribe(dictionary['subscriptions']['MQTT']['device']['topic']+'/'+DEVICE_ID+'/command', qos=0)

def on_message(client, userdata, message):
	print("MQTT - SUBSCRIBE: Message received - ", end=" ")
	topic = message.topic.split('/')
	msg = message.payload.decode("utf-8")
	if topic[-1] == DEVICE_ID:
		print("Subscription renewal")
		device = topic[1]
		jsonDict = json.loads(str(msg))
		#print(jsonDict)
	elif topic[-1] == "command":
		print("command: ", end =" ")
		print(msg)
		msg_parsed = json.loads(msg)
		peripheral = msg_parsed["e"][0]["n"]
		value = msg_parsed["e"][0]["v"]
		if peripheral == "led":
			if not value in ['0', '1', 0, 1]:
				print("Error parsing the command! Value is not 1 or 0")
			else:	
				sendSerial("L:"+str(value)) #value contains either '1' or '0'
	else:
		print("Unknown message")
		print(message.topic)
		print(message.payload)



def serialRead():
	print("Serial reading...", end=" ")
	if(ser.in_waiting >= 1):
		c = ser.read(1)
		#print(c)
		if c != INIT_BYTE:
			return None
	if(ser.in_waiting >= 2):
		ll = ser.read(2)
		#print(ll)
		l = int.from_bytes(ll, 'big')
		#print(l)
		msg_byte = ser.read(l)
		#print(msg_byte)
	else:
		msg_byte = None
	if(ser.in_waiting >= 1):
		e = ser.read(1)
		if e != EXIT_BYTE:
			return None
	msg = ""
	if msg_byte != None:
		for c in msg_byte:
			if c != ESCP_BYTE:
				msg += chr(c)
	print("Done", end=" ")
	return msg
	
def getTemperature():
	msg = serialRead()
	if msg == None:
		print("received None!")
		return [-1, None]
	print("received: " + msg)
	[what, value, unit] = msg.split(":")
	if what != 'T':
		return None
	return [value, unit]


if __name__ == '__main__':
	# GET Subscription Info
	print(str('%d GET Subscription Info' % time.time()))
	r = requests.get('http://{}/subscription'.format(HOST_NAME))
	print(r.content)
	dictionary = json.loads(r.content)

	client =mqtt.Client(DEVICE_ID)
	client.on_connect = on_connect
	client.on_message = on_message
	print("Connecting to: "+dictionary['subscriptions']['MQTT']['device']['hostname'])
	client.connect(dictionary['subscriptions']['MQTT']['device']['hostname'])
	client.loop_start()

	client.publish(dictionary['subscriptions']['MQTT']['device']['topic'],json.dumps(SUBSCRIPTION))
	counter = 0
	ser = serial.Serial("/dev/console", 9600) #Serial initialization
	while(True):
		time.sleep(SECOND_BTW_MESSAGES)
		[temperature, unit] = getTemperature()
		MEASURE["t"] = time.time()
		MEASURE["u"] = unit
		MEASURE["v"] = float(temperature)
		MESSAGE["e"] = [MEASURE]
		print(str('MQTT - PUBLISH: Temperature %s (timestamp: %d)' % (temperature, MEASURE["t"])))
		client.publish("devices/"+DEVICE_ID,json.dumps(MESSAGE))
		counter = counter + 1
		if counter%5 == 0:
			client.publish(dictionary['subscriptions']['MQTT']['device']['topic'],json.dumps(SUBSCRIPTION))



