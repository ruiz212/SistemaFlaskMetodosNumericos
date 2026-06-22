import numpy as np
import sympy as sp


class LagrangeInterpolator:
    """
    Clase que implementa el Método de Interpolación de Lagrange.
    Construye los polinomios base L_i(x) y el polinomio interpolante resultante.
    """
    def __init__(self, x_data, y_data, cfg=None):
        self.x_data = np.array(x_data, dtype=float)
        self.y_data = np.array(y_data, dtype=float)
        self.n = len(self.x_data)
        
        self.cfg = cfg if cfg is not None else {}
        self.auto_graph = self.cfg.get('inter_auto_graph', False)
        self.warn_extrap = self.cfg.get('inter_warn_extrap', True)
        self.warnings = []
        
        self.x_sym = sp.Symbol('x')
        self.ecuacion_simbolica = None
        self.ecuacion_simplificada = None
        self.polinomios_pasos = []
        
        # Validación de puntos repetidos
        if len(set(self.x_data)) < len(self.x_data):
            raise ValueError("Puntos X duplicados detectados, división por cero.")
            
    def calcular_polinomio(self):
        """Calcula el polinomio de Lagrange y sus pasos detallados."""
        n = self.n
        x_data = [sp.nsimplify(val) for val in self.x_data]
        y_data = [sp.nsimplify(val) for val in self.y_data]
        
        # Validar puntos repetidos
        if len(set(x_data)) < len(x_data):
            raise ValueError("Puntos X duplicados detectados, división por cero.")
            
        self.polinomios_pasos = []
        
        # Paso 1: Sustituyendo valores
        terms_p1 = []
        for i in range(n):
            num_str = "".join([f"(x - {x_data[j]})" for j in range(n) if i != j])
            num_str = num_str.replace('--', '+ ')
            
            den_str = "".join([f"({x_data[i]} - {x_data[j]})" for j in range(n) if i != j])
            den_str = den_str.replace('--', '+ ')
            
            # y_data[i] puede ser negativo, ajustar para LaTeX
            yi_str = sp.latex(y_data[i])
            if y_data[i] < 0:
                yi_str = f"({yi_str})"
                
            term = f"{yi_str} \\left[ \\frac{{{num_str}}}{{{den_str}}} \\right]"
            terms_p1.append(term)
            
        eq_p1 = " + ".join(terms_p1).replace("+ -", "- ")
        self.polinomios_pasos.append({
            "titulo": "Sustituyendo los valores de la tabla:",
            "ecuacion": f"P_{n-1}(x) = " + eq_p1
        })
        
        # Paso 2: Multiplicando binomios y calculando denominadores
        terms_p2 = []
        for i in range(n):
            num_expr = 1
            den_val = 1
            for j in range(n):
                if i != j:
                    num_expr *= (self.x_sym - x_data[j])
                    den_val *= (x_data[i] - x_data[j])
            
            num_exp_str = sp.latex(sp.expand(num_expr))
            
            yi_str = sp.latex(y_data[i])
            if y_data[i] < 0:
                yi_str = f"({yi_str})"
                
            term = f"{yi_str} \\left[ \\frac{{{num_exp_str}}}{{{den_val}}} \\right]"
            terms_p2.append(term)
            
        eq_p2 = " + ".join(terms_p2).replace("+ -", "- ")
        self.polinomios_pasos.append({
            "titulo": "Multiplicando los binomios del numerador y calculando denominadores:",
            "ecuacion": f"P_{n-1}(x) = " + eq_p2
        })
        
        # Paso 3: Dividiendo constantes con denominadores
        terms_p3 = []
        for i in range(n):
            den_val = 1
            num_expr = 1
            for j in range(n):
                if i != j:
                    den_val *= (x_data[i] - x_data[j])
                    num_expr *= (self.x_sym - x_data[j])
                    
            const_frac = sp.Rational(y_data[i], den_val)
            num_exp_str = sp.latex(sp.expand(num_expr))
            
            if const_frac == 1:
                c_str = ""
            elif const_frac == -1:
                c_str = "-"
            else:
                c_str = sp.latex(const_frac)
                
            # Si c_str tiene fraccion y es el primer termino, ok. 
            # Si es negativo, lo envolvemos si no es el primer término de la suma general
            if const_frac < 0:
                term = f"\\left( {c_str} \\left( {num_exp_str} \\right) \\right)"
            else:
                term = f"{c_str} \\left( {num_exp_str} \\right)"
                
            terms_p3.append(term)
            
        eq_p3 = " + ".join(terms_p3).replace("+ \\left( -", "- \\left( ")
        self.polinomios_pasos.append({
            "titulo": "Dividiendo las constantes con los denominadores y asociando:",
            "ecuacion": f"P_{n-1}(x) = " + eq_p3
        })
        
        # Polinomio final (Paso 4)
        P = 0
        for i in range(n):
            Li = 1
            for j in range(n):
                if i != j:
                    Li *= (self.x_sym - x_data[j]) / (x_data[i] - x_data[j])
            
            Li_simp = sp.simplify(Li)
            self.polinomios_pasos.append({
                "titulo": f"Polinomio Base L<sub>{i}</sub>(x):",
                "ecuacion": f"L_{{{i}}}(x) = " + sp.latex(Li_simp)
            })
            
            P += y_data[i] * Li
            
        P_expand = sp.expand(P)
        self.ecuacion_simbolica = P
        self.ecuacion_simplificada = P_expand
        self.grado = sp.degree(P_expand, gen=self.x_sym)
        
        self.polinomios_pasos.append({
            "titulo": "Agrupando términos semejantes y reduciendo (Resultado Final):",
            "ecuacion": f"P_{{{n-1}}}(x) = " + sp.latex(P_expand)
        })

    def obtener_ecuacion_string(self):
        if self.ecuacion_simplificada is None:
            return "Polinomio no calculado."
        return sp.latex(self.ecuacion_simplificada)
        
    def obtener_polinomios_pasos(self):
        """Retorna la lista de pasos para el frontend."""
        if not hasattr(self, 'polinomios_pasos'):
            return []
        return self.polinomios_pasos

    def _evaluar_polinomio(self, x_val):
        res = 0
        for i in range(self.n):
            li = 1
            for j in range(self.n):
                if i != j:
                    li *= (x_val - self.x_data[j]) / (self.x_data[i] - self.x_data[j])
            res += self.y_data[i] * li
        return res
        
    def pronosticar(self, x_nuevos):
        if isinstance(x_nuevos, (int, float)):
            x_nuevos = [x_nuevos]
            
        x_nuevos = np.array(x_nuevos, dtype=float)
        
        if self.warn_extrap:
            min_x, max_x = np.min(self.x_data), np.max(self.x_data)
            out_of_bounds = [x for x in x_nuevos if x < min_x or x > max_x]
            if out_of_bounds:
                self.warnings.append(f"Advertencia: Extrapolando para valores {out_of_bounds} fuera del rango [{min_x}, {max_x}]")
                
        y_pronosticos = np.array([self._evaluar_polinomio(x) for x in x_nuevos])
        return y_pronosticos if len(y_pronosticos) > 1 else y_pronosticos[0]
