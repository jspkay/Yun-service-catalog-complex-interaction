## catalog.py
# Simple catalog that collect data coming from devices, services, and users
#

import cherrypy
import json
import time
import paho.mqtt.client as mqtt

# Global variable that contains a dictionary

CATALOG = {
	'devices':{},
	'services':{},
	'users':{}
}

HOSTNAME = "192.168.163.99"
SUBSCRIPTION = {
	'subscriptions':{
		'REST':{
			'device': 'http://{}:8081/devices/subscription'.format(HOSTNAME),
			'service': 'http://{}:8081/services/subscription'.format(HOSTNAME),
			'user': 'http://{}:8081/users/subscription'.format(HOSTNAME)
		},
		'MQTT': {
			'device':{
				'hostname': HOSTNAME,
				'port':  '1883',
				'topic': 'tiot/prova/catalog/devices/subscription'
			}	
		}
	}
}
# Web Service to manage Subscription information
class InfoWebService(object):
	exposed = True

	# GET Subscription Info (http://127.0.0.1/)
	def GET (self, *uri, **params):
		global CATALOG
		if len(uri) == 0:
			return json.dumps(SUBSCRIPTION)
		else:
			raise cherrypy.HTTPError(404, "Bad Request: URI is not correctly formatted")

# Web Service to manage Devices
class DeviceWebService(object):
	exposed = True

	# GET Devices or Device (http://127.0.0.1/devices/{DEVICE_ID})
	def GET (self, *uri, **params):
		global CATALOG
		if len(uri) == 0:
			return json.dumps(CATALOG['devices'])
		elif len(uri) == 1:
			if uri[0] in CATALOG['devices'].keys():
				return json.dumps(CATALOG['devices'][uri[0]])
			else:
				raise cherrypy.HTTPError(404, "Bad Request: URI does not contain a device name")
		else:
			raise cherrypy.HTTPError(404, "Bad Request: URI is not correctly formatted")

	# POST Device (http://127.0.0.1/devices/subscription)
	def POST (self, *uri, **params):
		global CATALOG
		if len(uri) == 1 and uri[0] == 'subscription':
			contentLength = cherrypy.request.headers['Content-Length']
			if contentLength:
				rawBody = cherrypy.request.body.read(int(contentLength))
				dictionary = json.loads(rawBody)
				if 'uuid' in dictionary.keys():
					if dictionary['uuid'] in CATALOG['devices'].keys():
						CATALOG['devices'][dictionary['uuid']]['timestamp'] = time.time()
						print(CATALOG)
					else:
						if 'endPoints' in dictionary.keys():
							if 'availableResources' in dictionary.keys():
								dictionary['timestamp'] = time.time()
								CATALOG['devices'][dictionary['uuid']] = dictionary
								print(CATALOG)
							else:
								raise cherrypy.HTTPError(400, "Bad Request: payload does not contain a proper body")
						else:
							raise cherrypy.HTTPError(400, "Bad Request: payload does not contain a proper body")
				else:
					raise cherrypy.HTTPError(400, "Bad Request: payload does not contain a proper body")
			else:
				raise cherrypy.HTTPError(400, "Bad Request: payload does not contain a body")
		else:
			raise cherrypy.HTTPError(404, "Bad Request: URI is not correctly formatted")

# Web Service to manage Services
class ServiceWebService(object):
	exposed = True

	# GET Services or Service (http://127.0.0.1/services/{SERVICE_ID})
	def GET (self, *uri, **params):
		global CATALOG
		if len(uri) == 0:
			return json.dumps(CATALOG['services'])
		elif len(uri) == 1:
			if uri[0] in CATALOG['services'].keys():
				return json.dumps(CATALOG['services'][uri[0]])
			else:
				raise cherrypy.HTTPError(404, "Bad Request: URI does not contain a services name")
		else:
			raise cherrypy.HTTPError(404, "Bad Request: URI is not correctly formatted")

	# POST Service (http://127.0.0.1/service/subscription)
	def POST (self, *uri, **params):
		global CATALOG
		if len(uri) == 1 and uri[0] == 'subscription':
			contentLength = cherrypy.request.headers['Content-Length']
			if contentLength:
				rawBody = cherrypy.request.body.read(int(contentLength))
				dictionary = json.loads(rawBody)
				if 'uuid' in dictionary.keys():
					if dictionary['uuid'] in CATALOG['services'].keys():
						CATALOG['services'][dictionary['uuid']]['timestamp'] = time.time()
						print(CATALOG)
					else:
						if 'endPoints' in dictionary.keys():
							if 'description' in dictionary.keys():
								dictionary['timestamp'] = time.time()
								CATALOG['services'][dictionary['uuid']]=dictionary
								print(CATALOG)
							else:
								raise cherrypy.HTTPError(400, "Bad Request: payload does not contain a proper body")
						else:
							raise cherrypy.HTTPError(400, "Bad Request: payload does not contain a proper body")
				else:
					raise cherrypy.HTTPError(400, "Bad Request: payload does not contain a proper body")
			else:
				raise cherrypy.HTTPError(400, "Bad Request: payload does not contain a body")
		else:
			raise cherrypy.HTTPError(404, "Bad Request: URI is not correctly formatted")

# Web Service to manage User
class UserWebService(object):
	exposed = True

	# GET Users or User (http://127.0.0.1/users/{USER_ID})
	def GET (self, *uri, **params):
		global CATALOG
		if len(uri) == 0:
			return json.dumps(CATALOG['users'])
		elif len(uri) == 1:
			if uri[0] in CATALOG['users'].keys():
				return json.dumps(CATALOG['users'][uri[0]])
			else:
				raise cherrypy.HTTPError(404, "Bad Request: URI does not contain a services name")
		else:
			raise cherrypy.HTTPError(404, "Bad Request: URI is not correctly formatted")

	# POST User (http://127.0.0.1/service/subscription)
	def POST (self, *uri, **params):
		global CATALOG
		if len(uri) == 1 and uri[0] == 'subscription':
			contentLength = cherrypy.request.headers['Content-Length']
			if contentLength:
				rawBody = cherrypy.request.body.read(int(contentLength))
				dictionary = json.loads(rawBody)
				if 'uuid' in dictionary.keys():
					if dictionary['uuid'] in CATALOG['users'].keys():
						CATALOG['users'][dictionary['uuid']]['timestamp'] = time.time()
						print(CATALOG)
					else:
						if 'name' in dictionary.keys():
							if 'surname' in dictionary.keys():
								if 'email' in dictionary.keys():
									dictionary['timestamp'] = time.time()
									CATALOG['users'][dictionary['uuid']]=dictionary
									print(CATALOG)
								else:
									raise cherrypy.HTTPError(400, "Bad Request: payload does not contain a proper body")
							else:
								raise cherrypy.HTTPError(400, "Bad Request: payload does not contain a proper body")
						else:
							raise cherrypy.HTTPError(400, "Bad Request: payload does not contain a proper body")
				else:
					raise cherrypy.HTTPError(400, "Bad Request: payload does not contain a proper body")
			else:
				raise cherrypy.HTTPError(400, "Bad Request: payload does not contain a body")
		else:
			raise cherrypy.HTTPError(404, "Bad Request: URI is not correctly formatted")

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
	print("Connected to broker with result code {0}".format(str(rc)))  # Print result of connection attempt
	client.subscribe('tiot/prova/catalog/devices/subscription', qos=0)

def on_message(client, userdata, message):
	topic = message.topic.split('/')
	device = topic[1]
	dictionary = json.loads(str(message.payload.decode("utf-8")))
	if 'uuid' in dictionary.keys():
		if dictionary['uuid'] in CATALOG['devices'].keys():
			CATALOG['devices'][dictionary['uuid']]['timestamp'] = time.time()
			client.publish('tiot/prova/catalog/devices/subscription/'+dictionary['uuid'],json.dumps(CATALOG['devices'][dictionary['uuid']]))
			print(CATALOG)
		else:
			if 'endPoints' in dictionary.keys():
				if 'availableResources' in dictionary.keys():
					dictionary['timestamp'] = time.time()
					CATALOG['devices'][dictionary['uuid']] = dictionary
					client.publish('tiot/prova/catalog/devices/subscription/'+dictionary['uuid'],json.dumps(CATALOG['devices'][dictionary['uuid']]))
					print(CATALOG)


if __name__ == '__main__': 
	client = mqtt.Client('ResourceCatalog')
	client.on_connect = on_connect
	client.on_message = on_message
	client.connect('127.0.0.1')
	client.loop_start()
	conf = { 
		'/': { 
			'request.dispatch': cherrypy.dispatch.MethodDispatcher(), 
		} 
	}
	cherrypy.tree.mount(DeviceWebService(), '/devices', conf)
	cherrypy.tree.mount(ServiceWebService(), '/services', conf)
	cherrypy.tree.mount(UserWebService(), '/users', conf)
	cherrypy.tree.mount(InfoWebService(), '/subscription', conf)

	cherrypy.config.update({'server.socket_host': '0.0.0.0'})
	cherrypy.config.update({'server.socket_port': 8081})

	cherrypy.engine.start() 
	

	while(True):
		time.sleep(60)
		timeReference = time.time()

		deletedDevices = []
		for i in CATALOG['devices'].keys():
			if timeReference - CATALOG['devices'][i]['timestamp'] > 60:
				deletedDevices.append(i)
		for i in deletedDevices:
			del CATALOG['devices'][i]
			print('DELETED ' + i)

		deletedServices = []
		for i in CATALOG['services'].keys():
			if timeReference - CATALOG['services'][i]['timestamp'] > 60:
				deletedServices.append(i)
		for i in deletedServices:
			del CATALOG['services'][i]
			print('DELETED ' + i)

		deletedUsers = []
		for i in CATALOG['users'].keys():
			if timeReference - CATALOG['users'][i]['timestamp'] > 60:
				deletedUsers.append(i)
		for i in deletedUsers:
			del CATALOG['users'][i]
			print('DELETED ' + i)
