import random
import time
import sys
import argparse
import paho.mqtt.publish as publisher
import json

class DatasetGenerator:
    HOSTNAME = "192.168.89.103"

    def __init__(self):
        self.createArgumentsParser()

    def start(self):
        args = self.parser.parse_args()
        self.sendDataEveryNSeconds(args.id, args.name, args.topic, args.tsamp, args.radius, args.length)

    def createArgumentsParser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--version", action="version", version="%(prog)s 0.0.1")
        parser.add_argument("-id", type=int, default=1)
        parser.add_argument("-t", "--topic", type=str, default="fermi/ssh/vinegar/balsamicLevel/")
        parser.add_argument("-ts", "--tsamp", type=int, default=10)
        parser.add_argument("-n", "--name", type=str, default="B0")
        parser.add_argument("-r", "--radius", type=int, default=25)
        parser.add_argument("-l", "--length", type=int, default=45)
        self.parser = parser

    def sendDataEveryNSeconds(self, id, name, topic, timeSample, radius, length):
        while True:
            data = json.dumps(self.generateDataset(id, name, radius, length)).encode("utf-8")

            print(data)
            try:
                publisher.single(
                    topic=topic,
                    payload=data,
                    qos=0,
                    retain=True,
                    hostname=self.HOSTNAME,
                    port=1883)
            except:
                print("Unable to publish data")
                
            time.sleep(timeSample)

    def generateDataset(self, id, name, radius, length):
        data = {
            "id" : id,
            "name": name,
            "time" : int(time.time()),
            "radius" : radius,
            "length" : length,
            "level" : self.generateLevel()
        }
        return data

    def generateLevel(self):
        intPart = random.randint(5, 15)
        #decPart = random.randint(0, 99)
        return f'{intPart}'#.{decPart}'
        

if __name__ == "__main__":
    generator = DatasetGenerator()
    generator.start()
    

