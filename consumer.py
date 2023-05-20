import kafka as kf
import msgpack
from dotenv import load_dotenv
import os
from pytermgui import tim
import tkinter as tk
from datetime import datetime
from eventcontainer import EventContainer
from guihelpers import insert_message_info

load_dotenv()

server_ip = os.getenv("KAFKA_SERVER_IP")
kafka_username = os.getenv("KAFKA_USERNAME")
kafka_password = os.getenv("KAFKA_PASSWORD")

# To consume latest messages and auto-commit offsets
consumer = kf.KafkaConsumer(f'discord-{kafka_username}-all',
                            bootstrap_servers=[str(server_ip)],
                            request_timeout_ms=10000,
                            session_timeout_ms=5000,
                            value_deserializer=msgpack.loads,
                            key_deserializer=msgpack.loads,
                            sasl_mechanism="PLAIN",
                            security_protocol="SASL_PLAINTEXT",
                            sasl_plain_username=kafka_username,
                            sasl_plain_password=kafka_password
                            #, auto_offset_reset="earliest"
                            )

if consumer.bootstrap_connected():
    tim.print("[blue]INIT[/]    Estabilished connection with Kafka server")


kafka_messages_list: list[EventContainer] = []

def update_pooler():
    pool_data = consumer.poll()
    for _, records in pool_data.items():
        for record in records:
            event = EventContainer(record.value)
            message_list.insert(tk.END, datetime.utcfromtimestamp(int(
                record.timestamp/1000)).strftime('%Y-%m-%d %H:%M:%S')+" "+event.create_label())
            kafka_messages_list.append(event)
    root.after(1000, update_pooler)


# initialize creation
root = tk.Tk(className="Consumer")

# Create scrollbars
scrollbar_msg = tk.Scrollbar(root)
scrollbar_msg.pack(side=tk.LEFT, fill=tk.Y)
scrollbar_det = tk.Scrollbar(root)
scrollbar_det.pack(side=tk.RIGHT, fill=tk.Y)
# this one is for wide data in detiled view
scrollbar_det_hor = tk.Scrollbar(root, orient=tk.HORIZONTAL)
# we pack it later, as packing order matters
# create lists for displaying data
message_list = tk.Listbox(root, yscrollcommand=scrollbar_msg.set)
message_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
detail_list = tk.Listbox(
    root, yscrollcommand=scrollbar_det.set, xscrollcommand=scrollbar_det_hor.set)
scrollbar_det_hor.pack(side=tk.BOTTOM, fill=tk.X)
detail_list.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# connect scrollbars with respective lists
scrollbar_msg.config(command=message_list.yview)
scrollbar_det.config(command=message_list.yview)
scrollbar_det_hor.config(command=message_list.xview)


# "UI" creation, here for the lambda function in event binding
def generate_details(evt: tk.Event):
    try:
        message_data: EventContainer = kafka_messages_list[evt.widget.curselection()[
            0]]
    except IndexError:
        # this will frequently fail, if clicked not onto a proper element in the list
        return
    # clean display
    detail_list.delete(0, tk.END)
    # insert standardized label
    detail_list.insert(tk.END, message_data.create_label())
    # process reactions, if applicable
    if message_data.reactions:
        detail_list.insert(tk.END, "   ◎Relevant reactions")
        for reaction in message_data.reactions:
            detail_list.insert(tk.END, f"   ┠    Reaction: {reaction.name}")
            # unicode reactions have no links
            if reaction.url:
                detail_list.insert(tk.END, f"   ┃   ├   Link: {reaction.url}")
            detail_list.insert(tk.END, f"   ┃   └   Count: {reaction.count}")
        # for events 5 and 6
        if message_data.reaction_user:
            detail_list.insert(
                tk.END, f"   ◎By user: {message_data.reaction_user}")
    # go through messages
    if message_data.messages:
        detail_list.insert(tk.END, "   ◎Relevant messages")
        if message_data.action_id == 2:
            detail_list.insert(tk.END, "   ┎  Edited")
            insert_message_info(message_data.messages[0], detail_list)
            detail_list.insert(tk.END, "   ┎  Original")
            insert_message_info(message_data.messages[1], detail_list)
        elif message_data.action_id == 4:
            for message in message_data.messages:
                insert_message_info(message, detail_list)
        else:
            insert_message_info(message_data.messages[0], detail_list)


message_list.bind('<<ListboxSelect>>', generate_details)

# create details list


# start loop
update_pooler()
root.mainloop()
