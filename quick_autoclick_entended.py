# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 20:32:06 2022

@author: nghia_sv
"""

from pynput import mouse, keyboard
import time
    
mc = mouse.Controller()
kc = keyboard.Controller()

flag_auto = False
flag_quit = False

def on_press(key):
    global flag_auto
    global flag_quit
    if key == keyboard.Key.scroll_lock:
        flag_auto = ~flag_auto
        print('[INFO] auto-click %s' % ('on' if flag_auto else 'off'))

def on_release(key):
    global flag_auto
    global flag_quit
    if key == keyboard.Key.esc and not flag_auto:
        # Stop listener
        print('[INFO] exit')
        flag_quit = True
        return False

# Collect events until released
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    while(not flag_quit):
        if flag_auto:
            mc.click(mouse.Button.left, 1) #choose it
            time.sleep(0.001)
    listener.join()
        

# ...or, in a non-blocking fashion:
# listener = keyboard.Listener(on_press=on_press, on_release=on_release)
# listener.start()