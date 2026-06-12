import numpy as np
import sympy as sp

class RegresionSimple:
    """
    Clase que implementa el Método de Regresión Simple.
    Calcula la recta y = b0 + b1*x que mejor se ajusta a los datos por mínimos cuadrados.
    """
    def __init__(self, x_data, y_data, cfg=None):
        self.x_data = np.array(x_data, dtype=float)
        self.y_data = np.array(y_data, dtype=float)
        self.n = len(self.x_data)
        
        if self.n < 2:
            raise ValueError("La regresión simple requiere al menos 2 puntos.")
            
        self.x_sym = sp.Symbol('x')
        self.ecuacion_simbolica = None
        self.b0 = 0.0
        self.b1 = 0.0
        
        self.tabla_error = []
        self.R2 = 0.0
        self.r = 0.0
        
    def calcular_modelo(self):
        x = self.x_data
        y = self.y_data
        n = self.n
        
        sum_x = np.sum(x)
        sum_y = np.sum(y)
        sum_x2 = np.sum(x**2)
        sum_xy = np.sum(x * y)
        
        # Mínimos cuadrados
        den = (n * sum_x2 - sum_x**2)
        if den == 0:
            raise ValueError("Todos los valores de x son iguales. No se puede calcular la regresión.")
            
        self.b1 = (n * sum_xy - sum_x * sum_y) / den
        y_mean = sum_y / n
        x_mean = sum_x / n
        self.b0 = y_mean - self.b1 * x_mean
        
        self.ecuacion_simbolica = self.b0 + self.b1 * self.x_sym
        
        # Análisis del error
        SSR = 0.0 # Sum of Squares Regression
        SSE = 0.0 # Sum of Squares Error
        
        self.tabla_error = []
        
        for i in range(n):
            y_pred = self.b0 + self.b1 * x[i]
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
            self.R2 = 1.0 # Caso perfecto si SST = 0 (y constante)
            
        self.r = np.sign(self.b1) * np.sqrt(self.R2)
        
    def obtener_ecuacion_string(self):
        if self.ecuacion_simbolica is None:
            return "Modelo no calculado."
        
        # Formatear ecuación como y = b0 + b1*x
        # Limitamos decimales visuales en el latex pero no perdemos en la cuenta
        b0_round = round(self.b0, 4)
        b1_round = round(self.b1, 4)
        
        sign = "+" if b1_round >= 0 else "-"
        val_b1 = abs(b1_round)
        
        return f"\\hat{{Y}} = {b0_round} {sign} {val_b1} x"
        
    def obtener_resultados_error(self):
        return {
            'tabla': self.tabla_error,
            'R2': self.R2,
            'r': self.r
        }

    def pronosticar(self, x_nuevos):
        if isinstance(x_nuevos, (int, float)):
            x_nuevos = [x_nuevos]
        return np.array([self.b0 + self.b1 * val for val in x_nuevos])
