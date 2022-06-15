# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 11:02:34 2022

@author: nghia_sv
"""
import win32gui
import pyautogui
from pynput import mouse, keyboard
import time
from PIL import Image
import numpy as np
from multiprocessing import Process, Manager, Lock

mutex = Lock()
mc = mouse.Controller()
kc = keyboard.Controller()

GAME_WINDOW_TITLE_SUFFICES = [' - Cookie Clicker', ' - Cookie Baker', '(RGB/8#)']
THRESHOLD_MATCHING = 5
GOLDEN_COOKIE_LOOKING_PERIOD = 0.4

DICT_PATTERN = 'pattern'
DICT_ANCHORS = 'anchors'

WAIT = 1/200

def periodic_observe_and_react(period, flags, flag_destroy,
                               callback_observe, args_observe,
                               callback_react, args_react,
                               ):
    time_prev = time.time()
    while not flags[flag_destroy]:
        time_curr = time.time()
        if time_curr - time_prev >= period:
            return_data = callback_observe(*args_observe)
            callback_react(return_data, *args_react)
            time_prev = time_curr

def detect_pattern_anchors(pattern_dict, names, query_region,
                           dict_pattern=DICT_PATTERN,
                           dict_anchors=DICT_ANCHORS,
                           diff_threshold=THRESHOLD_MATCHING):
    #gonna return list of center points of candidates
    query = np.array(pyautogui.screenshot(region=query_region), dtype=np.int32)
    candidates = []
    
    for name in names:
        pattern = pattern_dict[name][dict_pattern]
        anchors = pattern_dict[name][dict_anchors]
        
        ph, pw, _ = pattern.shape
        candidates_pattern = None
        for anchor in anchors:
            psx, psy = anchor
            
            pattern_sample = pattern[psy, psx, :]
            diff = (abs(query - pattern_sample)).mean(axis=2)
            ys, xs = np.where(diff <= diff_threshold)
            yxs = set([(y-psy+ph//2, x-psx+pw//2) for y,x in zip(ys,xs) if y >= psy and x >= psx])
            
            if candidates_pattern is None:
                candidates_pattern = yxs
            else:
                candidates_pattern = candidates_pattern.intersection(yxs)
            
            #quit as soon as there is no candidate after the first try
            if not candidates_pattern:
                break
        
        if candidates_pattern:
            print('[INFO] found %d %s' % (len(candidates_pattern), name))
            candidates += list(candidates_pattern)
        
    return candidates

def click_cookie(candidates, offset_x, offset_y, wait=1):
    mutex.acquire()
    for candidate in candidates:
        gcy, gcx = candidate
        mc.position = (offset_x + gcx, offset_y + gcy)
        time.sleep(wait)
        mc.click(mouse.Button.left, 1)
        time.sleep(wait)
        print('[INFO] done clicking')
    
    mutex.release()
       
def on_press(key):
    global flags
    global to_detect_pattern_names
    
    change_list = []
    
    if key == keyboard.Key.f1:
        flags['auto'] = not flags['auto']
        flags['fixed_pos'] = flags['auto']
        while to_detect_pattern_names:
            to_detect_pattern_names.remove(to_detect_pattern_names[-1])
        
        print('[INFO] auto-click %s' % ('on' if flags['auto'] else 'off'))
        print('[INFO] fixed mouse pos %s' % ('on' if flags['fixed_pos'] else 'off'))
        print('[INFO] detect popup off')
    
    elif key == keyboard.Key.f2 and flags['auto']:
        change_list = ['golden_cookie', 'contract']
        
    elif key == keyboard.Key.f4 and flags['auto']:
        change_list = ['wrath_cookie', 'wrath_contract']
        
    elif key == keyboard.Key.f5 and flags['auto']:
        change_list = ['bunny_0', 'bunny_1', 'bunny_2', 'bunny_3']
        
    elif key == keyboard.Key.f6 and flags['auto']:
        change_list = ['wrath_bunny_0', 'wrath_bunny_1', 'wrath_bunny_2', 'wrath_bunny_3']
        
    elif key == keyboard.Key.f7 and flags['auto']:
        change_list = ['heart_0', 'heart_1', 'heart_2', 'heart_3', 'heart_4', 'heart_5', 'heart_6', 'heart_7']
        
    elif key == keyboard.Key.f8 and flags['auto']:
        change_list = ['spooky_cookie']
        
    elif key == keyboard.Key.f9 and flags['auto']:
        change_list = ['fortune_cookie']
        
    elif key == keyboard.Key.f3 and flags['auto']:
        flags['fixed_pos'] = not flags['fixed_pos']
        print('[INFO] fixed mouse pos %s' % ('on' if flags['fixed_pos'] else 'off'))
        
    if change_list:
        for item in change_list:
            if item in to_detect_pattern_names:
                to_detect_pattern_names.remove(item)
            else:
                to_detect_pattern_names.append(item)
        
        if to_detect_pattern_names:
            print('[INFO] detect popup %s' % (' | '.join(to_detect_pattern_names)))
        else:
            print('[INFO] detect popup off')

def on_release(key):
    global flags
    # if key == keyboard.Key.esc and not flags['auto']:
    if key == keyboard.Key.esc:
        # Stop listener
        print('[INFO] exit')
        flags['quit'] = True
        return False
    
def lookup_window(hwnd, position, suffices=GAME_WINDOW_TITLE_SUFFICES):
    for suffix in suffices:
        if win32gui.GetWindowText(hwnd).endswith(suffix):
            rect = win32gui.GetWindowRect(hwnd)
            x = rect[0]
            y = rect[1]
            w = rect[2] - x
            h = rect[3] - y
            
            position.append((x,y,w,h))
            # win32gui.SetForegroundWindow(hwnd)
            return

if __name__ == '__main__':
    #lookup
    print('[INFO] finding game window...')
    game_window_position_list = []
    win32gui.EnumWindows(lookup_window, (game_window_position_list))
    
    assert len(game_window_position_list) == 1, '[ERRO] cannot find appropriate game window'

    game_window_position = game_window_position_list[0]
    offset_x, offset_y = game_window_position[0], game_window_position[1]
    
    pattern_dict = {'big_cookie': {
                    'pattern': np.array(Image.open('data/big_cookie_ref.png').convert('RGB'), dtype=np.int32),
                    'anchors':[(40,40), (40,80), (80,40), (80,80)],
                    },
        
                'golden_cookie': {
                    'pattern': np.array(Image.open('data/goldCookie.png').convert('RGB'), dtype=np.int32),
                    'anchors':[(30,30), (30,50), (50,30), (50,50)],
                    },
        
                'wrath_cookie': {
                    'pattern': np.array(Image.open('data/wrathCookie.png').convert('RGB'), dtype=np.int32),
                    'anchors':[(30,30), (30,50), (50,30), (50,50)],
                    },
        
                'contract': {
                    'pattern': np.array(Image.open('data/contract.png').convert('RGB'), dtype=np.int32),
                    'anchors':[(30,30), (30,50), (50,30), (50,50)],
                    },
        
                'wrath_contract': {
                    'pattern': np.array(Image.open('data/wrathContract.png').convert('RGB'), dtype=np.int32),
                    'anchors':[(30,30), (30,50), (50,30), (50,50)],
                    },
        
                'bunny_0': {
                    'pattern': np.array(Image.open('data/bunnies.png').convert('RGB'), dtype=np.int32)[0:96,0:96,:],
                    'anchors':[(39,24), (29,35), (48,53), (33,78)],
                    },
        
                'wrath_bunny_0': {
                    'pattern': np.array(Image.open('data/bunnies.png').convert('RGB'), dtype=np.int32)[96:192,0:96,:],
                    'anchors':[(39,24), (29,35), (48,53), (33,78)],
                    },
        
                'bunny_1': {
                    'pattern': np.array(Image.open('data/bunnies.png').convert('RGB'), dtype=np.int32)[0:96,96:192,:],
                    'anchors':[(36,36), (58,41), (32,62), (55,58)],
                    },
        
                'wrath_bunny_1': {
                    'pattern': np.array(Image.open('data/bunnies.png').convert('RGB'), dtype=np.int32)[96:192,96:192,:],
                    'anchors':[(36,36), (58,41), (32,62), (55,58)],
                    },
        
                'bunny_2': {
                    'pattern': np.array(Image.open('data/bunnies.png').convert('RGB'), dtype=np.int32)[0:96,192:288,:],
                    'anchors':[(50,20), (57,27), (54,54), (36,70)],
                    },
        
                'wrath_bunny_2': {
                    'pattern': np.array(Image.open('data/bunnies.png').convert('RGB'), dtype=np.int32)[96:192,192:288,:],
                    'anchors':[(50,20), (57,27), (54,54), (36,70)],
                    },
        
                'bunny_3': {
                    'pattern': np.array(Image.open('data/bunnies.png').convert('RGB'), dtype=np.int32)[0:96,288:384,:],
                    'anchors':[(24,35), (43,30), (49,53), (69,57)],
                    },
        
                'wrath_bunny_3': {
                    'pattern': np.array(Image.open('data/bunnies.png').convert('RGB'), dtype=np.int32)[96:192,288:384,:],
                    'anchors':[(24,35), (43,30), (49,53), (69,57)],
                    },
        
                'heart_0': {
                    'pattern': np.array(Image.open('data/hearts.png').convert('RGB'), dtype=np.int32)[0:96,0:96,:],
                    'anchors':[(30,30), (30,60), (60,30), (60,60)],
                    },
        
                'heart_1': {
                    'pattern': np.array(Image.open('data/hearts.png').convert('RGB'), dtype=np.int32)[0:96,96*1:96*2,:],
                    'anchors':[(30,30), (30,60), (60,30), (60,60)],
                    },
        
                'heart_2': {
                    'pattern': np.array(Image.open('data/hearts.png').convert('RGB'), dtype=np.int32)[0:96,96*2:96*3,:],
                    'anchors':[(30,30), (30,60), (60,30), (60,60)],
                    },
        
                'heart_3': {
                    'pattern': np.array(Image.open('data/hearts.png').convert('RGB'), dtype=np.int32)[0:96,96*3:96*4,:],
                    'anchors':[(30,30), (30,60), (60,30), (60,60)],
                    },
        
                'heart_4': {
                    'pattern': np.array(Image.open('data/hearts.png').convert('RGB'), dtype=np.int32)[0:96,96*4:96*5,:],
                    'anchors':[(30,30), (30,60), (60,30), (60,60)],
                    },
        
                'heart_5': {
                    'pattern': np.array(Image.open('data/hearts.png').convert('RGB'), dtype=np.int32)[0:96,96*5:96*6,:],
                    'anchors':[(30,30), (30,60), (60,30), (60,60)],
                    },
        
                'heart_6': {
                    'pattern': np.array(Image.open('data/hearts.png').convert('RGB'), dtype=np.int32)[0:96,96*6:96*7,:],
                    'anchors':[(30,30), (30,60), (60,30), (60,60)],
                    },
        
                'heart_7': {
                    'pattern': np.array(Image.open('data/hearts.png').convert('RGB'), dtype=np.int32)[0:96,96*7:96*8,:],
                    'anchors':[(30,30), (30,60), (60,30), (60,60)],
                    },
        
                'spooky_cookie': {
                    'pattern': np.array(Image.open('data/spookyCookie.png').convert('RGB'), dtype=np.int32),
                    'anchors':[(30,30), (30,60), (60,30), (60,60)],
                    },
        
                'fortune_cookie': {
                    'pattern': np.array(Image.open('data/fortune_icon.png').convert('RGB'), dtype=np.int32),
                    'anchors':[(3,4), (9,6), (7,13), (15,10), (4,13), (10,18), (15,19)],
                    },
        
        }
    
    candidates = detect_pattern_anchors(pattern_dict, ['big_cookie'], game_window_position)
    assert len(candidates) == 1, '[ERRO] cannot detect big cookie'
    big_cookie_y, big_cookie_x = candidates[0]
    print('[INFO] Cookie Clicker window found at (%d, %d) of size (%d x %d)' % (game_window_position[0],
                                                                            game_window_position[1],
                                                                            game_window_position[3],
                                                                            game_window_position[2]))

    with Manager() as manager:

        flags = manager.dict({
            'auto': False,
            'quit': False,
            'fixed_pos': True,
            })

        to_detect_pattern_names = manager.list([])
            
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            thread_detect_popup_cookie = Process(target=periodic_observe_and_react,
                                                  args=(GOLDEN_COOKIE_LOOKING_PERIOD, flags, 'quit',
                                                        detect_pattern_anchors, (pattern_dict, to_detect_pattern_names, game_window_position,),
                                                        click_cookie, (offset_x, offset_y, WAIT,),
                                                ))
            
            thread_detect_popup_cookie.start()
            
            print('[INFO] ready!')
            while(not flags['quit']):
                if flags['auto']:
                    mutex.acquire()
                    if flags['fixed_pos']:
                        mc.position = (offset_x + big_cookie_x, offset_y + big_cookie_y)
                        time.sleep(WAIT)
                    mc.click(mouse.Button.left, 1)
                    time.sleep(WAIT)
                    mutex.release()
            
            thread_detect_popup_cookie.join()
            listener.join()