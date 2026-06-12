import numpy as np
import sympy as sp

class InterpolacionCuadratica:
    """
    Clase que implementa la Interpolación Cuadrática.
    Es un caso particular de Newton para n=3.
    """
    def __init__(self, x_data, y_data, cfg=None):
        self.x_data = [sp.nsimplify(val) for val in x_data]
        self.y_data = [sp.nsimplify(val) for val in y_data]
        
        if len(self.x_data) != 3:
            raise ValueError("La interpolación cuadrática requiere exactamente 3 puntos.")
            
        if len(set(self.x_data)) < 3:
            raise ValueError("Los valores de x no pueden repetirse (división por cero).")
            
        self.x_sym = sp.Symbol('x')
        self.polinomios_pasos = []
        self.ecuacion_simbolica = None
        self.ecuacion_simplificada = None
        self.grado = 2
        
    def calcular_polinomio(self):
        x0, x1, x2 = self.x_data
        y0, y1, y2 = self.y_data
        
        self.polinomios_pasos = []
        
        # Calcular diferencias divididas
        f_x0_x1 = sp.Rational(y1 - y0, x1 - x0)
        f_x1_x2 = sp.Rational(y2 - y1, x2 - x1)
        f_x0_x1_x2 = sp.Rational(f_x1_x2 - f_x0_x1, x2 - x0)
        
        y0_str = sp.latex(y0)
        if y0 < 0: y0_str = f"({y0_str})"
        
        # Binomios
        b0_str = f"(x - {sp.latex(x0)})" if x0 != 0 else "x"
        b0_str = b0_str.replace('--', '+ ')
        
        b1_str = f"(x - {sp.latex(x1)})" if x1 != 0 else "x"
        b1_str = b1_str.replace('--', '+ ')
        
        # Paso 1: Fórmula
        t1 = f"\\frac{{{sp.latex(y1 - y0)}}}{{{sp.latex(x1 - x0)}}}"
        t2_num = f"\\frac{{{sp.latex(y2 - y1)}}}{{{sp.latex(x2 - x1)}}} - \\frac{{{sp.latex(y1 - y0)}}}{{{sp.latex(x1 - x0)}}}"
        t2_den = f"{sp.latex(x2 - x0)}"
        t2 = f"\\left[ \\frac{{{t2_num}}}{{{t2_den}}} \\right]"
        
        eq_p1 = f"{y0_str} + {t1} \\cdot {b0_str} + {t2} \\cdot {b0_str}{b1_str}"
        self.polinomios_pasos.append({
            "titulo": "Sustituyendo los valores de los 3 puntos (Fórmula Cuadrática):",
            "ecuacion": "P_2(x) = " + eq_p1
        })
        
        # Paso 2: Constantes resueltas
        c1_str = sp.latex(f_x0_x1)
        c2_str = sp.latex(f_x0_x1_x2)
        
        sign_c1 = " - " if f_x0_x1 < 0 else " + "
        sign_c2 = " - " if f_x0_x1_x2 < 0 else " + "
        
        val_c1 = sp.latex(-f_x0_x1) if f_x0_x1 < 0 else c1_str
        val_c2 = sp.latex(-f_x0_x1_x2) if f_x0_x1_x2 < 0 else c2_str
        
        eq_p2 = f"{y0_str}{sign_c1}{val_c1} \\cdot {b0_str}{sign_c2}{val_c2} \\cdot {b0_str}{b1_str}"
        self.polinomios_pasos.append({
            "titulo": "Calculando las diferencias divididas:",
            "ecuacion": "P_2(x) = " + eq_p2
        })
        
        # Paso 3: Polinomio final
        P = y0 + f_x0_x1 * (self.x_sym - x0) + f_x0_x1_x2 * (self.x_sym - x0)*(self.x_sym - x1)
        P_expand = sp.expand(P)
        
        self.ecuacion_simbolica = P
        self.ecuacion_simplificada = P_expand
        
        self.polinomios_pasos.append({
            "titulo": "Agrupando términos semejantes y reduciendo (Resultado Final):",
            "ecuacion": "P_2(x) = " + sp.latex(P_expand)
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
