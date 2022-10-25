import sys

from paho.mqtt import client
from string import ascii_letters
from random import choice

from paho.mqtt.client import MQTTv311


class Client(client.Client):
    def __init__(self, broker_address, id="P1"):
        super(Client, self).__init__(id, protocol=MQTTv311)
        self.connect(broker_address)

    def subscribe_list(self, topics):
        for t in topics:
            self.subscribe(t)


    def start(self):
        self.loop_start()

def random_name(length):
    return ''.join(choice(ascii_letters) for _ in range(length))


if __name__ == '__main__':
    if len(sys.argv) > 2:
        topic = sys.argv[1]
        role = sys.argv[2]
        broker = '172.21.144.106'
        port = 1883
        c = Client(broker, id=random_name(15))
        c.publish(topic, role)
