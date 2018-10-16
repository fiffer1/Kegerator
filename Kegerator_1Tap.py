# File Name: Kegerator_1Tap.py
# Created By: Kayser-Sosa, with help from ThatGuyYouKnow and JackBurtonn.
# Minor changes by: fiffer1 to include multiple temperature sensors and display for just one tap

# Use: Displays information about the beers, how much is left in the kegs, and kegerator temperatures.

# Code modified from - Adafruit Kegomatic
# https://learn.adafruit.com/adafruit-keg-bot


# convert liter to gal and back because didnt want to fig out flowmeter.py
# store current values to another file, check file before reloading


# Imports ======================================================================================================================
import os
import sys
import time
import math
import logging
import pygame, sys
from pygame.locals import *
import RPi.GPIO as GPIO
from flowmeter import *
from beerinfo import *

sys.path.append('/home/pi/Projects/SendMail')
from SendMail_API import send_mail


# GPIO Setup ===================================================================================================================
GPIO.setmode(GPIO.BCM) # use real GPIO numbering
#GPIO.setup(23,GPIO.IN, pull_up_down=GPIO.PUD_UP) # Left Tap, Beer 1
GPIO.setup(24,GPIO.IN, pull_up_down=GPIO.PUD_UP) # Middle Tap, Beer 2
#GPIO.setup(25,GPIO.IN, pull_up_down=GPIO.PUD_UP) # Right Tap, Beer 3
# Flow Meter Wiring: Red = 5-24VDC, Black = Ground, Yellow = GPIO Pin


# Initialize Pygame ============================================================================================================
pygame.init()


# Read/Write File ==============================================================================================================
FILENAME = '/home/pi/Projects/Kegerator/flowMeterValues.txt'


# Hide the Mouse ===============================================================================================================
pygame.mouse.set_visible(False)


# Flow Meters Setup ============================================================================================================
flowMeter1 = FlowMeter('gallon', ["beer"]) # Left Tap, Beer 1
flowMeter2 = FlowMeter('gallon', ["beer"]) # Middle Tap, Beer 2
flowMeter3 = FlowMeter('gallon', ["beer"]) # Right Tap, Beer 3
# Inputs - FlowMeter('displayFormat', ['beverage'])
                                        # displayFormat (select ONE): liter, pint, gallon
                                        # beverage = beer


# Read Saved Values from flowMeterValues.txt ++=================================================================================
# The text file is in gallons and totalPour is in liters so each needs to be converted from gal to L
with open(FILENAME,'r') as f:
        lines = f.readlines()
        flowMeter1.totalPour = float(lines[0]) * 3.7854
        flowMeter2.totalPour = float(lines[1]) * 3.7854
        flowMeter3.totalPour = float(lines[2]) * 3.7854
f.closed


# Colors Setup =================================================================================================================
# http://www.rapidtables.com/web/color/RGB_Color.htm
BLACK = (0,0,0)
WHITE = (255,255,255)
TGREEN = (80,200,100) # PC Terminal Green
RED = (255,0,0)
ORANGE = (255,128,0)
YELLOW = (255,255,0)
PINK = (255,51,255)
BLUE = (0,0,255)


# Text Backgroud Color for each beer
BEER1Bg = BLACK
BEER2Bg = None
BEER3Bg = BLACK


# Window Surface Setup =========================================================================================================
#VIEW_WIDTH = 1024 # original number 1024
#VIEW_HEIGHT = 600 # original number 576
VIEW_WIDTH = 1440
VIEW_HEIGHT = 900
pygame.display.set_caption('Kegerator')
screen = pygame.display.set_mode((VIEW_WIDTH,VIEW_HEIGHT), FULLSCREEN, 32)

#Resizable used for testing
#screen = pygame.display.set_mode((VIEW_WIDTH,VIEW_HEIGHT), RESIZABLE, 32)
windowInfo = pygame.display.Info()


# Backgrounds Setup ============================================================================================================
#background = pygame.image.load('/home/pi/Projects/Kegerator/images/Beer-Background.jpg')
background = pygame.image.load('/home/pi/Projects/Kegerator/images/Black.png')


# Rendering ====================================================================================================================
def renderThings(flowMeter2, screen, pint, mug, pilsner, weizen, tulip, snifter, goblet,
        BEER2Text, beer2name, beer2style, beer2ibu, beer2abv, beer2glasspic):

        # Clear the screen
        screen.blit(background,(0,0))

        #text formatting
        #https://pygame-zero.readthedocs.io/en/latest/ptext.html
        
        # Beer 2 Details - Middle Tap ==============================================================================================
        
        #https://stackoverflow.com/questions/32673965/pygame-blitting-center
        #centering text
        
        
        # Beer 2 Title
        screenfont = pygame.font.SysFont(None, 60)
        screenfont.set_underline(1)
        rendered = screenfont.render("On Tap", True, RED, BEER2Bg)
        screen.blit(rendered, (650, 0))

        # Beer 2 Tap
        screen.blit(beer2glasspic, (50, 135))
        
        # Beer 2 Name
        screenfont = pygame.font.SysFont(None, 100)
        rendered = screenfont.render(beer2name, True, RED, BEER2Bg)
        screen.blit(rendered, (475,125))
                                           
##        # Beer 2 Separator Line
##        screenfont = pygame.font.SysFont(None, 20)
##        rendered = screenfont.render('________________________________', True, BEER2Text, BEER2Bg)
##        screen.blit(rendered, (550, 160))
                
        # Beer 2 Style
        screenfont = pygame.font.SysFont(None, 55)
        rendered = screenfont.render(beer2style, True, BEER2Text, BEER2Bg)
        screen.blit(rendered, (750, 250))
        
##        # Beer 2 Original Gravity (OG) - Don't even know what this is, so not including it
##        screenfont = pygame.font.SysFont(None, 45)
##        rendered = screenfont.render(beer2OG, True, BEER2Text, BEER2Bg)
##        screen.blit(rendered, (550, 220))
        
        # Beer 2 International Bittering Units (IBU)
        screenfont = pygame.font.SysFont(None, 55)
        rendered = screenfont.render(beer2ibu, True, BEER2Text, BEER2Bg)
        screen.blit(rendered, (750, 290))
        
        # Beer 2 Alcohol / Volume (ABV)
        screenfont = pygame.font.SysFont(None, 55)
        rendered = screenfont.render(beer2abv, True, BEER2Text, BEER2Bg)
        screen.blit(rendered, (750, 330))

        # Beer 2 Poured in Pints
        if flowMeter2.enabled:
                totalPour = flowMeter2.getFormattedTotalPour()
                thisPour = flowMeter2.getFormattedThisPour()
                thisPourText = 'Pouring ' + thisPour + ' Pints'

                #If it's been 2.5 seconds since the last pour, then consider this pour complete and reset 
                if (currentTime - flowMeter2.lastClick > 2500):
                        flowMeter2.thisPour = 0.00
                        thisPourText = ''

                        #Send a text if more than 0.2 pints has been poured
                        #if float(thisPour) > 0.2:
                                #send_mail('Party On!','Beer has been poured (' + thisPourText + ' Pints)')
                                
                screenfont = pygame.font.SysFont(None, 55)
                rendered = screenfont.render(thisPourText, True, YELLOW, BEER2Bg)
                textRect = rendered.get_rect()
                screen.blit(rendered, (720, 560))

				#totalPour is returned as string, so convert to float and round then convert to string again
                screenfont = pygame.font.SysFont(None, 45)
                rendered = screenfont.render(str(round(float(totalPour),2)) + ' gallons remaining', True, ORANGE, BEER2Bg)
                textRect = rendered.get_rect()
                screen.blit(rendered, (720,630))

        
        # Kegerator Temps ===========================================================================================================
		# The temperatures are recorded in SensorTemps.txt.  So read from that file to get the values for each sensor.
        d = {}
        with open('/home/pi/Projects/Temperature/SensorTemps.txt') as f:
                for line in f:
                        (key,val) = line.split()
                        d[key] = val
        
        if 'Tower' in d:
                Tower_temp = d['Tower']
        else:
                Tower_temp = ' '
                
        if 'Top' in d:
                Top_temp = d['Top']
        else:
                Top_temp = ' '
                
        if 'Bottom' in d:
                Bottom_temp = d['Bottom']
        else:
                Bottom_temp = ' '

        TowerDisp = ' Keg Temps:             Tower = ' + Tower_temp
        TopDisp = 'Top = ' + Top_temp
        BottomDisp = 'Bottom = ' + Bottom_temp

		#Set color of temperature displayed based on the temperature range
        if Tower_temp != ' ':
                if float(Tower_temp) < 35:
                        tempColor = BLUE
                elif float(Tower_temp) > 45:
                        tempColor = RED
                else:
                        tempColor = TGREEN
        else:
                tempColor = TGREEN

        screenfont = pygame.font.SysFont(None, 45)
        rendered = screenfont.render(TowerDisp, True, tempColor, None)
        screen.blit(rendered, (200, 765))

        if Top_temp != ' ':
                if float(Top_temp) < 35:
                        tempColor = BLUE
                elif float(Top_temp) > 45:
                        tempColor = RED
                else:
                        tempColor = TGREEN
        else:
                tempColor = TGREEN

        screenfont = pygame.font.SysFont(None, 45)
        rendered = screenfont.render(TopDisp, True, tempColor, None)
        screen.blit(rendered, (730, 765))

        if Bottom_temp != ' ':
                if float(Bottom_temp) < 35:
                        tempColor = BLUE
                elif float(Bottom_temp) > 45:
                        tempColor = RED
                else:
                        tempColor = TGREEN
        else:
                tempColor = TGREEN

        screenfont = pygame.font.SysFont(None, 45)
        rendered = screenfont.render(BottomDisp, True, tempColor, None)
        screen.blit(rendered, (940, 765))
     
        # Date / Time ==============================================================================================================
        # Date & Time required internet access to initially set
        #screenfont = pygame.font.SysFont(None, 35)
        #rendered = screenfont.render(time.strftime("%I:%M:%S %p - %Y/%m/%d"), True, WHITE, BLACK)
        #screen.blit(rendered, (0, 575))
        
                
        # Display everything
        pygame.display.flip()

    
# Flowmeter Updates ============================================================================================================
# Beer 1, on Pin 23.
def doAClick1(channel):
        currentTime = int(time.time() * FlowMeter.MS_IN_A_SECOND)
        if flowMeter1.enabled == True:
                flowMeter1.update(currentTime)
                saveValues(flowMeter1, flowMeter2, flowMeter3)

# Beer 2, on Pin 24.  Used for single tap installation
def doAClick2(channel):
        currentTime = int(time.time() * FlowMeter.MS_IN_A_SECOND)
        if flowMeter2.enabled == True:
                flowMeter2.update(currentTime)
                saveValues(flowMeter1, flowMeter2, flowMeter3)

# Beer 3, on Pin 25.
def doAClick3(channel):
        currentTime = int(time.time() * FlowMeter.MS_IN_A_SECOND)
        if flowMeter3.enabled == True:
                flowMeter3.update(currentTime)
                saveValues(flowMeter1, flowMeter2, flowMeter3)

#GPIO.add_event_detect(23, GPIO.RISING, callback=doAClick1, bouncetime=20) # Beer 1, on Pin 23
GPIO.add_event_detect(24, GPIO.RISING, callback=doAClick2, bouncetime=20) # Beer 2, on Pin 24
#GPIO.add_event_detect(25, GPIO.RISING, callback=doAClick3, bouncetime=20) # Beer 3, on Pin 24


# Erase & Save New Data to File +===============================================================================================
def saveValues(flowMeter1, flowMeter2, flowMeter3):
        f = open(FILENAME, 'w')
        if flowMeter1.enabled == True:
                f.write(flowMeter1.getFormattedTotalPour() + "\n")
        if flowMeter2.enabled == True:
                f.write(flowMeter2.getFormattedTotalPour() + "\n")
        if flowMeter3.enabled == True:
                f.write(flowMeter3.getFormattedTotalPour() + "\n")
        f.close()


# Main Never Ending Loop =======================================================================================================
while True:
        # Handle keyboard events
        for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                        GPIO.cleanup()
                        pygame.quit()
                        sys.exit()
                elif event.type == KEYUP and event.key == K_1:
                        flowMeter1.enabled = not(flowMeter1.enabled)
                elif event.type == KEYUP and event.key == K_2:
                        flowMeter2.enabled = not(flowMeter2.enabled)
                elif event.type == KEYUP and event.key == K_3:
                        flowMeter3.enabled = not(flowMeter3.enabled)
                elif event.type == KEYUP and event.key == K_8:
                        flowMeter1.clear()
                elif event.type == KEYUP and event.key == K_9:
                        flowMeter2.clear()
                elif event.type == KEYUP and event.key == K_0:
                        flowMeter3.clear()
  
        currentTime = int(time.time() * FlowMeter.MS_IN_A_SECOND)
  
# Update the screen ===============================================================================================================
        renderThings(flowMeter2, screen, pint, mug, pilsner, weizen, tulip, snifter, goblet,
                BEER2Text, beer2name, beer2style, beer2ibu, beer2abv, beer2glasspic)

