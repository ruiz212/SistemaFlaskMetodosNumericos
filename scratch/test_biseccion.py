"""Test Biseccion"""
import sys
sys.path.insert(0, r'c:\ProyectoFlaskMetodos')
import numpy as np
from metodos.biseccion import biseccion

def f(x):
    # Looking at the table, f(1)=1. f(0.625)=0.15499. f(0.25)=-1.136.
    # What function is this?
    # Actually I don't need the exact function, I can mock it or just use an arbitrary one that gives similar signs.
    # Wait, the user didn't give the equation.
    pass

# Let's just mock the biseccion function directly to see its condition
def biseccion_mock(a, b, tol):
    c_anterior = None
    i = 1
    while True:
        c_actual = (a + b) / 2.0
        if c_anterior is None:
            error_rp = float('inf')
        elif c_actual != 0:
            error_rp = abs((c_actual - c_anterior) / c_actual) * 100.0
            
        print(f"Iter {i}: a={a}, b={b}, c={c_actual}, error_rp={error_rp}")
        
        if c_anterior is not None and (error_rp / 100.0) < tol:
            print("STOPPED at", i)
            break
            
        # We need f(a)*f(c) signs.
        # From screenshot:
        # Iter 1: a=0.25, b=1. c=0.625. f(a)*f(c) = -0.176 < 0 -> b=c
        # Iter 2: a=0.25, b=0.625. c=0.4375. f(a)*f(c) = 0.442 > 0 -> a=c
        # Iter 3: a=0.4375, b=0.625. c=0.53125. f(a)*f(c) = 0.039 > 0 -> a=c
        # Iter 4: a=0.53125, b=0.625. c=0.578125. f(a)*f(c) = -0.003 < 0 -> b=c
        # Iter 5: a=0.53125, b=0.578125. c=0.554688. f(a)*f(c) = 0.003 > 0 -> a=c
        
        if i == 1: b = c_actual
        elif i == 2: a = c_actual
        elif i == 3: a = c_actual
        elif i == 4: b = c_actual
        elif i == 5: a = c_actual
        else: b = c_actual # just arbitrary

        c_anterior = c_actual
        i += 1
        if i > 20: break

biseccion_mock(0.25, 1.0, 0.0001)
