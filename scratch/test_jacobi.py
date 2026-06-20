"""Test: raw error vs percentage error comparison with tol=0.00001"""
import sys
sys.path.insert(0, r'c:\ProyectoFlaskMetodos')
import numpy as np

A = np.array([[7, 3, -1, 2], [1, 5, -1, 3], [2, 0, 4, -1], [-1, 1, 1, -3]], dtype=float)
b = np.array([3, -2, 21, 14], dtype=float)
x = np.zeros(4)
n = 4
tol = 0.00001

print("CURRENT CODE (percentage vs tol):")
print(f"tol = {tol}")
for k in range(1, 51):
    x_new = np.zeros(4)
    for i in range(n):
        s = sum(A[i,j]*x[j] for j in range(n) if j!=i)
        x_new[i] = (b[i] - s) / A[i,i]
    
    if k > 1:
        errs_pct = [abs((x_new[i]-x[i])/x_new[i])*100 for i in range(n)]
        errs_raw = [abs((x_new[i]-x[i])/x_new[i]) for i in range(n)]
        
        all_final_pct = all(e <= tol for e in errs_pct)
        all_final_raw = all(e <= tol for e in errs_raw)
        
        if k <= 22 or all_final_pct or all_final_raw:
            print(f"  Iter {k:2d}: max_err_pct={max(errs_pct):.8f}%  max_err_raw={max(errs_raw):.10f}  "
                  f"pct<={tol}? {'SI' if all_final_pct else 'NO'}  raw<={tol}? {'SI' if all_final_raw else 'NO'}")
        
        if all_final_pct:
            print(f"\n  >>> PARA con comparacion PORCENTAJE en iteracion {k}")
            break
    x = x_new.copy()

print()
x = np.zeros(4)
print("FIXED CODE (raw decimal vs tol):")
for k in range(1, 51):
    x_new = np.zeros(4)
    for i in range(n):
        s = sum(A[i,j]*x[j] for j in range(n) if j!=i)
        x_new[i] = (b[i] - s) / A[i,i]
    
    if k > 1:
        errs_raw = [abs((x_new[i]-x[i])/x_new[i]) for i in range(n)]
        all_final = all(e <= tol for e in errs_raw)
        
        if k >= 18 or all_final:
            errs_pct = [e*100 for e in errs_raw]
            print(f"  Iter {k:2d}: errors_display={[f'{e:.6f}%' for e in errs_pct]}  raw<={tol}? {'SI' if all_final else 'NO'}")
        
        if all_final:
            print(f"\n  >>> PARA con comparacion RAW en iteracion {k}")
            break
    x = x_new.copy()
