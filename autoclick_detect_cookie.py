# -*- coding: utf-8 -*-
"""
Created on Mon May 30 02:37:49 2022

@author: nghia_sv
"""

from pynput import mouse, keyboard
import time
from PIL import Image
import numpy as np
import pyautogui

def detect_golden_cookie(query, pattern, half_window=True):
    #gonna return list of center points of candidates
    query = np.array(query, dtype=np.int32)
    if half_window:
        query = query[:,:query.shape[1]//2,:]
    candidates = None
    
    for psx in PSXS:
        for psy in PSYS:
            pattern_sample = pattern[psy, psx, :]
            diff = (abs(query - pattern_sample)).mean(axis=2)
            ys, xs = np.where(diff <= THRESHOLD_MATCHING)
            yxs = set([(y-psy+PH//2, x-psx+PW//2) for y,x in zip(ys,xs) if y >= psy and x >= psx])
            
            if candidates is None:
                candidates = yxs
            else:
                candidates = candidates.intersection(yxs)
            
            #quit as soon as there is no candidate after the first try
            if not candidates:
                break
    return candidates
    
if __name__ == '__main__':
    PH = 96
    PW = 96
        
    PSXS = list(range(30,51,20))
    PSYS = list(range(30,51,20))
    
    BIG_COOKIE_Y = 430
    BIG_COOKIE_X = 144
    
    THRESHOLD_MATCHING = 5
    
    PATTERN_MASK = np.array(Image.open('data/goldCookie.png').convert('RGBA'), dtype=np.int32)
    MASK = PATTERN_MASK[:,:,3:] > 0
    PATTERN = PATTERN_MASK[:,:,:3] * MASK
    
    PATTERN_MASK_2 = np.array(Image.open('data/wrathCookie.png').convert('RGBA'), dtype=np.int32)
    MASK_2 = PATTERN_MASK_2[:,:,3:] > 0
    PATTERN_2 = PATTERN_MASK_2[:,:,:3] * MASK_2
    
    WAIT = 0.0001
    MAX_LOOKING_PERIOD = 3
    
    mc = mouse.Controller()
    kc = keyboard.Controller()
    
    flag_auto = False
    flag_quit = False
    flag_detect_golden_cookie = True
    flag_detect_wrath_cookie = True
    flag_fix_mouse_pos_big_cookie = True
    
    def on_press(key):
        global flag_auto
        global flag_quit
        global flag_detect_golden_cookie
        global flag_detect_wrath_cookie
        global flag_fix_mouse_pos_big_cookie
        
        if key == keyboard.Key.f1:
            flag_auto = not flag_auto
            flag_detect_golden_cookie = flag_auto and flag_detect_golden_cookie
            flag_detect_wrath_cookie = flag_auto and flag_detect_wrath_cookie
            flag_fix_mouse_pos_big_cookie = flag_auto
            
            print('[INFO] auto-click %s' % ('on' if flag_auto else 'off'))
            print('[INFO] golden cookie detection %s' % ('on' if flag_detect_golden_cookie else 'off'))
            print('[INFO] wrath cookie detection %s' % ('on' if flag_detect_wrath_cookie else 'off'))
            print('[INFO] fix mouse position %s' % ('on' if flag_fix_mouse_pos_big_cookie else 'off'))
        
        elif key == keyboard.Key.f2 and flag_auto:
            flag_detect_golden_cookie = not flag_detect_golden_cookie
            print('[INFO] golden cookie detection %s' % ('on' if flag_detect_golden_cookie else 'off'))
            
        elif key == keyboard.Key.f3 and flag_auto:
            flag_detect_wrath_cookie = not flag_detect_wrath_cookie
            print('[INFO] wrath cookie detection %s' % ('on' if flag_detect_wrath_cookie else 'off'))
            
        elif key == keyboard.Key.f4 and flag_auto:
            flag_fix_mouse_pos_big_cookie = not flag_fix_mouse_pos_big_cookie
            print('[INFO] fix mouse position %s' % ('on' if flag_fix_mouse_pos_big_cookie else 'off'))
    
    def on_release(key):
        global flag_auto
        global flag_quit
        if key == keyboard.Key.esc and not flag_auto:
            # Stop listener
            print('[INFO] exit')
            flag_quit = True
            return False
    
    # Collect events until released
    time_prev_golden = time.time()
    time_prev_wrath = time.time()
    speed_divider_golden_cookie = 1
    speed_divider_wrath_cookie = 1
    
    looking_golden_cookie = 1
    looking_wrath_cookie = 1
    
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        while not flag_quit:
            if flag_auto:
                time_curr = time.time()
                candidates = None
                
                if flag_detect_golden_cookie:
                    if time_curr - time_prev_golden >= looking_golden_cookie:
                        time_prev_golden = time_curr
                        query = pyautogui.screenshot()
                        candidates = detect_golden_cookie(query, PATTERN)
                    
                    if candidates:
                        looking_golden_cookie = 1.0 / len(candidates)
                        print('[INFO] golden found %d' % len(candidates))
                        for candidate in candidates:
                            gcy, gcx = candidate
                            mc.position = (gcx, gcy)
                            time.sleep(WAIT)
                            mc.click(mouse.Button.left, 1)
                            time.sleep(WAIT)
                    else:
                        looking_golden_cookie = min(looking_golden_cookie + 0.4, MAX_LOOKING_PERIOD)
                          
                time_curr = time.time()
                candidates = None
                
                if flag_detect_wrath_cookie:
                    if time_curr - time_prev_wrath >= looking_wrath_cookie:
                        time_prev_wrath = time_curr
                        query = pyautogui.screenshot()
                        candidates = detect_golden_cookie(query, PATTERN_2)
                    
                    if candidates:
                        looking_wrath_cookie = 1.0 / len(candidates)
                        print('[INFO] wrath found %d' % len(candidates))
                        for candidate in candidates:
                            gcy, gcx = candidate
                            mc.position = (gcx, gcy)
                            time.sleep(WAIT)
                            mc.click(mouse.Button.left, 1)
                            time.sleep(WAIT)
                    else:
                        looking_wrath_cookie = min(looking_wrath_cookie + 0.4, MAX_LOOKING_PERIOD)
                
                if flag_fix_mouse_pos_big_cookie:
                    mc.position = (BIG_COOKIE_X, BIG_COOKIE_Y)
                    time.sleep(WAIT)
                mc.click(mouse.Button.left, 1)
                time.sleep(WAIT)
            
        listener.join()