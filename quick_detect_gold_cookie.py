# -*- coding: utf-8 -*-
"""
Created on Sun May 29 16:41:08 2022

@author: nghia_sv
"""

from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import pyautogui

H = 96
W = 96

AY = 832
AX = 354

PSXS = list(range(30,51,20))
PSYS = list(range(30,51,20))

THRESHOLD_MATCHING = 5

pattern_mask = np.array(Image.open('wrathCookie.png').convert('RGBA'), dtype=np.int32)
mask = pattern_mask[:,:,3:] > 0
pattern = pattern_mask[:,:,:3] * mask

query = np.array(Image.open('Untitled2.png'), dtype=np.int32)
# query = np.array(pyautogui.screenshot(), dtype=np.int32)
candidates = None

for psx in PSXS:
    for psy in PSYS:
        pattern_sample = pattern[psy, psx, :]
        diff = (abs(query - pattern_sample)).mean(axis=2)
        ys, xs = np.where(diff < THRESHOLD_MATCHING)
        yxs = set([(y-psy,x-psx) for y,x in zip(ys,xs) if y >= psy and x >= psx])
        
        if candidates is None:
            candidates = yxs
        else:
            candidates = candidates.intersection(yxs)
            print(psy, psx)
            print(candidates)

for candidate in candidates:
    plt.subplots()
    y, x = candidate
    plt.imshow(query[y:y+H, x:x+W, :])