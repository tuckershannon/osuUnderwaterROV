#!/usr/bin/env python
#coding: Latin-1

import SocketServer


# Settings for the RemoteKeyBorg server
portListen = 9038                       # What messages to listen for (LEDB on an LCD)

# Class used to handle UDP messages
class PicoBorgHandler(SocketServer.BaseRequestHandler):
    # Function called when a new message has been received
    def handle(self):
        global isRunning
        request, socket = self.request     # Read who spoke to us and what they said
        request = request.upper()          # Convert command to upper case
        driveCommands = request.split(',') # Separate the command into individual drives
        print driveCommands
        #print "LeftX: %.2f LeftY: %.2f RightX: %.2f RightY: %.2f" %(float(driveCommands[0]),float(driveCommands[1]),float(driveCommands[2]),float(driveCommands[3]))
            

try:
    global isRunning

    # Start by turning all drives off
    raw_input('You can now turn on the power, press ENTER to continue')
    # Setup the UDP listener
    remoteKeyBorgServer = SocketServer.UDPServer(('', portListen), PicoBorgHandler)
    # Loop until terminated remotely
    isRunning = True
    while isRunning:
        remoteKeyBorgServer.handle_request()
    # Turn off the drives and release the GPIO pins
    print 'Finished'
    raw_input('Turn the power off now, press ENTER to continue')
except KeyboardInterrupt:
    # CTRL+C exit, turn off the drives and release the GPIO pins
    print 'Terminated'
    raw_input('Turn the power off now, press ENTER to continue')
