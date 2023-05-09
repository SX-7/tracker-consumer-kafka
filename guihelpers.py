import tkinter as tk
from eventcontainer import Message
# template for text generation
def insert_message_info(message:Message,detail_list:tk.Listbox):
    detail_list.insert(tk.END,f"   ┠    ID: {message.id}")
    detail_list.insert(tk.END,f"   ┠    URL: {message.url}")
    detail_list.insert(tk.END,f"   ┠    Author")
    detail_list.insert(tk.END,f"   ┃    ├   Name: {message.author_name}")
    detail_list.insert(tk.END,f"   ┃    └   ID: {message.author_id}")
    detail_list.insert(tk.END,f"   ┠    Channel")
    detail_list.insert(tk.END,f"   ┃    ├   Name: {message.channel_name}")
    detail_list.insert(tk.END,f"   ┃    └   ID: {message.channel_id}")
    detail_list.insert(tk.END,f"   ┠    Created: {message.created}")
    if message.edited:
        detail_list.insert(tk.END,f"   ┠    Edited: {message.edited}")
    detail_list.insert(tk.END,f"   ┠    Type: {message.type}")
    detail_list.insert(tk.END,f"   ┠    Content")
    # most of these can, and usually will be void
    if message.stickers:
        detail_list.insert(tk.END,f"   ┠        Sticker")
        detail_list.insert(tk.END,f"   ┃        ├   Name: {message.stickers[0].name}")
        detail_list.insert(tk.END,f"   ┃        └   URL: {message.stickers[0].url}")
    if message.content:
        detail_list.insert(tk.END,f"   ┠        Text: {message.content}")
    if message.attachments:
        for attachment in message.attachments:
            detail_list.insert(tk.END,f"   ┠        Attachment")
            detail_list.insert(tk.END,f"   ┃        ├   Filename: {attachment.name}")
            detail_list.insert(tk.END,f"   ┃        └   URL: {attachment.url}")
    if message.reference_id:
        detail_list.insert(tk.END,f"   ┠    Referenced message")
        detail_list.insert(tk.END,f"   ┃    ├   ID: {message.reference_id}")
        detail_list.insert(tk.END,f"   ┃    └   URL: {message.reference_url}")
