import numpy as np

def interpolacion_lagrange(x_puntos, y_puntos):
    n = len(x_puntos)
    def L(i, x):
        li = 1
        for j in range(n):
            if i != j:
                li *= (x - x_puntos[j]) / (x_puntos[i] - x_puntos[j])
        return li
        
    def P(x):
        return sum(y_puntos[i] * L(i, x) for i in range(n))
        
    return P

def diferencias_divididas(x_puntos, y_puntos):
    n = len(x_puntos)
    tabla = np.zeros((n, n))
    tabla[:, 0] = y_puntos
    
    for j in range(1, n):
        for i in range(n - j):
            tabla[i, j] = (tabla[i + 1, j - 1] - tabla[i, j - 1]) / (x_puntos[i + j] - x_puntos[i])
            
    coefs = tabla[0, :]
    
    def P(x):
        res = coefs[0]
        prod = 1
        for i in range(1, n):
            prod *= (x - x_puntos[i - 1])
            res += coefs[i] * prod
        return res
        
    return coefs.tolist(), P
