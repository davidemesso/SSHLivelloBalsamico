import math
import paho.mqtt.client as client
import json
import mysql.connector as connector
import time
import websocket
import threading
import time

class MySQLHandler():
	DEFAULT_CONNECTOR_CONFIG = {
		'user': 'access',
		'password': 'RootRoot123!',
		'host': 'localhost',
		'database': 'sshDatabase'
	}

	def connect(self, config = DEFAULT_CONNECTOR_CONFIG):
		try:
			self.connector = connector.connect(**config)
			self.cursor = self.connector.cursor()
		except:
			print("database connection error")

	def executeSingleQuery(self, query):
		try:
			self.cursor.execute(query)
			self.connector.commit()
			print("updated database")
		except:
			print("Error updating database")

	def executeSingleSelectQuery(self, query):
		try:
			self.cursor.execute(query)
			return self.cursor.fetchall()
		except:
			print("Error getting data")

	def closeConnection(self):
		self.cursor.close()
		self.connector.close()        


class wsMessageReceiverThread(threading.Thread):
	def __init__(self, mySQLHandler, wsHandler):
		threading.Thread.__init__(self)
		self.mySQLHandler = mySQLHandler
		self.wsHandler = wsHandler

		self.sendServerHandshake()

	def sendServerHandshake(self):
		message = { "type": "ServerHandshake" }
		try:
			self.wsHandler.send(json.dumps(message))
		except:
			print("Tornado is not connected")

	def run(self):
		self.receiveDataWS()

	def receiveDataWS(self):
		while True:
			try:
				data = json.loads(self.wsHandler.recv())
			except:
				print('Connection closed')
				break
			
			print(data)
			if data['type'] == "StoricDataRequest":
				self.sendStoricData(data['payload'])
			elif data['type'] == "SensorsDataRequest":
				self.sendSensorsData(data['payload'])
	
	def sendStoricData(self, data):
		query = f"""SELECT ambientData.id, name, timestamp, pressure, temperature, humidity 
					FROM ambientData JOIN barrels
					ON (ambientData.id = barrels.id)
					WHERE date(timestamp) >= "{data['startTime']}" and
							date(timestamp) <= "{data['endTime']}" 
                                        LIMIT 600;"""
		storicData = self.mySQLHandler.executeSingleSelectQuery(query)
		formattedData = []
		for el in storicData:
			formattedData.append({
				"id"   : str(el[0]),
				"name" : str(el[1]),
				"time" : str(el[2]),
				"pres" : str(el[3]),
				"temp" : str(el[4]),
				"hum"  : str(el[5])
			})
		packet = {
			"type" : "StoricDataServe",
			"payload" : {
				"data" : formattedData,
				"id" : data['id']
			}
		}
		self.wsHandler.send(json.dumps(packet))

	def sendSensorsData(self, data):
		query = """ SELECT barrels.id, name, volume, radius, length, lat, lng
					FROM barrels JOIN balsamicLevel
					ON barrels.id = balsamicLevel.id AND
					timestamp = (SELECT timestamp FROM balsamicLevel WHERE id=barrels.id ORDER BY timestamp desc LIMIT 1)
					GROUP BY id;"""
		sensorsData = self.mySQLHandler.executeSingleSelectQuery(query)
		formattedData = []
		for el in sensorsData:
			formattedData.append({
				"id"   : str(el[0]),
				"name" : str(el[1]),
				"volume" : str(el[2]),
				"radius" : str(el[3]),
				"length" : str(el[4]),
				"lat" : str(el[5]),
				"long" : str(el[6])
			})
		packet = {
			"type" : "SensorsDataServe",
			"payload" : {
				"data" : formattedData,
				"id" : data['id']
			}
		}
		self.wsHandler.send(json.dumps(packet))


class MQTTSubscriber:
	HOSTNAME = "192.168.89.103"
	TOPIC = "fermi/ssh/vinegar/#"

	def __init__(self, name):
		self.client = client.Client(name)

		#MQTT related init
		self.client.on_message = self.onMessage

		#Database connection related inits
		self.mySQLHandler = MySQLHandler()
		self.mySQLHandler.connect()
		
		#WS sender related init
		self.wsHandler = self.openWsConnectionToTornado()

		#WS receiver related inits
		self.wsReceiver = wsMessageReceiverThread(self.mySQLHandler, self.wsHandler)
		self.wsReceiver.start()
		
	def start(self):
		self.client.connect(self.HOSTNAME)
		self.client.subscribe(self.TOPIC)
		self.client.loop_forever()

	def onMessage(self, client, userdata, message):
		data = json.loads(message.payload.decode("utf-8"))
		print(data)

		topic = message.topic
		datetime = self.getDatetimeFromEpoch(data['time'])
		print(topic)

		if topic == "fermi/ssh/vinegar/ambientData/":
			query = f"""INSERT INTO ambientData (id, timestamp, temperature, pressure, humidity) 
						VALUES ({data['id']}, "{datetime}", 
								{data['temp']}, {data['pres']}, 
								{data['hum']});"""
			self.sendDataToTornado(json.dumps(data))
			self.mySQLHandler.executeSingleQuery(query)
		elif topic == "fermi/ssh/vinegar/balsamicLevel/":
			volume = self.getVolumeInLiters(data['radius'], data['length'], data['level'])
			print(volume)
			query = f"""INSERT INTO balsamicLevel (id, timestamp, level, volume) 
					VALUES ({data['id']}, "{datetime}",
							{data['level']}, {volume});"""

			#self.mySQLHandler.executeSingleQuery(query)


	def getDatetimeFromEpoch(self, epoch):
		localtime = time.localtime(epoch)
		return time.strftime('%Y-%m-%d %H:%M:%S', localtime)

	def getVolume(self, radius, length, depth):
		r = radius
		l = length
		d = int(depth)

		# Volume of partially filled cylinder https://www.mathopenref.com/cylindervolpartial.html
		segArea = math.pow(r, 2) * math.acos((r-d)/ r) - (r-d)*math.sqrt(2*r*d - d*d);
		volume = segArea * l
		
		return volume

	def getVolumeInLiters(self, radius, length, depth):
			return self.getVolume(radius, length, depth) * 0.001

	def openWsConnectionToTornado(self):
		ws = None
		try:
			ws = websocket.create_connection("ws://127.0.0.1:80/data/ws")
		except:
			print("ws connection error")
		return ws


	def sendDataToTornado(self, data):
		try:
			packet = {
				"type" : "RealTimeData",
				"payload" : str(data)
			}
			self.wsHandler.send(json.dumps(packet))
		except:
			self.wsHandler.close()
			print("error sending data")


if __name__ == '__main__':
	subscriber = MQTTSubscriber("")
	subscriber.start()
	
