import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

class CubicSplinesInterpolator:
    """
    Clase que implementa el Método de Interpolación por Trazadores Cúbicos (Splines).
    Condición de frontera: Natural (S''(x_0) = 0 y S''(x_n) = 0).
    """
    def __init__(self, x_data, y_data, cfg=None):
        self.x_data = np.array(x_data, dtype=float)
        self.y_data = np.array(y_data, dtype=float)
        self.n = len(self.x_data)
        
        self.cfg = cfg if cfg is not None else {}
        self.warn_extrap = self.cfg.get('inter_warn_extrap', True)
        self.warnings = []
        
        self.x_sym = sp.Symbol('x')
        self.polinomios = [] # Lista de diccionarios con info de cada spline
        self.ecuaciones_simplificadas = [] # Lista de strings de ecuaciones
        
        # Validar orden de puntos
        if np.any(np.diff(self.x_data) <= 0):
            # Ordenar si no están ordenados
            idx = np.argsort(self.x_data)
            self.x_data = self.x_data[idx]
            self.y_data = self.y_data[idx]
            
        if len(set(self.x_data)) < len(self.x_data):
            raise ValueError("Puntos X duplicados detectados, división por cero.")
            
    def calcular_splines(self):
        n = self.n
        # Convertir a fracciones exactas
        x = [sp.nsimplify(val) for val in self.x_data]
        a = [sp.nsimplify(val) for val in self.y_data]
        
        h = [x[i+1] - x[i] for i in range(n-1)]
        
        # Sistema matricial A * c = b (usando SymPy para mantener fracciones exactas)
        A = sp.zeros(n, n)
        b = sp.zeros(n, 1)
        
        # Splines naturales: c_0 = 0, c_{n-1} = 0
        A[0, 0] = 1
        A[n-1, n-1] = 1
        
        for i in range(1, n - 1):
            A[i, i-1] = h[i-1]
            A[i, i] = 2 * (h[i-1] + h[i])
            A[i, i+1] = h[i]
            b[i, 0] = sp.Rational(3, h[i]) * (a[i+1] - a[i]) - sp.Rational(3, h[i-1]) * (a[i] - a[i-1])
            
        # Resolver sistema para encontrar c
        c = A.solve(b)
        
        self.polinomios = []
        self.ecuaciones_simplificadas = []
        
        for i in range(n - 1):
            # Coeficientes b y d
            b_coef = (a[i+1] - a[i]) / h[i] - h[i] * (2*c[i] + c[i+1]) / 3
            d_coef = (c[i+1] - c[i]) / (3 * h[i])
            
            # Polinomio simbólico S_i(x) exacto
            S_i = a[i] + b_coef*(self.x_sym - x[i]) + c[i]*(self.x_sym - x[i])**2 + d_coef*(self.x_sym - x[i])**3
            S_i_simp = sp.simplify(S_i)
            
            self.polinomios.append({
                'intervalo': [x[i], x[i+1]],
                'ecuacion': S_i_simp,
                'coeficientes': (a[i], b_coef, c[i], d_coef)
            })
            
            # Guardamos la versión string en formato latex
            self.ecuaciones_simplificadas.append(sp.latex(S_i_simp))
            
    def obtener_polinomios_pasos(self):
        """Para splines, retorna la lista de polinomios para el frontend."""
        if not self.ecuaciones_simplificadas:
            return []
        return self.ecuaciones_simplificadas
        
    def _evaluar_spline(self, x_val):
        if not self.polinomios:
            self.calcular_splines()
            
        # Convertir x_val a exacto para evaluación precisa si es necesario, 
        # pero pronosticar usa float, por lo que podemos operar en float.
        x_val_exact = sp.nsimplify(x_val)
        
        # Encontrar el intervalo correspondiente
        # Si x_val está fuera del rango, usar el spline más cercano (extrapolación lineal/cúbica de ese spline)
        if x_val <= float(self.x_data[0]):
            p = self.polinomios[0]
        elif x_val >= float(self.x_data[-1]):
            p = self.polinomios[-1]
        else:
            for p in self.polinomios:
                if p['intervalo'][0] <= x_val_exact <= p['intervalo'][1]:
                    break
                    
        a_coef, b_coef, c_coef, d_coef = p['coeficientes']
        xi = p['intervalo'][0]
        dx = x_val_exact - xi
        res = a_coef + b_coef*dx + c_coef*dx**2 + d_coef*dx**3
        return float(res)
        
    def pronosticar(self, x_nuevos):
        if isinstance(x_nuevos, (int, float)):
            x_nuevos = [x_nuevos]
            
        x_nuevos = np.array(x_nuevos, dtype=float)
        
        if self.warn_extrap:
            min_x, max_x = np.min(self.x_data), np.max(self.x_data)
            out_of_bounds = [x for x in x_nuevos if x < min_x or x > max_x]
            if out_of_bounds:
                self.warnings.append(f"Advertencia: Extrapolando para valores {out_of_bounds} fuera del rango [{min_x}, {max_x}]. Los Splines pueden oscilar mucho en extrapolación.")
                
        y_pronosticos = np.array([self._evaluar_spline(x) for x in x_nuevos])
        return y_pronosticos if len(y_pronosticos) > 1 else y_pronosticos[0]
