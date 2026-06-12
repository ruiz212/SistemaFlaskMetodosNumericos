import numpy as np
import sympy as sp

class RegresionPolinomial:
    """
    Clase que implementa el Método de Regresión Polinomial.
    Ajusta una curva de grado m usando mínimos cuadrados.
    """
    def __init__(self, x_data, y_data, grado_m, cfg=None):
        self.x_data = np.array(x_data, dtype=float)
        self.y_data = np.array(y_data, dtype=float)
        self.grado_m = int(grado_m)
        self.n = len(self.x_data)
        
        if self.n < self.grado_m + 1:
            raise ValueError(f"Para una regresión de grado {self.grado_m}, se requieren al menos {self.grado_m + 1} puntos.")
            
        self.x_sym = sp.Symbol('x')
        self.ecuacion_simbolica = None
        self.coefs = [] # [b0, b1, ..., bm]
        
        self.tabla_error = []
        self.R2 = 0.0
        self.r = 0.0
        
    def calcular_modelo(self):
        x = self.x_data
        y = self.y_data
        
        # np.polyfit retorna coeficientes de mayor a menor grado [bm, bm-1, ..., b0]
        # Usamos np.polyfit para una solución numéricamente estable de mínimos cuadrados
        poly_coefs = np.polyfit(x, y, self.grado_m)
        
        # Invertir para que sea [b0, b1, ..., bm]
        self.coefs = poly_coefs[::-1]
        
        # Construir la ecuación simbólica
        P = 0
        for i, coef in enumerate(self.coefs):
            P += coef * (self.x_sym ** i)
            
        self.ecuacion_simbolica = P
        
        # Análisis del error
        y_mean = np.sum(y) / self.n
        SSR = 0.0
        SSE = 0.0
        
        self.tabla_error = []
        
        # Función de predicción
        p_func = np.poly1d(poly_coefs)
        
        for i in range(self.n):
            y_pred = p_func(x[i])
            ssr_i = (y_pred - y_mean)**2
            sse_i = (y[i] - y_pred)**2
            
            SSR += ssr_i
            SSE += sse_i
            
            self.tabla_error.append([
                float(x[i]), 
                float(y[i]), 
                float(y_pred), 
                float(ssr_i), 
                float(sse_i)
            ])
            
        SST = SSR + SSE
        if SST > 0:
            self.R2 = SSR / SST
        else:
            self.R2 = 1.0 # Caso perfecto o y constante
            
        self.r = np.sqrt(self.R2) # En regresión múltiple/polinomial r es la raíz positiva de R2
        
    def obtener_ecuacion_string(self):
        if self.ecuacion_simbolica is None:
            return "Modelo no calculado."
        
        # Formatear ecuación truncando decimales en LaTeX para presentación visual
        eq_str = "\\hat{Y} = "
        for i, coef in enumerate(self.coefs):
            c_round = round(coef, 4)
            if c_round == 0:
                continue
                
            sign = "+" if c_round >= 0 else "-"
            val = abs(c_round)
            
            if i == 0:
                eq_str += f"{c_round}"
            else:
                eq_str += f" {sign} {val}x" if i == 1 else f" {sign} {val}x^{i}"
                
        if eq_str == "\\hat{Y} = ":
            eq_str += "0"
            
        return eq_str
        
    def obtener_resultados_error(self):
        return {
            'tabla': self.tabla_error,
            'R2': self.R2,
            'r': self.r
        }

    def pronosticar(self, x_nuevos):
        if isinstance(x_nuevos, (int, float)):
            x_nuevos = [x_nuevos]
        
        # poly_coefs están en [bm, ..., b0] 
        p_func = np.poly1d(self.coefs[::-1])
        return np.array([p_func(val) for val in x_nuevos])
