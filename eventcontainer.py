class Reaction:
    '''
    Class used for storing reaction data

    Designed in line with reaction event messages
    '''
    name: str = None
    '''Unicode compliant emoji symbol, if not applicable then name of the emoji'''
    count: int = None
    '''Count of reactions of this type under an affected message'''
    url: str = None
    '''URL pointing to image of the emoji'''

    def __init__(self, reaction_data: dict) -> None:
        '''Extracts reaction info dictionary recieved from an event into a class'''
        self.name = reaction_data["name"]
        self.count = reaction_data["count"]
        self.url = reaction_data["url"]


class Sticker:
    '''
    Class used for storing sticker data

    Designed in line with sticker information within event messages
    '''
    name: str = None
    '''Name of the sticker, as seen in discord'''
    url: str = None
    '''URL pointing to the sticker image'''

    def __init__(self, sticker_data: dict) -> None:
        '''Extracts data from sticker info provided from an event'''
        self.name = sticker_data["name"]
        self.url = sticker_data["url"]


class Attachment:
    '''
    Class for storing attachment data

    In line with attachment format within events
    '''
    name: str = None
    '''Filename of the attachment'''
    url: str = None
    '''URL pointing to the resource'''

    def __init__(self, attachment_data: dict) -> None:
        '''Extracts data from attachment info provided from an event'''
        self.name = attachment_data["name"]
        self.url = attachment_data["url"]


class Message:
    '''
    Class holding all info relevant to the message that is provided from an event
    '''
    id: int = None
    '''ID of the message'''
    author_name: str = None
    '''Name of the author, in a display_name#discriminator fashion'''
    author_id: int = None
    '''User ID of the author'''
    content: str = None
    '''Message content, string or standardized message in english language, in case of system messages'''
    channel_name: str = None
    '''Channel name to which this message is relevant to'''
    channel_id: int = None
    '''ID of the channel to which this message is relevant to'''
    created: str = None
    '''Time of creation of this message, provided in YYYY-MM-DD HH-MM-SS+HH:MM (part after + is timezone)'''
    edited: str = None
    '''Time of edit of this message, provided in YYYY-MM-DD HH-MM-SS+HH:MM (part after + is timezone)
    
    Can be None, always will be None on new messages'''
    url: str = None
    '''URL pointing to the message'''
    type: str = None
    '''Type of the message, for non-system messages it'll be "default" or "reply"'''
    attachments: list[Attachment] = None
    '''List of the attachments, if applicable.'''
    stickers: list[Sticker] = None
    '''List of stickers, if applicable.'''
    reference_id: int = None
    '''If applicable, ID of the message referred to (pin, reply)
    
    Can be None, if it is, reference_url will too'''
    reference_url: str = None
    '''If applicable, URL to the message referred to (pin, reply)
    
    Can be None, if it is, reference_id will too'''

    def __init__(self, message_data: dict):
        self.id = message_data["id"]
        self.author_id = message_data["author"]["id"]
        self.author_name = message_data["author"]["name"]
        self.content = message_data["content"]
        self.channel_id = message_data["channel"]["id"]
        self.channel_name = message_data["channel"]["name"]
        self.created = message_data["created"]
        self.edited = message_data["edited"]
        self.url = message_data["url"]
        self.type = message_data["type"][0] # actually contains two pieces of data, so we take one
        self.attachments = [Attachment(attachment_data)
                            for attachment_data in message_data["attachments"]]
        self.stickers = [Sticker(sticker_data)
                         for sticker_data in message_data["stickers"]]
        if message_data["reference"]:
            self.reference_id = message_data["reference"]["id"]
            self.reference_id = message_data["reference"]["url"]


class EventContainer:
    '''Container for data retrieved from events. 

    Many events are incomplete, so refer to the action_id and attribute docstrings'''
    action_id: int = None
    '''
    Informs which type of event has been recorded.
    
    Events 1-4 are message related, while 5-8 are reaction related
    
    1: Message sent. 2: Message edited. 3: Message deleted. 4: Messages bulk deleted
    
    5: Reaction added. 6: Reaction removed. 7: Reactions bulk cleared. 8: Particular reaction cleared
    '''
    messages: list[Message] = None
    '''
    List of messages relevant to the event. Unless stated otherwise, will contain only one message.

    For reaction related events, it'll refer to the message reacted with.

    If message was edited, [0] will be the current message, and [1] will be the original one.

    In case of bulk delete it will contain an unknown number of messages.
    '''
    reaction_user: str = None
    '''
    Name of the user which added, or removed a reaction for events 5 and 6
    '''
    reactions: list[Reaction] = None
    '''
    List of reactions relevant to the events 5-8 
    
    Will be of length 1 except for event 7, where every element will refer to one emoji type removed.
    '''

    def __init__(self, message_data: dict):
        '''Reassigns the message_data dictionary recieved from the server into easier to use python object

        message_data: Dictionary containing the message data. Value of action_id will be used to determine the unpacking of the rest of the data
        '''
        self.action_id = message_data["action_id"]
        # Handle reactions
        if self.action_id in {5,6}:
            self.reaction_user= message_data["user"]
        if self.action_id in {5,6,8}:
            self.reactions=[Reaction(message_data["reaction"])]
        if self.action_id in {7}:
            self.reactions=[Reaction(reaction_data) for reaction_data in message_data["reaction"]]
        # Handle messages
        if self.action_id in {2}:
            self.messages=[Message(message_data["after"]),Message(message_data["before"])]
        elif self.action_id in {4}:
            self.messages=[Message(m_data) for m_data in message_data["messages"]]
        else:
            self.messages=[Message(message_data["message"])]

    def create_label(self) -> str:
        '''
        Creates a string containing a description of the event in english language.
        '''
        match self.action_id:
            case 1:
                return f"{self.messages[0].author_name} sent a message in {self.messages[0].channel_name}"
            case 2:
                return f"{self.messages[0].author_name} edited their message in {self.messages[0].channel_name}"
            case 3:
                return f"{self.messages[0].author_name}'s message was deleted in {self.messages[0].channel_name}"
            case 4:
                return "Messages got bulk deleted"
            case 5:
                return f"{self.reaction_user} added a {self.reactions[0].name} reaction to {self.messages[0].author_name}'s message"
            case 6:
                return f"{self.reaction_user} removed a {self.reactions[0].name} reaction from {self.messages[0].author_name}'s message"
            case 7:
                return f"All reactions were cleared from {self.messages[0].author_name}'s message"
            case 8:
                return f"All {self.reactions[0].name} reactions were removed from {self.messages[0].author_name}'s message"
