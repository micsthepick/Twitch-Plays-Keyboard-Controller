# Default version of cfg.py, in case you mess your current one up
# Create a copy of this file and rename it "cfg.py" to revert to default

HOST = "irc.twitch.tv"              # the Twitch IRC server
PORT = 6667                         # always use port 6667!
CHAN = "twitchplays_everything"     # the channel you want to join

NICK = "username"                   # your Twitch username, lowercase
PASS = "oauth:xxxxxxxxxxxxxxxxxxxxxxxxx" # your Twitch OAuth token ( https://twitchapps.com/tmi/ )



""" Special Keys """
RESET = "escape"         # This key will delete the current message being built
SEND = "return"          # This key will send the current message to twitch


""" Keybindings - what text to bind to each keyboard key
        
        "w": "text",          Sends " _text " on w press, " -text " on release
        "d": "#mash(b)",      Sends " #mash(b) " on d press, nothing on release
        "]": "!loadstate 6"   Sends " !loadstate 6 " on pressing the ] key, nothing on release

if the text starts with "#" it will be treated as a call to a macro
if the text starts with "!" it will be treated as a call to a command
(Because buttons have a "time held" duration, but macros/commands do not)

Bear in mind that most !commands (like !loadstate 6) will only work when they are sent by themselves

Key names are Case-Sensitive and should always be lowercase

Make sure not to use the keys bound to SEND or RESET
"""

KEYBINDINGS = {
     "p": "#p",
     "space": "a",
     "w": "b",
     "a": "left",
     "s": "down",
     "d": "right",
     "e": "up",
     "leftshift": "y",
     "r": "!loadstate 6",
     "t": "!savestate 6",
}









""" Other junk that should be left alone """
DEBUG_MODE = False
MOD_MODE = False

if MOD_MODE:
     MAX_CHAT_RATE = (99/30)
else:
     MAX_CHAT_RATE = (19/30)
CHAT_WAIT_TIME = 1 / MAX_CHAT_RATE
