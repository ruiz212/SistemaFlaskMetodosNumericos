import numpy as np

def eliminacion_gaussiana(A, b):
    n = len(b)
    Ab = np.hstack([A, b.reshape(-1, 1)]).astype(float)
    pasos = []
    
    for i in range(n):
        # Pivoteo parcial
        max_row = i + np.argmax(np.abs(Ab[i:, i]))
        if Ab[max_row, i] == 0:
            return {"error": "El sistema no tiene solución única."}
        Ab[[i, max_row]] = Ab[[max_row, i]]
        
        pasos.append({"msg": f"Pivoteo: fila {i+1} con fila {max_row+1}", "matrix": Ab.copy().tolist()})
        
        for j in range(i + 1, n):
            factor = Ab[j, i] / Ab[i, i]
            Ab[j, i:] -= factor * Ab[i, i:]
            pasos.append({"msg": f"Eliminación: R{j+1} = R{j+1} - ({factor:.4f}) * R{i+1}", "matrix": Ab.copy().tolist()})
            
    # Sustitución hacia atrás
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (Ab[i, n] - np.dot(Ab[i, i+1:n], x[i+1:n])) / Ab[i, i]
        
    return {"solucion": x.tolist(), "pasos": pasos}

def factorizacion_lu(A, b):
    n = len(A)
    L = np.eye(n)
    U = A.copy().astype(float)
    
    for i in range(n):
        for j in range(i + 1, n):
            factor = U[j, i] / U[i, i]
            L[j, i] = factor
            U[j, i:] -= factor * U[i, i:]
            
    # Solve Ly = b
    y = np.linalg.solve(L, b)
    # Solve Ux = y
    x = np.linalg.solve(U, y)
    
    return {"solucion": x.tolist(), "L": L.tolist(), "U": U.tolist()}
