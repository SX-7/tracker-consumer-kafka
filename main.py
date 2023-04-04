from kafka import KafkaConsumer
import msgpack
from dotenv import load_dotenv
import os

load_dotenv()

server_ip = os.getenv("SERVER_IP")

# To consume latest messages and auto-commit offsets
consumer = KafkaConsumer('my-topic',
                         bootstrap_servers=[':9092'],
                         request_timeout_ms=10000,
                         session_timeout_ms=5000,
                         value_deserializer=msgpack.unpackb
                         )
print(consumer.bootstrap_connected())
for message in consumer:
    print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value))

