import sys
sys.path.append('c:\\\\ProyectoFlaskMetodos')
from metodos.integracion import romberg
import math
import numpy as np

def f(x):
    return np.exp(x)

res = romberg(1, 3, 4, f)
print(res)
