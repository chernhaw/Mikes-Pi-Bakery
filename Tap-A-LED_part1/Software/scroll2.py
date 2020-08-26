#!/usr/bin/env python3
# Scroll 2 text allows setting the colour of each letter
# by Mike Cook August 2020

import board
import neopixel
import time

backCol = (0, 0, 0)  # colour for background
letterCol =  [ (128, 0, 0), (0, 128, 0), (128, 128, 0), (0, 64, 128),
               (0, 0, 128) ] # extend to as many colours as you want

def main():
    init()
    displayText("Tap-A-LED by Mike Cook ") # change to what you want to show, end with a space

def displayText(text):
    print("Displaying:-", text)
    dotBuffer = [(0, 0, 0)] * len(text) * 64
    lCol = -1
    for y in range(8): # do a row for each of the 8 rows of the font
        lCol = -1 # comment out and see what happens
        for i in range(0,len(text)): # step through each letter
            t = text[i: i+1:]
            fontPlace = ord(t) - 0x20
            fontEntry = fontPlace
            bitPattern = FONT8x8[fontEntry]
            bits = bitPattern[7-y]
            lCol += 1
            if lCol >= len(letterCol) : lCol = 0
            for x in range(8):
                mask = 1 << (7-x)
                if bits & mask !=0 :
                    dotBuffer[(x * 8) + (y) + (i * 64)] = letterCol[lCol]
                else :
                    dotBuffer[(x * 8) + (y) + (i * 64)] = backCol
    # now display the text
    xPoint = 0   
    xLimit = len(text) * 64      
    while 1 :  # do until ctrl C
        for y in range(8):
            for x in range(16):
                if xPoint + (x * 8) >= xLimit :
                    pixels[(x * 8) + y] = dotBuffer[xPoint - xLimit + (x * 8) + y]
                else :        
                    pixels[(x * 8) + y] = dotBuffer[xPoint + (x * 8) + y]
        pixels.show()
        time.sleep(0.1)
        xPoint += 8
        if xPoint >= xLimit : xPoint = 0
    
def init():
    global pixels, FONT8x8
    size = 8, 16 # size of LED display
    pointer = 0
    pixel_pin = board.D18
    num_pixels = 128
    # RGB or GRB. Some NeoPixels have red and green reversed
    ORDER = neopixel.GRB
    BRIGHTNESS = 0.2 # 0.6 is maximum brightness for 3A external supply
    pixels = neopixel.NeoPixel(pixel_pin, num_pixels,
             brightness = BRIGHTNESS, auto_write = False,
             pixel_order = ORDER)
    pixels.fill((0, 0, 0))
    # defint an 8 by 8 font
    FONT8x8 = [
    #  columns, rows, num_bytes_per_char
    (0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00), #  space 0x20
    (0x30,0x78,0x78,0x30,0x30,0x00,0x30,0x00), #  !
    (0x6C,0x6C,0x6C,0x00,0x00,0x00,0x00,0x00), #  "
    (0x6C,0x6C,0xFE,0x6C,0xFE,0x6C,0x6C,0x00), #  #
    (0x18,0x3E,0x60,0x3C,0x06,0x7C,0x18,0x00), #  $
    (0x00,0x63,0x66,0x0C,0x18,0x33,0x63,0x00), #  %
    (0x1C,0x36,0x1C,0x3B,0x6E,0x66,0x3B,0x00), #  &
    (0x30,0x30,0x60,0x00,0x00,0x00,0x00,0x00), #  '
    (0x0C,0x18,0x30,0x30,0x30,0x18,0x0C,0x00), #  (
    (0x30,0x18,0x0C,0x0C,0x0C,0x18,0x30,0x00), #  )
    (0x00,0x66,0x3C,0xFF,0x3C,0x66,0x00,0x00), #  *
    (0x00,0x30,0x30,0xFC,0x30,0x30,0x00,0x00), #  +
    (0x00,0x00,0x00,0x00,0x00,0x18,0x18,0x30), #  ,
    (0x00,0x00,0x00,0x7E,0x00,0x00,0x00,0x00), #  -
    (0x00,0x00,0x00,0x00,0x00,0x18,0x18,0x00), #  .
    (0x03,0x06,0x0C,0x18,0x30,0x60,0x40,0x00), #  / (forward slash)
    (0x3E,0x63,0x63,0x6B,0x63,0x63,0x3E,0x00), #  0 0x30
    (0x18,0x38,0x58,0x18,0x18,0x18,0x7E,0x00), #  1
    (0x3C,0x66,0x06,0x1C,0x30,0x66,0x7E,0x00), #  2
    (0x3C,0x66,0x06,0x1C,0x06,0x66,0x3C,0x00), #  3
    (0x0E,0x1E,0x36,0x66,0x7F,0x06,0x0F,0x00), #  4
    (0x7E,0x60,0x7C,0x06,0x06,0x66,0x3C,0x00), #  5
    (0x1C,0x30,0x60,0x7C,0x66,0x66,0x3C,0x00), #  6
    (0x7E,0x66,0x06,0x0C,0x18,0x18,0x18,0x00), #  7
    (0x3C,0x66,0x66,0x3C,0x66,0x66,0x3C,0x00), #  8
    (0x3C,0x66,0x66,0x3E,0x06,0x0C,0x38,0x00), #  9
    (0x00,0x18,0x18,0x00,0x00,0x18,0x18,0x00), #  :
    (0x00,0x18,0x18,0x00,0x00,0x18,0x18,0x30), #  ;
    (0x0C,0x18,0x30,0x60,0x30,0x18,0x0C,0x00), #  <
    (0x00,0x00,0x7E,0x00,0x00,0x7E,0x00,0x00), #  =
    (0x30,0x18,0x0C,0x06,0x0C,0x18,0x30,0x00), #  >
    (0x3C,0x66,0x06,0x0C,0x18,0x00,0x18,0x00), #  ?
    (0x3E,0x63,0x6F,0x69,0x6F,0x60,0x3E,0x00), #  @ 0x40
    (0x18,0x3C,0x66,0x66,0x7E,0x66,0x66,0x00), #  A
    (0x7E,0x33,0x33,0x3E,0x33,0x33,0x7E,0x00), #  B
    (0x1E,0x33,0x60,0x60,0x60,0x33,0x1E,0x00), #  C
    (0x7C,0x36,0x33,0x33,0x33,0x36,0x7C,0x00), #  D
    (0x7F,0x31,0x34,0x3C,0x34,0x31,0x7F,0x00), #  E
    (0x7F,0x31,0x34,0x3C,0x34,0x30,0x78,0x00), #  F
    (0x1E,0x33,0x60,0x60,0x67,0x33,0x1F,0x00), #  G
    (0x66,0x66,0x66,0x7E,0x66,0x66,0x66,0x00), #  H
    (0x3C,0x18,0x18,0x18,0x18,0x18,0x3C,0x00), #  I
    (0x0F,0x06,0x06,0x06,0x66,0x66,0x3C,0x00), #  J
    (0x73,0x33,0x36,0x3C,0x36,0x33,0x73,0x00), #  K
    (0x78,0x30,0x30,0x30,0x31,0x33,0x7F,0x00), #  L
    (0x63,0x77,0x7F,0x7F,0x6B,0x63,0x63,0x00), #  M
    (0x63,0x73,0x7B,0x6F,0x67,0x63,0x63,0x00), #  N
    (0x3E,0x63,0x63,0x63,0x63,0x63,0x3E,0x00), #  O
    (0x7E,0x33,0x33,0x3E,0x30,0x30,0x78,0x00), #  P 0x50
    (0x3C,0x66,0x66,0x66,0x6E,0x3C,0x0E,0x00), #  Q
    (0x7E,0x33,0x33,0x3E,0x36,0x33,0x73,0x00), #  R
    (0x3C,0x66,0x30,0x18,0x0C,0x66,0x3C,0x00), #  S
    (0x7E,0x5A,0x18,0x18,0x18,0x18,0x3C,0x00), #  T
    (0x66,0x66,0x66,0x66,0x66,0x66,0x7E,0x00), #  U
    (0x66,0x66,0x66,0x66,0x66,0x3C,0x18,0x00), #  V
    (0x63,0x63,0x63,0x6B,0x7F,0x77,0x63,0x00), #  W
    (0x63,0x63,0x36,0x1C,0x1C,0x36,0x63,0x00), #  X
    (0x66,0x66,0x66,0x3C,0x18,0x18,0x3C,0x00), #  Y
    (0x7F,0x63,0x46,0x0C,0x19,0x33,0x7F,0x00), #  Z
    (0x3C,0x30,0x30,0x30,0x30,0x30,0x3C,0x00), #  [
    (0x60,0x30,0x18,0x0C,0x06,0x03,0x01,0x00), #  \ (back slash)
    (0x3C,0x0C,0x0C,0x0C,0x0C,0x0C,0x3C,0x00), #  ]
    (0x08,0x1C,0x36,0x63,0x00,0x00,0x00,0x00), #  ^
    (0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xFF), #  _
    (0x18,0x18,0x0C,0x00,0x00,0x00,0x00,0x00), #  ` 0x60
    (0x00,0x00,0x3C,0x06,0x3E,0x66,0x3B,0x00), #  a
    (0x70,0x30,0x3E,0x33,0x33,0x33,0x6E,0x00), #  b
    (0x00,0x00,0x3C,0x66,0x60,0x66,0x3C,0x00), #  c
    (0x0E,0x06,0x3E,0x66,0x66,0x66,0x3B,0x00), #  d
    (0x00,0x00,0x3C,0x66,0x7E,0x60,0x3C,0x00), #  e
    (0x1C,0x36,0x30,0x78,0x30,0x30,0x78,0x00), #  f
    (0x00,0x00,0x3B,0x66,0x66,0x3E,0x06,0x7C), #  g
    (0x70,0x30,0x36,0x3B,0x33,0x33,0x73,0x00), #  h
    (0x18,0x00,0x38,0x18,0x18,0x18,0x3C,0x00), #  i
    (0x06,0x00,0x06,0x06,0x06,0x66,0x66,0x3C), #  j
    (0x70,0x30,0x33,0x36,0x3C,0x36,0x73,0x00), #  k
    (0x38,0x18,0x18,0x18,0x18,0x18,0x3C,0x00), #  l
    (0x00,0x00,0x66,0x7F,0x7F,0x6B,0x63,0x00), #  m
    (0x00,0x00,0x7C,0x66,0x66,0x66,0x66,0x00), #  n
    (0x00,0x00,0x3C,0x66,0x66,0x66,0x3C,0x00), #  o
    (0x00,0x00,0x6E,0x33,0x33,0x3E,0x30,0x78), #  p 0x70
    (0x00,0x00,0x3B,0x66,0x66,0x3E,0x06,0x0F), #  q
    (0x00,0x00,0x6E,0x3B,0x33,0x30,0x78,0x00), #  r
    (0x00,0x00,0x3E,0x60,0x3C,0x06,0x7C,0x00), #  s
    (0x08,0x18,0x3E,0x18,0x18,0x1A,0x0C,0x00), #  t
    (0x00,0x00,0x66,0x66,0x66,0x66,0x3B,0x00), #  u
    (0x00,0x00,0x66,0x66,0x66,0x3C,0x18,0x00), #  v
    (0x00,0x00,0x63,0x6B,0x7F,0x7F,0x36,0x00), #  w
    (0x00,0x00,0x63,0x36,0x1C,0x36,0x63,0x00), #  x
    (0x00,0x00,0x66,0x66,0x66,0x3E,0x06,0x7C), #  y
    (0x00,0x00,0x7E,0x4C,0x18,0x32,0x7E,0x00), #  z
    (0x0E,0x18,0x18,0x70,0x18,0x18,0x0E,0x00), #  (
    (0x0C,0x0C,0x0C,0x00,0x0C,0x0C,0x0C,0x00), #  |
    (0x70,0x18,0x18,0x0E,0x18,0x18,0x70,0x00), #  ), 
    (0x3B,0x6E,0x00,0x00,0x00,0x00,0x00,0x00), #  ~
    (0x1C,0x36,0x36,0x1C,0x00,0x00,0x00,0x00) ] # DEL    

    
if __name__ == '__main__':
    main()
