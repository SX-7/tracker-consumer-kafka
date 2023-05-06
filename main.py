from kafka import KafkaConsumer
import msgpack
from dotenv import load_dotenv
import os
from pytermgui import tim

load_dotenv()

server_ip = os.getenv("KAFKA_SERVER_IP")
kafka_username=os.getenv("KAFKA_USERNAME")
kafka_password=os.getenv("KAFKA_PASSWORD")

# To consume latest messages and auto-commit offsets
consumer = KafkaConsumer(f'discord-{kafka_username}-all',
                         bootstrap_servers=[str(server_ip)],
                         request_timeout_ms=10000,
                         session_timeout_ms=5000,
                         value_deserializer=msgpack.unpackb,
                         key_deserializer=msgpack.unpackb,
                         sasl_mechanism="PLAIN",
                         security_protocol="SASL_PLAINTEXT",
                         sasl_plain_username=kafka_username,
                         sasl_plain_password=kafka_password,
                         auto_offset_reset="earliest"
                         )

if consumer.bootstrap_connected():
    tim.print("[blue]INIT[/]    Estabilished connection with Kafka server")

try:
    for message in consumer:
        tim.print(f'Topic {message.topic}, partition {message.partition}, offset {message.offset}, key {message.key}, action {message.value["action_id"]}')
except KeyboardInterrupt:
    consumer.close