# -*- coding: utf-8 -*-
"""
Created on Mon May 30 18:31:50 2022

@author: Nghia
"""

from pynput import mouse, keyboard
import time
from PIL import Image
import numpy as np
import pyautogui
# from threading import Thread, Lock
from multiprocessing import Process, Manager, Lock

mutex = Lock()
mc = mouse.Controller()
kc = keyboard.Controller()

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
GOLDEN_COOKIE_LOOKING_PERIOD = 0.1

def periodic_observe_and_react(period, flags,
                               callback_observe, args_observe, flag_observe,
                               callback_react, args_react, flag_react,
                               flag_destroy):
    time_prev = time.time()
    while not flags[flag_destroy]:
        time_curr = time.time()
        if time_curr - time_prev >= period:
            t = time.time()
            if flags[flag_observe]:
                return_data = callback_observe(*args_observe)
                
            if flags[flag_react]:
                callback_react(return_data, *args_react)
                
            print('took %.3f' % (time.time() - t))
            time_prev = time_curr

def detect_golden_cookie(pattern, half_window=True):
    #gonna return list of center points of candidates
    query = np.array(pyautogui.screenshot(), dtype=np.int32)
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

def click_cookie(candidates, wait=1):
    mutex.acquire()
    for candidate in candidates:
        gcy, gcx = candidate
        mc.position = (gcx, gcy)
        time.sleep(wait)
        mc.click(mouse.Button.left, 1)
        time.sleep(wait)
    
    mutex.release()
    
    
def on_press(key):
    global flags
    
    if key == keyboard.Key.f1:
        flags['auto'] = not flags['auto']
        flags['detect_golden_cookie'] = flags['auto'] and flags['detect_golden_cookie']
        flags['detect_wrath_cookie'] = flags['auto'] and flags['detect_wrath_cookie']
        
        print('[INFO] auto-click %s' % ('on' if flags['auto'] else 'off'))
        print('[INFO] golden cookie detection %s' % ('on' if flags['detect_golden_cookie'] else 'off'))
        print('[INFO] wrath cookie detection %s' % ('on' if flags['detect_wrath_cookie'] else 'off'))
    
    elif key == keyboard.Key.f2 and flags['auto']:
        flags['detect_golden_cookie'] = not flags['detect_golden_cookie']
        print('[INFO] golden cookie detection %s' % ('on' if flags['detect_golden_cookie'] else 'off'))
        
    elif key == keyboard.Key.f3 and flags['auto']:
        flags['detect_wrath_cookie'] = not flags['detect_wrath_cookie']
        print('[INFO] wrath cookie detection %s' % ('on' if flags['detect_wrath_cookie'] else 'off'))

def on_release(key):
    global flags
    if key == keyboard.Key.esc and not flags['auto']:
        # Stop listener
        print('[INFO] exit')
        flags['quit'] = True
        return False

if __name__ == '__main__':

    with Manager() as manager:

        flags = manager.dict({
            'auto': False,
            'quit': False,
            'detect_golden_cookie': True,
            'detect_wrath_cookie': True,
            })
        
        candidates_golden_cookie = None
        candidates_wrath_cookie = None
            
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            thread_detect_golden_cookie = Process(target=periodic_observe_and_react,
                                                  args=(GOLDEN_COOKIE_LOOKING_PERIOD, flags,
                                                        detect_golden_cookie, (PATTERN,), 'detect_golden_cookie',
                                                        click_cookie, (WAIT,), 'detect_golden_cookie',
                                                        'quit'))
            
            thread_detect_wrath_cookie = Process(target=periodic_observe_and_react,
                                                  args=(GOLDEN_COOKIE_LOOKING_PERIOD, flags,
                                                        detect_golden_cookie, (PATTERN_2,), 'detect_wrath_cookie',
                                                        click_cookie, (WAIT,), 'detect_wrath_cookie',
                                                        'quit'))
            
            thread_detect_golden_cookie.start()
            thread_detect_wrath_cookie.start()
            
            while(not flags['quit']):
                if flags['auto']:
                    mutex.acquire()
                    mc.position = (BIG_COOKIE_X, BIG_COOKIE_Y)
                    time.sleep(WAIT)
                    mc.click(mouse.Button.left, 1)
                    time.sleep(WAIT)
                    mutex.release()
            
            thread_detect_golden_cookie.join()
            thread_detect_wrath_cookie.join()
            listener.join()