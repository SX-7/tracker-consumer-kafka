import kafka as kf
import msgpack
from dotenv import load_dotenv
import os
from pytermgui import tim
import tkinter as tk
from datetime import datetime

load_dotenv()

server_ip = os.getenv("KAFKA_SERVER_IP")
kafka_username=os.getenv("KAFKA_USERNAME")
kafka_password=os.getenv("KAFKA_PASSWORD")

# To consume latest messages and auto-commit offsets
consumer = kf.KafkaConsumer(f'discord-{kafka_username}-all',
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

kafka_messages_list=[]

def create_label(message) -> str:
    match message["action_id"]:
        case 1:
            return message["message"]["author"]["name"]+" sent a message in "+message["message"]["channel"]["name"]
        case 2:
            return message["after"]["author"]["name"]+" edited their message in "+message["after"]["channel"]["name"]
        case 3:
            return message["message"]["author"]["name"]+"'s message was deleted in "+message["message"]["channel"]["name"]
        case 4:
            return "Messages got bulk deleted"
        case 5:
            return message["user"]+" added a "+message["reaction"]["name"]+" reaction to "+message["message"]["author"]["name"]+"'s message"
        case 6:
            return message["user"]+" removed a "+message["reaction"]["name"]+" reaction from "+message["message"]["author"]["name"]+"'s message"
        case 7:
            return "All reactions were cleared from "+message["message"]["author"]["name"]+"'s message"
        case 8:
            return "All "+message["reaction"]["name"]+" reactions were removed from "+message["message"]["author"]["name"]+"'s message"
    return str(message["action_id"])+" yielded an error"
    

def update_pooler():
    pool_data = consumer.poll()
    for _,records in pool_data.items():
        for record in records:
            message_list.insert(tk.END,datetime.utcfromtimestamp(int(record.timestamp/1000)).strftime('%Y-%m-%d %H:%M:%S')+" "+create_label(record.value))
            kafka_messages_list.append(record.value)
    root.after(1000, update_pooler)

#initialize creation
root = tk.Tk(className="Consumer")

# generate scrollbars
scrollbar_msg = tk.Scrollbar(root)
scrollbar_det = tk.Scrollbar(root)
scrollbar_msg.pack( side = tk.LEFT, fill = tk.Y )
scrollbar_det.pack( side = tk.RIGHT, fill = tk.Y )

# create message list
message_list = tk.Listbox(root, yscrollcommand = scrollbar_msg.set)
message_list.pack( side = tk.LEFT, fill = tk.BOTH, expand=True)
scrollbar_msg.config( command = message_list.yview )

# create details list
detailed_list = tk.Listbox(root, yscrollcommand = scrollbar_det.set)
detailed_list.pack( side = tk.RIGHT, fill = tk.BOTH, expand=True)
scrollbar_det.config( command = detailed_list.yview )


update_pooler()
root.mainloop()
