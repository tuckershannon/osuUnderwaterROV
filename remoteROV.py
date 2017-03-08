#!/usr/bin/env python
# coding: Latin-1

# Load library functions we want
import socket
import time
import pygame

# Settings for the RemoteJoyBorg client
broadcastIP = '192.168.2.2'           # IP address to send to, 255 in one or more positions is a broadcast / wild-card
broadcastPort = 9038                    # What message number to send with
leftDrive = 1                           # Drive number for left motor
rightDrive = 4                          # Drive number for right motor
interval = 0.1                          # Time between updates in seconds, smaller responds faster but uses more processor time
regularUpdate = True                    # If True we send a command at a regular interval, if False we only send commands when keys are pressed or released

# Setup the connection for sending on
sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)       # Create the socket
sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)                        # Enable broadcasting (sending to many IPs based on wild-cards)
sender.bind(('0.0.0.0', 0))                                                         # Set the IP and port number to use locally, IP 0.0.0.0 means all connections and port 0 means assign a number for us (do not care)

# Setup pygame and key states
global hadEvent
global moveQuit
hadEvent = True
moveQuit = True
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
screen = pygame.display.set_mode([300,300])
pygame.display.set_caption("UnderwaterROV - Press [ESC] to quit")

# Function to handle pygame events
def PygameHandler(events):
    # Variables accessible outside this function
    global hadEvent
    global moveQuit
    global joystickData
    global buttonData
    # Handle each event individually
    for event in events:
        if joystick.get_button(8):        
            moveQuit = False
        joystickData = []
        hadEvent = True
        axes = joystick.get_numaxes()
        for i in range(axes):
             joystickData.append(str(joystick.get_axis(i)))
        nButtons = joystick.get_numbuttons()
        for j in range(nButtons):
            pressed = joystick.get_button(j)
            if pressed:
                joystickData.append(1)
            else:
                joystickData.append(0)
        arrowKeys = joystick.get_hat(0)
        joystickData.extend(arrowKeys)
try:
    print ('Press [ESC] to quit')
    # Loop indefinitely
    while moveQuit:
        # Get the currently pressed keys on the keyboard
        PygameHandler(pygame.event.get())
        if hadEvent or regularUpdate:
            # Keys have changed, generate the command list based on keys
            hadEvent = False
        axesString = ",".join(str(x) for x in joystickData)
        sender.sendto(axesString.encode('utf-8'), (broadcastIP, broadcastPort))
        time.sleep(interval)
    # Inform the server to stop
    sender.sendto('ALLOFF'.encode('utf-8'), (broadcastIP, broadcastPort))
except KeyboardInterrupt:
    # CTRL+C exit, inform the server to stop
    sender.sendto('ALLOFF'.encode('utf-8'), (broadcastIP, broadcastPort))
