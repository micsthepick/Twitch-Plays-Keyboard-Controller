import socket
import select
import time

# Set up connection
class TwitchConnection:
    def __init__(self, name, oauth, channel, is_mod = 0):
        self.HOST = "irc.twitch.tv"              # the Twitch IRC server
        self.PORT = 6667                         # always use port 6667!
        self.PING = "PING :tmi.twitch.tv"
        self.PONG = "PONG :tmi.twitch.tv\r\n".encode("utf-8")        
        
        self.NICK = name
        self.PASS = oauth
        self.CHAN = channel
        
        self.chat_cooldown = 1 / (19/30)
        if is_mod:
            self.chat_cooldown = 1 / (99/30)        
        
        self.sock = None
        self.connect()
        
        self.last_response_time = time.perf_counter()
        self.RECONNECT_TIMEOUT = 10 # Seconds. 0 or less = no reconnect
        
        self.raw_responses = []
        self.parsed_responses = []
        
        self.last_chat = None
        self.last_chat_time = time.perf_counter()
        self.pending_chats = []


    def connect(self):
        self.sock = socket.socket()
        retries = 0
        self.sock.connect((self.HOST, self.PORT))
        self.sock.send("PASS {}\r\n".format(self.PASS).encode("utf-8"))
        self.sock.send("NICK {}\r\n".format(self.NICK).encode("utf-8"))
        self.sock.send("JOIN #{}\r\n".format(self.CHAN).encode("utf-8"))
    
    def update(self):
        # Get new twitch responses
        ready = select.select([self.sock], [], [], 0.1) #timeout after waiting 0.1sec
        responses = []        
        if ready[0]:
            try:
                received = self.sock.recv(1024).decode("utf-8")
            except Exception:
                self.connect()
                received = ""
            responses = received.split("\r\n")
            responses.pop() # Last element will just be empty string due to the .split()  

        for response in responses:  # For all the new responses
            self.last_response_time = time.perf_counter()
            self.raw_responses.append(response)
            self.parsed_responses.append(Response(response))
                
            if response == self.PING:    # Twitch asks if we're still connected
                self.sock.send(self.PONG)    # Yes, we are
            
        
        # Send pending chats
        chat_cooldown_is_over = time.perf_counter() - self.last_chat_time
        if chat_cooldown_is_over and len(self.pending_chats) > 0:
            msg = self.pending_chats.pop(0) # Take first reply from pending list
            if msg == self.last_chat:
                msg = msg + "."
            self.sock.send("PRIVMSG #{} :{}\r\n".format(self.CHAN, msg).encode("utf-8"))
            self.last_chat = msg
            self.last_chat_time = time.perf_counter()
                  
        
        # Reconnect if we suspect we've been disconnected
        silence_time = time.perf_counter() - self.last_response_time
        if self.RECONNECT_TIMEOUT > 0 and self.RECONNECT_TIMEOUT < silence_time:
            self.sock.close()
            self.connect()
    
    def send(self, chat):
        self.pending_chats.append(chat)

#= Response Stuff ==============================================================

import re

CHAT_MSG = re.compile(r":\w+!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :")
JOIN_MSG = re.compile(r":\w+!\w+@\w+\.tmi\.twitch\.tv JOIN #")
SERVER_MSG = re.compile(r":tmi\.twitch\.tv \d\d\d \w+ :")
SERVER_MSG_2 = re.compile(r":\w+\.tmi\.twitch\.tv \d\d\d \w+( =)? #\w+ :")

class Response:
    typeformats = {"PRIVMSG": "{0} chatted: \"{1}\"",
                   "JOIN": "{0} joined chat.",
                   "ERROR": "No match for|| {2}",
                   "SERVERMSG": "Server says: \"{1}\""
                   }    
    def __init__(self, response):
        self.orig_response = response
        self.sender, self.r_type, self.message = get_data(response)
        SOH='\x01'
        if len(self.message) > 0 and self.message[0] == SOH:  # Dealing with "/me"
            newmsg = self.message[(1 + len("ACTION")):-1] #Strip SOHACTION ... SOH
            self.message = "/me" + newmsg
        
    def __str__(self):
        resp_str = self.typeformats[self.r_type].format(self.sender, self.message, self.orig_response)
        return resp_str
    
def get_data(response):
    r_type = "ERROR"
    sender = "[ERROR: Sender not computed]"
    message = "[ERROR: Message never computed]"
    if SERVER_MSG.match(response):
        r_type = "SERVERMSG"
        sender = "Server"
        message = SERVER_MSG.sub("", response) # Replace matched part of regex with ""
    elif SERVER_MSG_2.match(response):
        r_type = "SERVERMSG"
        sender = "Server"
        message = SERVER_MSG_2.sub("", response) # Replace matched part of regex with ""  
    elif JOIN_MSG.match(response):
        r_type = "JOIN"
        sender = re.search(r"\w+", response).group(0) # return the entire match
        message = JOIN_MSG.sub("", response) # Replace matched part of regex with ""        
    elif CHAT_MSG.match(response):
        r_type = "PRIVMSG"
        sender = re.search(r"\w+", response).group(0) # return the entire match
        message = CHAT_MSG.sub("", response) # Replace matched part of regex with ""
    else:
        r_type = "ERROR"
        sender = "?"
        message = response
    return (sender, r_type, message)

if __name__ == "__main__":
    NICK = "username"                   # your Twitch username, lowercase
    PASS = "oauth:XXXXXXXXXXXXXXXXXXX" # your Twitch OAuth token    
    
    a = TwitchConnection(NICK, PASS, "tec_xxii", False)
    
    while 1:
        a.update()
        for r in a.parsed_responses:
            if r.message.startswith("!pyramid "):
                p = r.message[len("!pyramid ")-len(r.message):]
                a.send(p)
                a.send(p+" "+p)
                a.send(p+" "+p+" "+p)
                a.send(p+" "+p)
                a.send(p)
        a.parsed_responses = []
