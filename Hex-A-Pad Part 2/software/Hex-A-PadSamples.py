#!/usr/bin/env python3
# Hex-A-Pad Sample player & sequence
# By Mike Cook January 2020

import sys
import time
import os
import board
import busio
import adafruit_mpr121
import digitalio as io
import pygame
import math
  
def main():
    global last_touch
    init()
    setMPR121()
    last_touch = cap.touched()
    print ('Hex-A-Pad sample player')
    drawFixed()
    while True :
        checkForEvent()
        checkPlaying()
        if playback : checkPlayback(False)
        if not capSenseNew.value:
            cur_touch = cap.touched()
            for i in range(0, 8):
                readPins(i, cur_touch)
            last_touch = cur_touch    

def readPins(i, c_touch) :
    global last_touch, playing, contPlay, recording
    pin_bit = 1 << i
    if c_touch & pin_bit and not last_touch & pin_bit:
      if i < 6 : LEDs[i].value = True
      if choices[0] : # 8 triggers
          if i == 6 : controlLEDs(0, 3)
          if i == 7 : controlLEDs(1, 3)
      if pygame.mixer.find_channel() :
          if choices[0] or i <6 :
              playing[i] = sounds[bank][i].play()
              if recording and i < 6 : saveNote(i)
              if i == 6 : contPlay[0] = True
              if i == 7 : contPlay[1] = True
              updateTrigger(i, True)
          elif choices[5] :
              if i == 6 : startRecording()
              if i == 7 : controlPlayback()
      else :
          print("channel overflow")

def saveNote(note) :
    global savePos, stepCount, playback
    if not playback : playback = True
    savePos += 1
    savePos = constrain(savePos, 0, 5)
    seqNotes[(stepCount + 1) & 0x0F][savePos] = note
    
def startRecording() :
    global stopping, playback, recording, savePos
    if not recording: # start recording
        wipeSequence()
        savePos = -1
        recording = True
        stopping = True # once round
        controlLEDs(0, 1)
    
def controlPlayback() :
    global stopping, playback, recording, nextStep, stepCount
    if recording and choices[1]: # step recording
        controlLEDs(1, 1)
        checkPlayback(True) # next step irrespective of time
        time.sleep(0.2) ; controlLEDs(1, 2)
    else :    
        if playback :
            stopping = True
            controlLEDs(1, 3)
        else :    
            nextStep = time.time()
            stepCount = -1
            controlLEDs(1, 1)
            playback = True
   
def checkPlayback(go) :
    global nextStep, stepCount, playback, stopping
    global recording, savePos
    if recording and choices[1] :
        nextStep = time.time() + 2.0
    if go : nextStep = 0.0
    if time.time() >= nextStep: # time for a new step
        nextStep = time.time() + stepTime
        stepCount = (stepCount + 1) & 0xF # 0 to 15
        updateStep(stepCount)
        if recording :
            savePos = -1
        else :
            if pygame.mixer.find_channel() :
                for i in range(0, 6) :
                    if seqNotes[stepCount][i] != -1 :
                        sounds[recordedBank][seqNotes[stepCount][i]].play()    
        if stepCount == 15 and stopping :    
            playback = False
            stopping = False
            recording = False
            controlLEDs(0, 2)
            controlLEDs(1, 2)
    
def updateTrigger(i,on):
    if i < 6 : col = (0,97,255)
    else : col = (255, 222, 0)
    if on :
        pygame.draw.circle(screen, col, dLED[i], 4, 0)
    else :
        pygame.draw.circle(screen, black,
                           dLED[i], 4, 0)
    pygame.display.update()

def updateChoices():
    for i in  range(0, len(choices)) :
        pygame.draw.rect(screen, backCol,
                         choiceRect[i], 0)
        pygame.draw.rect(screen, black,
                         choiceRect[i], 1)
        if choices[i] :
            screen.blit(yes, (choiceRect[i].left,
                              choiceRect[i].top))
        else :
            screen.blit(no, (choiceRect[i].left,
                             choiceRect[i].top))
    for i in range(0,len(incRect)) :
        pygame.draw.rect(screen, backCol,
                         incRect[i], 0)
        pygame.draw.rect(screen, black,
                         incRect[i], 1)
        if i & 1 :
            screen.blit(minus, (incRect[i].left,
                                incRect[i].top))
        else :
            screen.blit(plus, (incRect[i].left,
                               incRect[i].top))         
            
    pygame.draw.rect(screen, backCol, ((188, 400),
                                      (32, 16)), 0)            
    drawWords(str(bpm), 190, 400, black, backCol)            
    pygame.display.update()    

def drawFixed() :
    screen.fill(backCol)
    pygame.draw.circle(screen, (138, 229, 229),
                (sWide // 2, padCo[1] + 113), 149, 0)
    pygame.draw.circle(screen, backCol, (sWide // 2,
                            padCo[1] + 113), 127, 0)
    screen.blit(pad,padCo)    
    for i in range(0,8) :
        pygame.draw.circle(screen, black,
                           dLED[i], 4, 0)
    for i in range(0,16) :
        pygame.draw.circle(screen, black,
                           sLED[i], 8, 0)
    pygame.draw.circle(screen, (0, 0, 255),
                       sLED[12], 8, 0)            
    drawWords("8 triggers", 36, 340, black, backCol)
    drawWords("6 triggers", 240, 340, black, backCol)
    drawWords("Record Step", 36, 370, black, backCol)
    drawWords("Record Live", 240, 370, black, backCol)
    drawWords("BPM Playback", 36, 400, black, backCol)
    drawWords("X10", 305, 400, black, backCol)
    drawWords("Bank 1", 36, 430, black, backCol)
    drawWords("Bank 2", 36, 460, black, backCol)
    drawWords("Bank 3", 36, 490, black, backCol)
    controlLEDs(0, 2) ; controlLEDs(1, 2)
    updateChoices()    

def updateStep(s) :
    s = (s - 3) & 15
    scol = (0, 0, 255)
    pygame.draw.circle(screen, scol, sLED[s], 8, 0)
    s -= 1
    if s < 0 : s = 15
    pygame.draw.circle(screen, black, sLED[s], 8, 0)
    pygame.display.update()
    
def drawWords(words,x,y,col,backCol) :
    textSurface = font.render(words, True,
                              col, backCol)
    textRect = textSurface.get_rect()
    textRect.left = x # right for align right
    textRect.top = y    
    screen.blit(textSurface, textRect)
    return textRect

def init():
    global i2c, cap, capSenseNew, LEDs, sounds
    global pygame, soundNames, playing, contPlay
    global pad, sWide, sHigh, screen, backCol, seqNotes
    global padCo, dLED, sLED, black, font, ccol
    global choiceRect, yes, no, choices, incRect
    global plus, minus, bpm, stepTime, playback
    global nextStep, recording, stepCount, savePos
    global bank, recordedBank, stopping    
    i2c = busio.I2C(board.SCL, board.SDA)
    cap = adafruit_mpr121.MPR121(i2c)
    capSenseNew = io.DigitalInOut(board.D4)
    capSenseNew.direction = io.Direction.INPUT
    capSenseNew.pull = io.Pull.UP
    LEDs = []
    LEDpin = [board.D17, board.D18, board.D27,
              board.D22, board.D23, board.D24]
    for i in range(0, len(LEDpin)):
        led = io.DigitalInOut(LEDpin[i])
        led.direction = io.Direction.OUTPUT 
        LEDs.append(led)    
    cap.reset()
    i2c.scan() # this is needed
    # Initialise Pygame system
    pygame.mixer.quit()
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.set_num_channels(20)
    pygame.init()
    pygame.display.set_caption(
        "Hex-A-Pad -> Sample Sequencer")
    os.environ['SDL_VIDEO_WINDOW_POS'] = 'center'
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([pygame.KEYDOWN,
                pygame.QUIT, pygame.MOUSEBUTTONDOWN,
                              pygame.MOUSEBUTTONUP])
    sWide = 430 ; sHigh = 520
    padCo = (sWide//2 - 100, 48) # top of screen
    screen = pygame.display.set_mode([sWide,
                                      sHigh], 0, 32)
    # Load graphics
    pad = pygame.image.load(
        "images/pad.png").convert_alpha()
    backCol = (160, 160, 160) ; black = (0, 0, 0)
    ccol = [ black, (255, 0, 70), (0, 255, 0),
             (255, 222, 0) ]
    x = [38, 69, 129, 161, 131, 68, 62, 136]
    y = [110, 58, 56, 109, 163, 163, 78, 77]
    dLED = []
    for i in range(0, 8):
        dLED.append( (x[i] + padCo[0],
                      y[i] + padCo[1]))
    sLED = [] ; s = math.radians(22.5)
    for i in range(0, 16):
        sLED.append((int(138 * math.cos(i * s) +
                         (sWide // 2)),
                     int(138 * math.sin(i * s) +
                         padCo[1] + 113)))
    choiceRect = [pygame.Rect((0, 0), (15, 15))] * 7
    for i in range(0,5) :
        ost = 0
        if i > 1 : ost = 30
        choiceRect[i] = pygame.Rect((155,
                        ost + 344 + i * 30), (15, 15))
    choiceRect[5] = pygame.Rect((355, 344), (15, 15))
    choiceRect[6] = pygame.Rect((355, 374), (15, 15))  
    incRect = [pygame.Rect((240, 402), (15, 15))] * 4
    incRect[1] = pygame.Rect((260, 402), (15, 15))
    incRect[2] = pygame.Rect((353, 402), (15, 15))
    incRect[3] = pygame.Rect((373, 402), (15, 15))
    no = pygame.image.load(
        "images/0.png").convert_alpha()
    yes = pygame.image.load(
        "images/1.png").convert_alpha()
    plus = pygame.image.load(
        "images/plus.png").convert_alpha()
    minus = pygame.image.load(
        "images/minus.png").convert_alpha()
    choices = [False] * 7 ;
    presetC = [5, 2, 6] # power up choices
    for i in range(0,len(presetC)) :
        choices[presetC[i]] = True           
    # Load Sounds three banks
    soundNames1 = ["tabla_ghe4", "bass_voxy_hit_c",
            "drum_splash_hard", "drum_tom_hi_hard",
            "drum_tom_lo_hard", "drum_snare_hard",
            "bass_voxy_c", "loop_amen_full"]
    sounds1 = [ pygame.mixer.Sound("sounds/"+
               soundNames1[i]+".wav")
               for i in range(0, len(soundNames1))]
    soundNames2 = ["Sax_a", "Sax_c", "Sax_d", "Sax_e",
                "Sax_g", "Sax_a2", "Sax_c2", "Sax_d2" ]
    sounds2 = [ pygame.mixer.Sound("sounds/"+
               soundNames2[i]+".wav")
               for i in range(0, len(soundNames2)) ]
    soundNames3 = ["K_a", "K_c", "K_d", "K_e",
                   "K_g", "K_a2", "K_c2", "K_d2" ]
    sounds3 = [ pygame.mixer.Sound("sounds/"+
               soundNames3[i]+".wav")
               for i in range(0, len(soundNames3))]
    sounds = [ sounds1, sounds2, sounds3]
    font = pygame.font.Font(None, 24)
    playing = [pygame.mixer.Channel(0)]*8
    contPlay = [False, False] ; playback = False
    recording = False ; nextStep = time.time()
    stepCount = -1 ; savePos = 0 ; bank = 0
    seqNotes = [] ; recordedBank = 0 ; stopping = False
    for i in range(0, 16) :
        seqNotes.append([-1, -1, -1, -1, -1, -1])
    bpm = 200 ; stepTime = 1 / (bpm / 60)

def wipeSequence() :
    global seqNotes, recordedBank
    for i in range(0, 16) :
        for j in range(0, 6) :
            seqNotes[i][j] = -1
    recordedBank = bank        
            
def controlLEDs(led, col) :
    pygame.draw.circle(screen, ccol[col],
                       dLED[led + 6], 4, 0)
    pygame.display.update()
    mask = 0x30
    if led == 1 : mask = mask <<  2
    i2c.writeto(0x5A, bytes([0x79, mask])) # LEDs off
    if col == 1 : mask = 0x20
    if col == 2 : mask = 0x10
    if col == 3 : mask = 0x30
    if led == 1 : mask = mask <<  2
    if col != 0 :
        i2c.writeto(0x5A, bytes([0x78, mask])) 
    
def checkPlaying(): # so we can turn off the lEDs
    global contPlay
    for i in range(0,6) :
        if (not playing[i].get_busy()) and LEDs[i].value :
            LEDs[i].value = False
            updateTrigger(i, False)
    if (not playing[6].get_busy()) and contPlay[0] :
        contPlay[0] = False
        controlLEDs(0, 0) # LED off
        updateTrigger(6, False)
    if (not playing[7].get_busy()) and contPlay[1] :
        contPlay[1] = False
        controlLEDs(1, 0) # LED off
        updateTrigger(7, False)
                                    
def setMPR121(): # top 4 sensor inputs to GPIOs
    # turn off cap sense
    i2c.writeto(0x5A, bytes([0x5e, 0]))
    #gpio enable top 4 bits
    i2c.writeto(0x5A, bytes([0x77, 0xf0]))
    # control 0 control 1 direction
    i2c.writeto(0x5A, bytes([0x73, 0xf0]))
    i2c.writeto(0x5A, bytes([0x74, 0xf0]))
    i2c.writeto(0x5A, bytes([0x76, 0xf0]))
    # limit sensor to first 8
    i2c.writeto(0x5A, bytes([0x5e, 8])) 

def handleMouse(pos): # look at mouse down
    global choices
    #print(pos)
    for i in range(0,len(choices)) :
        if choiceRect[i].collidepoint(pos) and not choices[i]:
            pygame.draw.rect(screen, (192, 192, 0),
                             choiceRect[i], 0)
            pygame.display.update()
            if i == 6 or i == 7 : wipeSequence()
    for i in range(0,len(incRect)) :
        if incRect[i].collidepoint(pos) :
            pygame.draw.rect(screen, (192, 0, 192),
                             incRect[i], 0)
            pygame.display.update()

def handleMouseUp(pos): # look at mouse up
    global choices, bank
    for i in range(0,len(choices)) :
        if choiceRect[i].collidepoint(pos) :
            if not choices[i]:
                doRadioButton(i)
                choices[i] = True
    for i in range(0,len(incRect)) :
        if incRect[i].collidepoint(pos) :
            updateBPM(i)
    j = 0
    for i in range(2, 5) :
        if choices[i] : bank = j
        j += 1    
    updateChoices()        

def updateBPM(i) :
    global bpm, stepTime
    if i == 0 : bpm += 1
    if i == 1 : bpm -= 1
    if i == 2 : bpm += 10
    if i == 3 : bpm -= 10
    bpm = constrain(bpm, 30, 500)
    stepTime = 1 / (bpm / 60)

def constrain(val, min_val, max_val) :
    return min(max_val, max(min_val, val))
    
def doRadioButton(i) :
    group = [ [0, 5], [1, 6], [2, 3, 4] ]
    for k in range(0,len(group) ) :
        if i in group[k] :
            for j in range(0,len(group[k])) :
                choices[group[k][j]] = False
    if i == 0:
        controlLEDs(0, 0) # sequence LEDs off
        controlLEDs(1, 0) 
    if i == 5 :
        controlLEDs(0, 2) # sequence LEDs green
        controlLEDs(1, 2) 

def terminate(): # close down the program
    pygame.quit() # close pygame
    os._exit(1)
   
def checkForEvent(): # see if we need to quit
    event = pygame.event.poll()
    if event.type == pygame.QUIT :
         terminate()
    if event.type == pygame.KEYDOWN :
       if event.key == pygame.K_ESCAPE :
          terminate()
    if event.type == pygame.MOUSEBUTTONDOWN :
        handleMouse(pygame.mouse.get_pos())        
    if event.type == pygame.MOUSEBUTTONUP :
        handleMouseUp(pygame.mouse.get_pos())                  
            
if __name__ == '__main__':
    main()

