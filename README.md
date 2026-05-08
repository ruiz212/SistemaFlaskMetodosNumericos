# Suite Numérica Pro 🚀

Bienvenido a la **Suite Numérica Pro**, un sistema avanzado construido sobre Flask y Python diseñado para resolver problemas matemáticos complejos usando métodos numéricos. Este proyecto no solo cuenta con un backend matemático robusto basado en `SymPy` y `NumPy`, sino que también presenta un diseño frontend impecable llamado **"Void Prism"**.

## 🎨 Arquitectura de Diseño (CSS y UI)

El sistema utiliza un motor de diseño propio (Vanilla CSS) distribuido en módulos para mantener el rendimiento y la legibilidad:

1. **`base.css` (El Núcleo):** Contiene la lógica del modo Día/Noche. Utiliza variables CSS (`--bg-page`, `--accent-primary`) que se reasignan dinámicamente según la clase `html.light` o `html.dark`. También incluye los estilos globales de los paneles con "Glassmorphism", inputs, botones, tablas y los temas personalizados de librerías externas como *Driver.js* y *SweetAlert2*.
2. **`index.css`:** Contiene los estilos hiper-optimizados de la Landing Page. Se centra en tipografías grandes (Outfit), animaciones de scroll, chips y el Hero Section. Enlaza directamente a las variables de `base.css` para lograr la transición fluida a modo día sin romper la estética.
3. **Animaciones (`animations.js`):** Utiliza `anime.js` para controlar cómo aparecen los elementos del DOM. Al cambiar de página, se hace un fade-in sutil, y al "Limpiar" datos, los elementos salen disparados hacia abajo como si fueran desechados.
4. **Tutoriales Interactivos:** Se integra `driver.js` para guiar a los usuarios nuevos, contextualizándose según la URL activa (Inicio, Ecuaciones, Polinomios o Sistemas).

## 🧠 Lógica Matemática (Backend)

La columna vertebral matemática se encuentra en `metodos/`. La decisión principal del sistema fue separar la lógica de la evaluación del algoritmo.

### `utils.py` (El Compilador)
Antes de que cualquier método itere, la ecuación de texto (ej. `sqrt(x) - cos(x)`) pasa por `compilar_funciones()`. 
* **Conversión Segura:** Convierte la cadena a un árbol de expresiones simbólicas usando `SymPy`.
* **Manejo de Ángulos:** Si el usuario elige "Grados", intercepta internamente las funciones trigonométricas (`sin`, `cos`, etc.) y les inyecta un multiplicador $\frac{\pi}{180}$ dinámico a los argumentos.
* **Evaluación Lambdify:** Traduce la expresión simbólica a una función binaria veloz de Python/Math para evaluar en tiempo real, con una red de seguridad (fallback) si se topa con números complejos (por ejemplo, evaluar $\sqrt{-1}$).

## ⚙️ Métodos Numéricos

El backend cuenta con validaciones estrictas de dominio y toma decisiones matemáticas preventivas para evitar que la aplicación colapse.

### 1. Ecuaciones No Lineales (1 Variable)
* **Bisección y Regla Falsa:** Algoritmos cerrados. El sistema evalúa primero $f(a)$ y $f(b)$. Si $f(a) \cdot f(b) > 0$, el backend **rechaza** la petición y alerta al usuario que no hay cambio de signo, respetando el Teorema de Bolzano.
* **Newton-Raphson:** Utiliza las derivadas simbólicas pre-compiladas. Si en la evaluación la derivada de $x_i$ es $0$, lanza un error previniendo una división entre cero.
* **Secante y Punto Fijo:** Algoritmos abiertos donde el control del error absoluto $|x_i - x_{i-1}|$ dicta cuándo se alcanza la tolerancia.

### 2. Polinomios y Raíces Complejas
A diferencia de los métodos anteriores que pueden fallar si no hay raíces reales, estos métodos están diseñados para el plano complejo.
* **Müller:** Utiliza parábolas en lugar de líneas rectas (secante). Maneja variables de tipo `complex` en Python. Extrae raíces tanto reales como imaginarias.
* **Bairstow:** Busca factores cuadráticos de la forma $x^2 - rx - s$. Divide sintéticamente el polinomio dos veces. Es excelente para limpiar raíces conjugadas.
* **Horner-Newton:** Método acelerado que utiliza división sintética para evaluar derivadas de manera extremadamente eficiente.

### 3. Sistemas No Lineales
* **Newton-Raphson Multivariable (`sistemas.py`):** 
  1. Parsea el número de variables (ej. $x_1, x_2$).
  2. Genera dinámicamente la matriz **Jacobiana** (una matriz de derivadas parciales) iterando sobre los símbolos extraídos por SymPy.
  3. Utiliza álgebra matricial (`np.linalg.inv()`) de NumPy para calcular $X_{i+1} = X_i - J^{-1} \cdot F(X_i)$.
  4. Decisiones de seguridad: Si el Jacobiano resulta ser una matriz singular (su determinante es $0$), el sistema captura el `LinAlgError`, cancela la iteración y notifica al usuario de la falla matemática.

---
_Desarrollado con arquitectura limpia, escalable y una obsesión por la precisión numérica y la experiencia de usuario._
