# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 20:32:06 2022

@author: nghia_sv
"""
from pynput import mouse, keyboard
import time
    
mc = mouse.Controller()
kc = keyboard.Controller()

time.sleep(1)
for t in range(5000):
    mc.click(mouse.Button.left, 1) #choose it
    time.sleep(0.001)
    