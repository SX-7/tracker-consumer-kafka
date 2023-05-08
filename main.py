import kafka as kf
import msgpack
from dotenv import load_dotenv
import os
from pytermgui import tim
import tkinter as tk
from datetime import datetime

load_dotenv()

server_ip = os.getenv("KAFKA_SERVER_IP")
kafka_username = os.getenv("KAFKA_USERNAME")
kafka_password = os.getenv("KAFKA_PASSWORD")

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
                            # prone to failures with current setup, might require few tries to work
                            sasl_plain_password=kafka_password, auto_offset_reset="earliest"
                            )

if consumer.bootstrap_connected():
    tim.print("[blue]INIT[/]    Estabilished connection with Kafka server")


kafka_messages_list = []


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
    for _, records in pool_data.items():
        for record in records:
            message_list.insert(tk.END, datetime.utcfromtimestamp(int(
                record.timestamp/1000)).strftime('%Y-%m-%d %H:%M:%S')+" "+create_label(record.value))
            kafka_messages_list.append(record.value)
    root.after(1000, update_pooler)


def generate_details(evt: tk.Event):
    try:
        message_data = kafka_messages_list[evt.widget.curselection()[0]]
    except IndexError:
        # this will frequently fail, if clicked not onto a proper element in the list
        return
    detail_list.delete(0,tk.END)
    detail_list.insert(tk.END,"General description of the event")
    detail_list.insert(tk.END,"Action")
    detail_list.insert(tk.END,"Time")
    detail_list.insert(tk.END,"In case of messages, here we put allllll of the message info that we have")
    detail_list.insert(tk.END,"We also provide a callback that'd let us copy any on the elements :)")
    detail_list.insert(tk.END,"If this is an editable, ofc we add another field for edited message")
    detail_list.insert(tk.END,"Bulk is... we'll see later, but not forget")
    detail_list.insert(tk.END,"Emojis getting added and removed should be the same, really")
    detail_list.insert(tk.END,"No, we won't download the emojis, just in case, but we can do that")
    detail_list.insert(tk.END,"And, ofc, don't forget the emojis funs with multiples")
    detail_list.insert(tk.END,"Have some message data")
    detail_list.insert(tk.END,message_data)


# initialize creation
root = tk.Tk(className="Consumer")

# create container on the left side of the window, put message list relevant data there
scrollbar_msg = tk.Scrollbar(root)
scrollbar_msg.pack(side=tk.LEFT, fill=tk.Y)
message_list = tk.Listbox(root, yscrollcommand=scrollbar_msg.set)
message_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar_msg.config(command=message_list.yview)

detail_list = tk.Listbox(root)
detail_list.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

message_list.bind('<<ListboxSelect>>', generate_details)

# create details list


# start loop
update_pooler()
root.mainloop()
