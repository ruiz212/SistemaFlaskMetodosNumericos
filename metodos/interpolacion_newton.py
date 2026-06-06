import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

class NewtonDividedDifferences:
    """
    Clase que implementa el Método de Interpolación por Diferencias Divididas de Newton.
    Incluye cálculo automático del grado óptimo basado en tolerancia, construcción
    simbólica de la ecuación y módulo de pronóstico.
    """
    def __init__(self, x_data, y_data, tolerancia=0.001, cfg=None):
        """
        Inicializa el interpolador de Newton.
        
        Args:
            x_data (list/array): Puntos en el eje X.
            y_data (list/array): Puntos en el eje Y.
            tolerancia (float): Tolerancia máxima de error para detener el cálculo del grado.
        """
        self.x_data = np.array(x_data, dtype=float)
        self.y_data = np.array(y_data, dtype=float)
        self.tolerancia = tolerancia
        
        self.n = len(self.x_data)
        self.tabla = None
        self.coeficientes = []
        self.grado_optimo = 0
        self.ecuacion_simbolica = None
        self.ecuacion_simplificada = None
        
        self.cfg = cfg if cfg is not None else {}
        self.auto_graph = self.cfg.get('inter_auto_graph', False)
        self.warn_extrap = self.cfg.get('inter_warn_extrap', True)
        self.warnings = []
        
        # Variable simbólica
        self.x_sym = sp.Symbol('x')
        
    def _calcular_tabla_diferencias(self, grado_maximo):
        """
        Calcula la tabla de diferencias divididas hasta un grado específico.
        """
        tabla = np.zeros((self.n, grado_maximo + 1))
        tabla[:, 0] = self.y_data
        
        for j in range(1, grado_maximo + 1):
            for i in range(self.n - j):
                if self.x_data[i + j] - self.x_data[i] == 0:
                    raise ValueError("Puntos X duplicados detectados, división por cero.")
                tabla[i, j] = (tabla[i + 1, j - 1] - tabla[i, j - 1]) / (self.x_data[i + j] - self.x_data[i])
                
        return tabla
        
    def _evaluar_polinomio(self, x_val, coefs, x_data_subset):
        """
        Evalúa el polinomio de Newton con coeficientes dados en un punto x_val.
        """
        resultado = coefs[0]
        producto = 1.0
        for i in range(1, len(coefs)):
            producto *= (x_val - x_data_subset[i - 1])
            resultado += coefs[i] * producto
        return resultado

    def calcular_polinomio_optimo(self):
        """
        Itera sobre los posibles grados del polinomio (1 a n-1) evaluando el error.
        Se detiene cuando el error <= tolerancia o la diferencia es 0.
        """
        self.errores_pasos = []
        self.razon_detencion = ""
        
        for k in range(1, self.n):
            # Calcular tabla temporal hasta grado k
            tabla_temp = self._calcular_tabla_diferencias(k)
            coefs_temp = tabla_temp[0, :k+1]
            
            # Evaluar el error usando el polinomio de grado k
            errores = []
            for i in range(self.n):
                y_calc = self._evaluar_polinomio(self.x_data[i], coefs_temp, self.x_data)
                errores.append(abs(y_calc - self.y_data[i]))
            
            error_maximo = max(errores)
            self.errores_pasos.append(error_maximo)
            
            # Chequear la siguiente diferencia dividida si es exactamente 0
            # Si el error es menor o igual a la tolerancia, nos detenemos.
            if error_maximo <= self.tolerancia:
                self.razon_detencion = f"Se alcanzó la tolerancia esperada (Error: {error_maximo:.6e} ≤ {self.tolerancia})"
                self.grado_optimo = k
                self.tabla = tabla_temp
                self.coeficientes = coefs_temp
                self._construir_ecuacion()
                return
            elif abs(coefs_temp[-1]) < 1e-15 and k > 1:
                self.razon_detencion = f"Las diferencias divididas se hicieron cero (Convergencia exacta, Error: {error_maximo:.6e})"
                self.grado_optimo = k
                self.tabla = tabla_temp
                self.coeficientes = coefs_temp
                self._construir_ecuacion()
                return
                
        # Si no se detuvo por tolerancia, usamos el grado máximo n-1
        self.razon_detencion = f"Se alcanzó el grado máximo posible con {self.n} puntos (Grado {self.n - 1}). Error final: {self.errores_pasos[-1]:.6e}"
        self.grado_optimo = self.n - 1
        self.tabla = self._calcular_tabla_diferencias(self.grado_optimo)
        self.coeficientes = self.tabla[0, :]
        self._construir_ecuacion()

    def _construir_ecuacion(self):
        """
        Construye la ecuación simbólica con sympy usando el grado óptimo,
        y también guarda todos los polinomios intermedios.
        """
        self.polinomios_pasos = []
        P = self.coeficientes[0]
        self.polinomios_pasos.append(sp.simplify(P))
        
        producto = 1
        for i in range(1, self.grado_optimo + 1):
            producto *= (self.x_sym - self.x_data[i - 1])
            P += self.coeficientes[i] * producto
            self.polinomios_pasos.append(sp.simplify(P))
            
        self.ecuacion_simbolica = P
        self.ecuacion_simplificada = self.polinomios_pasos[-1]
        
    def obtener_ecuacion_string(self):
        """Retorna la ecuación simplificada como string."""
        if self.ecuacion_simplificada is None:
            return "Polinomio no calculado."
        return str(self.ecuacion_simplificada)
        
    def obtener_polinomios_pasos(self):
        """Retorna una lista con las ecuaciones en cada grado."""
        if not hasattr(self, 'polinomios_pasos'):
            return []
        return [str(p) for p in self.polinomios_pasos]

    def pronosticar(self, x_nuevos):
        """
        Realiza pronósticos para nuevos valores de X utilizando el polinomio óptimo.
        
        Args:
            x_nuevos (float o list/array): Valores a predecir.
            
        Returns:
            list/array: Valores Y pronosticados.
        """
        if isinstance(x_nuevos, (int, float)):
            x_nuevos = [x_nuevos]
            
        x_nuevos = np.array(x_nuevos, dtype=float)
        
        if self.warn_extrap:
            min_x, max_x = np.min(self.x_data), np.max(self.x_data)
            out_of_bounds = [x for x in x_nuevos if x < min_x or x > max_x]
            if out_of_bounds:
                self.warnings.append(f"Advertencia: Extrapolando para valores {out_of_bounds} fuera del rango [{min_x}, {max_x}]")
                
        y_pronosticos = np.array([self._evaluar_polinomio(x, self.coeficientes, self.x_data) for x in x_nuevos])
        
        return y_pronosticos if len(y_pronosticos) > 1 else y_pronosticos[0]

    def graficar(self, x_pronostico=None, y_pronostico=None):
        """
        Genera la gráfica profesional con matplotlib.
        Muestra puntos originales, la curva suave del polinomio y los pronósticos si los hay.
        """
        plt.style.use('seaborn-v0_8-whitegrid') # Cuadrícula minimalista
        plt.figure(figsize=(10, 6))
        
        # Puntos originales
        plt.scatter(self.x_data, self.y_data, color='blue', s=80, label='Datos Originales', zorder=5)
        
        # Generar puntos para la curva suave
        min_x = np.min(self.x_data)
        max_x = np.max(self.x_data)
        
        if x_pronostico is not None:
            if isinstance(x_pronostico, (int, float)):
                min_x = min(min_x, x_pronostico)
                max_x = max(max_x, x_pronostico)
            else:
                min_x = min(min_x, np.min(x_pronostico))
                max_x = max(max_x, np.max(x_pronostico))
                
        # Margen del 10%
        margen = (max_x - min_x) * 0.1
        if margen == 0: margen = 1
        
        x_curva = np.linspace(min_x - margen, max_x + margen, 300)
        y_curva = [self._evaluar_polinomio(x, self.coeficientes, self.x_data) for x in x_curva]
        
        # Curva suave del polinomio
        plt.plot(x_curva, y_curva, color='dodgerblue', linewidth=2.5, 
                 label=f'Polinomio Óptimo (Grado {self.grado_optimo})')
        
        # Puntos pronosticados
        if x_pronostico is not None and y_pronostico is not None:
            if isinstance(x_pronostico, (int, float)):
                x_pronostico = [x_pronostico]
                y_pronostico = [y_pronostico]
            plt.scatter(x_pronostico, y_pronostico, color='red', marker='*', s=150, 
                        label='Pronósticos', zorder=6)
        
        plt.title('Interpolación por Diferencias Divididas de Newton', fontsize=16, fontweight='bold', pad=15)
        plt.xlabel('Valores de X', fontsize=12)
        plt.ylabel('Valores de Y', fontsize=12)
        plt.legend(fontsize=11, shadow=True)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    print("-" * 60)
    print("MÓDULO DE INTERPOLACIÓN: DIFERENCIAS DIVIDIDAS DE NEWTON")
    print("-" * 60)
    
    # 1. Definición de datos de prueba
    X = [1, 2, 3, 4, 5, 6]
    Y = [1, 8, 27, 64, 125, 216] # Es x^3, así que un grado 3 debería ser exacto
    tolerancia = 0.001
    
    print(f"X originales: {X}")
    print(f"Y originales: {Y}")
    print(f"Tolerancia configurada: {tolerancia}")
    
    # 2. Inicialización y cálculo
    interpolador = NewtonDividedDifferences(X, Y, tolerancia=tolerancia)
    interpolador.calcular_polinomio_optimo()
    
    print("\n--- RESULTADOS ---")
    print(f"Grado óptimo seleccionado: {interpolador.grado_optimo}")
    print(f"Coeficientes de diferencias divididas: {interpolador.coeficientes}")
    print(f"Ecuación simplificada: P(x) = {interpolador.obtener_ecuacion_string()}")
    
    # 3. Pronóstico
    X_nuevos = [2.5, 7.0]
    Y_predichos = interpolador.pronosticar(X_nuevos)
    
    print("\n--- PRONÓSTICOS ---")
    for i, x_n in enumerate(X_nuevos):
        print(f"Para X = {x_n}, Y pronosticado = {Y_predichos[i]}")
        
    # 4. Gráfica
    print("\nGenerando gráfica... (Cierra la ventana de la gráfica para terminar)")
    interpolador.graficar(x_pronostico=X_nuevos, y_pronostico=Y_predichos)
