"""
Play TPE with a Keyboard

Author: Sam Stratton, 10th April 2018
Modified: micsthepick, 27th May 2018
"""

import time
import pygame
from pygame.locals import *
from traceback import format_exc

import cfg
from generalised_twitch_module import *

from chatString import ChatString


class Main:
    def __init__(self):
        self.enabled = True
        self.chatstring = ChatString(cfg.NICK, cfg.PASS, cfg.CHAN, cfg.MOD_MODE)
        
        self.lastkey = ""
        
        pygame.init()
        pygame.font.init()
        icon = pygame.image.load('tpe.png')
        pygame.display.set_icon(icon)
        pygame.display.set_caption("TPE Keyboard - by Taximadish")
        screen = pygame.display.set_mode((500, 200))
        clock = pygame.time.Clock()

        myfont = pygame.font.SysFont('Verdana', 16)

        BGCOLOR = 0x000000

        # Main Loop ============================================================
        self.running = True
        try:
            while self.running:
                print(end="") # StdOut flush basically
                
                # Clean Slate
                pygame.draw.rect(screen, BGCOLOR, ((0,0),(500,200)), 0)    
                    
                textsurface = myfont.render('This window needs focus to capture input.', False, (255, 255, 255))
                screen.blit(textsurface,(10,10))
                
                displaytext = self.chatstring.optimise()
                textsurface = myfont.render(displaytext[-45:], False, (200, 100, 255))
                screen.blit(textsurface,(10,60))
                
                mlen = len(displaytext)
                textsurface = myfont.render("Length: "+str(mlen)+" chars", False, (255, 0, 0) if mlen >= 400
                                            else (255, 255, 255))
                screen.blit(textsurface,(10,110))
                
                textsurface = myfont.render("Reset: "+cfg.RESET, False, (255, 255, 255))
                screen.blit(textsurface,(200,110))             
                
                textsurface = myfont.render("Send: "+cfg.SEND, False, (255, 255, 255))
                screen.blit(textsurface,(350,110))
                
                textsurface = myfont.render("Key Name: "+self.lastkey, False, (255, 255, 255))
                screen.blit(textsurface,(10,160))              
                
                pygame.display.flip()
                clock.tick(30)
                self.do_actions()
        # Loop Exit ============================================================
        except Exception as e:
            print(format_exc())
        finally:
            pygame.quit()
            print("Process Ended")
    
    def do_actions(self):
        events = pygame.event.get()
        requests = self.updateKeys(events)
        
        for action in requests:
            actions.perform(action, self.chatstring)        
        
    def toggleEnabled(self):
        self.enabled = False if (self.enabled == True) else True
        if self.enabled:
            self.trayicon.icon = "tpe.ico"
        else:
            self.trayicon.icon = "tpeDisabled.ico"
        self.trayicon.refresh_icon()
        self.updateMenuOptions()
    
    def updateMenuOptions(self):
        enableText = "Disable" if self.enabled else "Enable"
        self.menu_options = [ # [Name, function, ticked]
            [enableText, lambda: self.toggleEnabled(), False]
        ]
        self.trayicon.refresh_menu_options(self.menu_options)


    def updateKeys(self, events):
        """ Turn Key Events into Requests """
        requests = []
        for event in events:
            if event.type == pygame.QUIT:
##                pygame.display.quit()
                self.running = False
                return []
                
            if event.type == KEYUP:
                key = pygame.key.name(event.key).replace(" ", "")
                if key in cfg.KEYBINDINGS.keys():
                    value = cfg.KEYBINDINGS[key]
                    if value[0] not in {"#", "!"}:
                        self.chatstring.add_button(value, 0)
                    
            if event.type == KEYDOWN:
                key = pygame.key.name(event.key).replace(" ", "")
                self.lastkey = key
                if key == cfg.RESET:
                    self.chatstring.reset()                
                elif key == cfg.SEND:
                    self.chatstring.send()
                                
                if key in cfg.KEYBINDINGS.keys():
                    value = cfg.KEYBINDINGS[key]
                    if value[0] in {"#", "!"}:
                        self.chatstring.add_macro(value)
                    else:
                        self.chatstring.add_button(value, 1)
                
        
        return requests


# Go!
Main()
