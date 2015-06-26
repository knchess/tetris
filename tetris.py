#!/usr/bin/env python3

"""

Tetris clone written in Python 3 using PyGame

Controls:
Z: rotate left / counter-clockwise
X/Up: rotate right / clockwise
Left: move left
Right: move right
Down: move down / soft drop
Space: hard drop
P: pause / unpause

This clone aims to replicate the Tetris Guideline including Random Generator and Super Rotation System (SRS)
http://tetris.wikia.com/wiki/Tetris_Guideline

Currently missing features:
    -levels/increasing gravity
    -scoring
    -ghost piece
    -wallkick/floorkick
    -next piece prediction
    -hold piece

"""

from app import App

if __name__ == '__main__':
    app = App()
    app.run()
