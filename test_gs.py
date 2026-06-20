import numpy as np

# Matriz exacta del Excel del usuario (Gauss-Seidel)
A = np.array([
    [9, -2, -3, 1],
    [3, 8, -1, 2],
    [-1, 3, -10, -2],
    [2, -1, -2, 7]
], dtype=float)

b = np.array([3, -11, -20, -15], dtype=float)
x = np.zeros(4, dtype=float)
tol = 0.00001
n = 4

print(f"{'Iter':>4} | {'x1 new':>14} {'x2 new':>14} {'x3 new':>14} {'x4 new':>14} | {'Err x1':>14} {'Err x2':>14} {'Err x3':>14} {'Err x4':>14} | Decisiones")
print("-" * 180)

prev_all_final = False

for k in range(1, 30):
    x_new = x.copy()
    errores = [None]*n
    
    for i in range(n):
        suma = 0
        for j in range(n):
            if i != j:
                suma += A[i, j] * x_new[j]
        val_old = x_new[i]
        x_new[i] = (b[i] - suma) / A[i, i]
        
        if k > 1:
            if x_new[i] != 0:
                errores[i] = abs((x_new[i] - val_old) / x_new[i]) * 100
            else:
                errores[i] = 0.0
    
    err_strs = []
    for e in errores:
        if e is None:
            err_strs.append(f"{'':>14}")
        else:
            err_strs.append(f"{e:>14.8f}")
    
    # Decisiones con comparacion directa
    decisions = []
    if k == 1:
        decisions = ["", "", "", ""]
    else:
        for i in range(n):
            if errores[i] > tol:
                decisions.append("Cont")
            else:
                decisions.append("Fin ")
    
    all_final_now = (k > 1) and all(d.strip() == "Fin" for d in decisions)
    
    print(f"{k:>4} | {x_new[0]:>14.8f} {x_new[1]:>14.8f} {x_new[2]:>14.8f} {x_new[3]:>14.8f} | {err_strs[0]} {err_strs[1]} {err_strs[2]} {err_strs[3]} | {decisions}")
    
    x = x_new.copy()
    
    if prev_all_final and all_final_now:
        print(f"\n==> DETENIDO en iteracion {k} (confirmacion de Finalizar)")
        break
    prev_all_final = all_final_now

print(f"\nTotal iteraciones: {k}")
