#!/usr/bin/env python
#coding: Latin-1

import SocketServer
import time
import os
import sys
from Adafruit_PWM_Servo_Driver import PWM
pwm = PWM(0x40)
pwm.setPWMFreq(50)
# Settings for the RemoteROV server
portListen = 9038                      
global motorMin 
global motorNuetral
global motorMax
#global throttleRange = motorMax - motorNeutral
# Class used to handle UDP messages
class rovHandler(SocketServer.BaseRequestHandler):
    joyData=[]
    motorMin = 170;
    motorNuetral = 330;
    motorMax = 450;
    throttleRange = motorMax - motorNuetral;

    def handle(self):
        global isRunning
        request, socket = self.request     # Read who spoke to us and what they said
        request = request.upper()          # Convert command to upper case
        if request == 'ALLOFF':
            exit()
        self.joyData = request.split(',') # Separate the command into individual drives
        #print self.joyData
        self.runMotors()
        if self.joyData[13] == '1':
            print "starting camera stream..."
            os.system("raspivid -t 999999 -w 640 -h 480 -vf -o - | nc 10.42.0.1 5001 &" )

    def runMotors(self):
        xLeftJoy = float(self.joyData[0])
        yLeftJoy = float(self.joyData[1])
        xRightJoy = float(self.joyData[2])
        yRightJoy = float(self.joyData[3])
       
        turn = [1,-1,0,0,-1,1]
        moveForward = [-1,-1,0,0,1,1]
        moveBackward = [-1,-1,0,0,1,1]
        strafe = [-1,1,0,0,-1,1]
        up = [0,0,-1,-1,0,0]

        for motor in range(0,6):
            speed = 0
            if abs(yLeftJoy) > .01:
                speed = speed + (moveForward[motor]*yLeftJoy)
            if abs(xLeftJoy) > .01:
                speed = speed + (strafe[motor]*xLeftJoy)
            if abs(xRightJoy) > .01:
                speed = speed + (turn[motor]*xRightJoy)
            if abs(yRightJoy) > .01:
                speed = speed + (up[motor]*yRightJoy)
            print "motor " , motor+1 , " " , speed
            if speed > 1:
                speed = 1
            if speed < -1:
                speed = -1
            speed =self.motorNuetral+(speed*self.throttleRange)
            pwm.setPWM(motor,0,int(speed))
    

        
        #print "LeftX: %.2f LeftY: %.2f RightX: %.2f RightY: %.2f" %(float(driveCommands[0]),float(driveCommands[1]),float(driveCommands[2]),float(driveCommands[3]))          

try:
    global isRunning

    SocketServer.UDPServer.allow_reuse_address = True
    # Start by turning all drives off
    #raw_input('You can now turn on the power, press ENTER to continue')
    # Setup the UDP listener
    remoteRovServer = SocketServer.UDPServer(('', portListen), rovHandler)
    # Loop until terminated remotely
    isRunning = True
    while isRunning:
        remoteRovServer.handle_request()
    print 'Finished'
except KeyboardInterrupt:
    print 'Terminated'
