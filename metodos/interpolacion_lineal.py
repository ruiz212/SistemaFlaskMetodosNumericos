import numpy as np
import sympy as sp

class InterpolacionLineal:
    """
    Clase que implementa la Interpolación Lineal.
    Es un caso particular de Newton para n=2.
    """
    def __init__(self, x_data, y_data, cfg=None):
        self.x_data = [sp.nsimplify(val) for val in x_data]
        self.y_data = [sp.nsimplify(val) for val in y_data]
        
        if len(self.x_data) != 2:
            raise ValueError("La interpolación lineal requiere exactamente 2 puntos.")
            
        if self.x_data[0] == self.x_data[1]:
            raise ValueError("Los valores de x no pueden ser iguales (división por cero).")
            
        self.x_sym = sp.Symbol('x')
        self.polinomios_pasos = []
        self.ecuacion_simbolica = None
        self.ecuacion_simplificada = None
        self.grado = 1
        
    def calcular_polinomio(self):
        x0, x1 = self.x_data[0], self.x_data[1]
        y0, y1 = self.y_data[0], self.y_data[1]
        
        self.polinomios_pasos = []
        
        # Paso 1: Fórmula
        num_str = sp.latex(y1 - y0)
        den_str = sp.latex(x1 - x0)
        y0_str = sp.latex(y0)
        x0_str = sp.latex(x0)
        
        if y0 < 0: y0_str = f"({y0_str})"
        if x0 < 0: 
            binomio_str = f"(x + {sp.latex(-x0)})"
        elif x0 == 0:
            binomio_str = "x"
        else:
            binomio_str = f"(x - {x0_str})"
            
        eq_p1 = f"{y0_str} + \\frac{{{num_str}}}{{{den_str}}} \\cdot {binomio_str}"
        self.polinomios_pasos.append({
            "titulo": "Sustituyendo los valores de los 2 puntos (Fórmula Lineal):",
            "ecuacion": "P_1(x) = " + eq_p1
        })
        
        # Paso 2: Constante resuelta
        m = sp.Rational(y1 - y0, x1 - x0)
        m_str = sp.latex(m)
        if m < 0:
            eq_p2 = f"{y0_str} - {sp.latex(-m)} \\cdot {binomio_str}"
        else:
            eq_p2 = f"{y0_str} + {m_str} \\cdot {binomio_str}"
            
        self.polinomios_pasos.append({
            "titulo": "Calculando la pendiente (Diferencia Dividida):",
            "ecuacion": "P_1(x) = " + eq_p2
        })
        
        # Paso 3: Polinomio final
        P = y0 + m * (self.x_sym - x0)
        P_expand = sp.expand(P)
        
        self.ecuacion_simbolica = P
        self.ecuacion_simplificada = P_expand
        
        self.polinomios_pasos.append({
            "titulo": "Agrupando términos semejantes y reduciendo (Resultado Final):",
            "ecuacion": "P_1(x) = " + sp.latex(P_expand)
        })

    def obtener_ecuacion_string(self):
        if self.ecuacion_simplificada is None:
            return "Polinomio no calculado."
        return sp.latex(self.ecuacion_simplificada)
        
    def obtener_polinomios_pasos(self):
        return self.polinomios_pasos

    def _evaluar_polinomio(self, x_val):
        x_val_exact = sp.nsimplify(x_val)
        return float(self.ecuacion_simplificada.subs(self.x_sym, x_val_exact))
        
    def pronosticar(self, x_nuevos):
        if isinstance(x_nuevos, (int, float)):
            x_nuevos = [x_nuevos]
        return np.array([self._evaluar_polinomio(x) for x in x_nuevos])
