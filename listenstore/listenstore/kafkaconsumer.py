import json
import logging
from kafka import KafkaClient, SimpleConsumer
from .listen import Listen


class KafkaConsumer(object):
    def __init__(self, conf):
        self.log = logging.getLogger(__name__)
        self.client = KafkaClient(conf["kafka_server"])


    def start_listens(self, callback):
        # convert json dicts to Listen() for callback
        listenifyCallback = lambda x: callback(Listen.from_json(x))
        return self.start(listenifyCallback, b"listen-group", b"listens")


    def start(self, callback, group_name, topic_name):
        self.callback = callback
        self.group_name = group_name
        self.topic_name = topic_name
        self.log.info("KafkaConsumer subscribed to %s -> %s" % (group_name, topic_name))
        self.consumer = SimpleConsumer(self.client, self.group_name, self.topic_name)

        for message in self.consumer:
            json_data =  message.message.value
            try:
                data = json.loads(json_data)
            except ValueError as e:
                self.log.error("Cannot parse JSON: %s\n'%s'" % (str(e), json_data))

            try:
                self.callback(data)
            except ValueError as e:
                self.log.error("Cannot insert listen: %s" % str(e))
