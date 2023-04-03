from kafka import KafkaConsumer

# To consume latest messages and auto-commit offsets
consumer = KafkaConsumer('my-topic',
                         bootstrap_servers=[':9092'],
                         request_timeout_ms=10000,
                         session_timeout_ms=5000,
                         security_protocol="",
                         sasl_mechanism="",
                         sasl_plain_username="",
                         sasl_plain_password="")

print(consumer.metrics())