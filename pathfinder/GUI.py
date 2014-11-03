#!/usr/bin/env python
# encoding: utf-8

__author__ = 'Daniel'

"""
Simple Graphic User Interface (GUI) for Pathfinder SDNapp
"""

from PIL import ImageFile, Image

import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
import sys

# ## Globals (state)
message = "GUI Test"
store = 0
inData = 0
#im = Image.open("/home/i2cat/Documents/test.png", mode='r')
#im = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/gutenberg.jpg")
im = simplegui.load_image("/home/i2cat/Documents/test.png")
### Helper functions


### Classes


### Define event handlers
# Handler for mouse click
def click(pos=None):
    global message
    global mag_pos
    message = "Click"
    if pos:
        mag_pos = list(pos)

# Handler to draw on canvas
def draw(canvas):
    canvas.draw_image(im, [IMA_WIDTH // 2, IMA_HEIGHT // 2], [IMA_WIDTH, IMA_HEIGHT], [CAN_WIDTH // 2, CAN_HEIGHT // 2], [CAN_WIDTH, CAN_HEIGHT])
    ima_center = [SCALE * mag_pos[0], SCALE * mag_pos[1]]
    ima_rectangle = [MAG_SIZE, MAG_SIZE]
    mag_center = mag_pos
    mag_rectangle = [MAG_SIZE, MAG_SIZE]
    canvas.draw_image(im, ima_center, ima_rectangle, mag_center, mag_rectangle)

    if inData:
        canvas.draw_text(str(inData), [50, 223], 48, "Green")


def tick():
    print "QoS SDNapp"


def output():
    '''print content of store and operand'''
    print "Store = ", store
    print "Input = ", inData
    print " "


def swap():
    '''swap contents of store and operand'''
    global store, inData
    store, inData = inData, store
    output()


def enter(t):
    '''input for a new data'''
    global inData
    inData = int(t)
    output()


def exit():
    '''Closes GUI window'''
    sys.exit()

# Image, canvas, magnifier sizes
IMA_WIDTH = 800
IMA_HEIGHT = 600

SCALE = 3

CAN_WIDTH = IMA_WIDTH // SCALE
CAN_HEIGHT = IMA_HEIGHT // SCALE

MAG_SIZE = 120
mag_pos = [CAN_WIDTH // 2, CAN_HEIGHT // 2]


# create frame
f = simplegui.create_frame("SDNapp: Pathfinder GUI", CAN_WIDTH, CAN_HEIGHT)

#im.save("/home/i2cat/Documents/test4534.png")


# register event handlers
#f.add_button("Print", output, 100)
#f.add_button("Swap",swap, 100)
#f.add_button("Add", add, 100)
#f.add_button("Sub", sub, 100)
#f.add_button("Mult", mult, 100)
#f.add_button("Div", div, 100)
f.add_button("Send request", tick, 100)
f.add_button("Change stats", tick, 100)
f.add_button("Get path", click, 100)
f.add_button("Exit", exit, 100)
f.add_input("Enter", enter, 100)


# Main
f.set_mouseclick_handler(click)
f.set_draw_handler(draw)
f.start()

"""
# Some practice on python GUIs
def add():
    '''add operand to store'''
    global store
    store = store + operand
    output()

def sub():
    '''substract om store'''
    global store
    store = store - operand
    output()

def mult():
    '''multipiply store by operand'''
    global store
    store = store * operand
    output()

def div():
    '''divide store by operand'''
    global store
    if operand > 0:
        store = store / operand
        output()


# Main
timer = simplegui.create_timer(1000, tick)
frame = simplegui.create_frame("Frame", 500, 500, 200)
frame.add_button("Send", click)
frame.add_button("View", click)
frame.set_draw_handler(draw)

frame.start()
timer.start()
"""