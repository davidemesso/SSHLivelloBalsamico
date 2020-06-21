import time
import websocket
import json

while True:
	ws = websocket.create_connection("ws://balsamico.ssh.edu.it/data/ws")

	packet = {
        	"type" : "SensorsDataRequest",
        	"payload" : {}
	};

	ws.send(json.dumps(packet))
	print(ws.recv())
	time.sleep(50)
	ws.close()
