# Stores the string to send and other attributes, and deals with delivery.

import time
from generalised_twitch_module import *

class ChatString:
    def __init__(self, name, oauth, channel, is_mod = 0):
        # Twitch connection tomfoolery
        self.twitch = TwitchConnection(name, oauth, channel, is_mod)
        self.twitch.connect()
        print("Connecting to: " + channel)
        self.reset()
        self.last_message_end_time = time.perf_counter()
        
    def reset(self):
        self.message = ""
        self.last_add_time = None
        self.duration = 0

    def add_button(self, button, pos):
        thistime = time.perf_counter()
        if pos == 1:
            prefix = "_"
        else:
            prefix = "-"
        if self.last_add_time != None:  # This isn't the first action
            wait_time_ms = int(1000 * (thistime - self.last_add_time))
            self.message += "  #{}ms  ".format(wait_time_ms)
            self.duration += wait_time_ms
        self.message += prefix+button
        self.last_add_time = thistime
    
    def add_macro(self, macro):
        thistime = time.perf_counter()
        if self.last_add_time != None:  # This isn't the first action
            wait_time_ms = int(1000 * (thistime - self.last_add_time))
            self.message += "  #{}ms  ".format(wait_time_ms)
            self.duration += wait_time_ms
        self.message += macro
        self.last_add_time = thistime
    
    def update(self):
        self.twitch.update()
        
    def send(self):
        if self.message != "":
            #print(self.message)
            #print("Optimising...")
            self.message = self.optimise()
            #print(self.message + "\n")
            #print("Pre-Op Duration: {}ms\n===".format(self.duration))
            self.twitch.send(self.message)
            self.last_message_end_time = time.perf_counter()*1000 + self.duration
        self.twitch.update()
        self.reset()
    
    def optimise(self):
        if self.message == "":
            return ""
        
        tokens = self.message.split("  ")
        
##        # Remove Starting A releases
##        if tokens[0] == "-a":
##            tokens.pop(0)
##            tokens.pop(1)
        
        # Replace near-seconds with seconds
        for i in range(len(tokens)):
            t = tokens[i]
            if t.startswith("#") and t.endswith("ms"):
                ms = int(t[1:-2])
                dist = abs(ms - round(ms, -3))
                if dist <= 50:
                    tokens[i] = "#{}s".format(round(ms, -3)//1000)
        
        # Replace #0s with +
        for i, token in enumerate(tokens):
            if token == "#0s":
                tokens[i] = "+"
        ##for i in range(tokens.count("#0s")):
        ##    tokens[tokens.index("#0s")] = "+"
        
        # Replace "_a #888ms -a" with "a888ms". It's painfully messy, sorry.
        new_tokens = []
        i = 0
        while i < len(tokens):
            a, b, c, d = (tokens+[""]*3)[i:i+4]
            # If A is a push and C is a release, of the same button
            if a.startswith("_") and c.startswith("-") and a[1:] == c[1:] \
               and b.startswith("#") and d != '+': # ... AND b is a delay, and d is not +
                new_tokens.append(a[1:]+b[1:]) # Then simplify to "a888ms" form
                i += 3
            else:
                new_tokens.append(a)
                i += 1
        tokens = new_tokens
        
        # Replace near-200/400ms with periods
        for i in range(len(tokens)):
            t = tokens[i]
            if t.startswith("#") and t.endswith("ms"):
                ms = int(t[1:-2])
                if abs(ms - 200) <= 25: # Duration is close to 200ms
                    tokens[i] = "."
                elif abs(ms - 400) <= 25: # Duration is close to 400ms
                    tokens[i] = ".."
                elif abs(ms - 600) <= 25: # Duration is close to 600ms
                    tokens[i] = "..."
                elif abs(ms - 800) <= 25: # Duration is close to 800ms
                    tokens[i] = "...."                        

        cont = True
        while cont:
            cont = False
            # Remove any released buttons at the end of string because that's automatic
            if tokens and tokens[-1].startswith("-"):
                tokens.pop()
                cont = True
            
            # Remove trailing pluses
            if len(tokens) > 0:
                if tokens[-1] == "+":
                    tokens.pop()
                    cont = True
        
        # Reconstruct String
        return "".join(tokens)

#===============================================================================
#@ STEALTHY REDIRECT                                                           |
#===============================================================================
if __name__ == "__main__":
    print("[Redirecting to main.py]")
    import main
#===============================================================================
