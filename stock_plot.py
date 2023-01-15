# -*- coding: utf-8 -*-
"""
Created on Sun Jun 12 03:06:21 2022

@author: nghia_sv
"""

import matplotlib.pyplot as plt

a_base = 10
A = [-1, -2, -3, -4, 2, -2, 4, 5, 10]

plt.subplots()
plt.grid()

a = a_base

for i, ai in enumerate(A):
    plt.plot([i,i+1], [a,a+ai], c='r' if ai < 0 else 'g')
    a = a + ai
    

plt.show()