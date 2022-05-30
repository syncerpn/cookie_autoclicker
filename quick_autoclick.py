# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 20:32:06 2022

@author: nghia_sv
"""

from pynput import mouse, keyboard
import time
    
mc = mouse.Controller()
kc = keyboard.Controller()

def on_press(key):
    if key == keyboard.Key.ctrl_l:
        mc.click(mouse.Button.left, 1) #choose it
        time.sleep(0.001)

def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener
        return False

# Collect events until released
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

# ...or, in a non-blocking fashion:
# listener = keyboard.Listener(on_press=on_press, on_release=on_release)
# listener.start()