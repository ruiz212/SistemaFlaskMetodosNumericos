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

def regla_de_cramer(A, b):
    det_A = np.linalg.det(A)
    if abs(det_A) < 1e-12:
        return {"error": "El determinante es 0, el sistema no tiene solución única por Cramer."}
    
    n = len(b)
    soluciones = []
    detalles = []
    
    for i in range(n):
        Ai = A.copy().astype(float)
        Ai[:, i] = b
        det_Ai = np.linalg.det(Ai)
        xi = det_Ai / det_A
        soluciones.append(xi)
        detalles.append({"var": f"x{i+1}", "det": float(det_Ai), "matrix": Ai.tolist()})
        
    return {"solucion": soluciones, "det_principal": float(det_A), "detalles": detalles}

def gauss_jordan(A, b):
    n = len(b)
    Ab = np.hstack([A, b.reshape(-1, 1)]).astype(float)
    pasos = []
    
    for i in range(n):
        # Pivoteo
        max_row = i + np.argmax(np.abs(Ab[i:, i]))
        if abs(Ab[max_row, i]) < 1e-12:
            return {"error": "Sistema sin solución única."}
        Ab[[i, max_row]] = Ab[[max_row, i]]
        
        # Normalizar fila pivote
        pivot = Ab[i, i]
        Ab[i, :] /= pivot
        pasos.append({"msg": f"Normalizar R{i+1}: R{i+1} / {pivot:.4f}", "matrix": Ab.copy().tolist()})
        
        # Eliminar otras filas
        for j in range(n):
            if i != j:
                factor = Ab[j, i]
                Ab[j, :] -= factor * Ab[i, :]
                pasos.append({"msg": f"Eliminación: R{j+1} = R{j+1} - ({factor:.4f}) * R{i+1}", "matrix": Ab.copy().tolist()})
                
    return {"solucion": Ab[:, n].tolist(), "pasos": pasos}

def matriz_inversa(A, b):
    n = len(A)
    # Matriz aumentada [A | I]
    AI = np.hstack([A, np.eye(n)]).astype(float)
    pasos = []
    
    for i in range(n):
        # Pivoteo
        max_row = i + np.argmax(np.abs(AI[i:, i]))
        if abs(AI[max_row, i]) < 1e-12:
            return {"error": "La matriz no es invertible (determinante 0)."}
        
        if max_row != i:
            AI[[i, max_row]] = AI[[max_row, i]]
            pasos.append({"msg": f"Intercambio de filas: R{i+1} <-> R{max_row+1}", "matrix": AI.copy().tolist()})
        
        # Normalizar
        pivot = AI[i, i]
        AI[i, :] /= pivot
        pasos.append({"msg": f"Hacer 1 el pivote: R{i+1} = R{i+1} / {pivot:.4f}", "matrix": AI.copy().tolist()})
        
        # Reducir otras filas
        for j in range(n):
            if i != j:
                factor = AI[j, i]
                AI[j, :] -= factor * AI[i, :]
                pasos.append({"msg": f"Transformación: R{j+1} = R{j+1} - ({factor:.4f}) * R{i+1}", "matrix": AI.copy().tolist()})
                
    inversa = AI[:, n:]
    x = np.dot(inversa, b)
    
    return {
        "solucion": x.tolist(), 
        "inversa": inversa.tolist(), 
        "pasos": pasos,
        "msg_final": "Se obtuvo la inversa mediante Gauss-Jordan sobre [A|I] y luego se multiplicó X = A⁻¹ * b"
    }
