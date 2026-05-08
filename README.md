# Suite Numérica Pro 🚀

Bienvenido a la **Suite Numérica Pro**, un sistema web avanzado construido con Flask (Backend) y Vanilla CSS/JS (Frontend) diseñado para resolver problemas matemáticos de ingeniería mediante aproximaciones numéricas. 

Este documento explica en detalle y paso a paso la lógica computacional de cada uno de los archivos del sistema, incluyendo cómo el backend procesa los datos y qué función cumple cada condicional (`if`) crítico en los algoritmos.

---

## ⚙️ Análisis Detallado del Motor Matemático (`/metodos`)

El corazón matemático de este proyecto se ubica en el directorio `metodos/`. Cada algoritmo está encapsulado en su propio archivo Python, asegurando escalabilidad y aislamiento estructural.

### 1. El Compilador Central: `utils.py`
Antes de ejecutar cualquier algoritmo, el sistema necesita "entender" las cadenas de texto (ej. `"sqrt(x) - cos(x)"`).
* **`parse_ecuacion()`:** Recibe la ecuación como string. Si el modo es "Grados" (`modo_angulo == 'deg'`), busca todas las instancias de `sin`, `cos`, etc., e inyecta dinámicamente un factor de $\frac{\pi}{180}$ para convertirlas a radianes matemáticamente hablando.
* **`compilar_funciones()`:** Usa la librería `SymPy`. 
  * Convierte la cadena en un objeto simbólico (`sympify`).
  * Calcula la derivada exacta analíticamente (`sp.diff`).
  * Traduce estas funciones simbólicas a funciones ultra rápidas usando `lambdify`.
* **`if isinstance(val, complex):`** Dentro de `evaluar_f()`. Si el sistema detecta que el número evaluado es imaginario (ocurre cuando iteramos métodos como Müller o Bairstow), fuerza a `SymPy` a manejar la evaluación matemática en el plano complejo usando el subsistema `.evalf()` en lugar del estándar matemático real.

---

### 2. Ecuaciones No Lineales (1 Variable)

#### `biseccion.py` (Método de Bisección)
Corta un intervalo $[a, b]$ a la mitad iterativamente hasta encerrar la raíz.
1. **Paso 1:** Evalúa $f(a)$ y $f(b)$.
2. **`if isinstance(fa, complex) and fa.imag != 0:`** Este `if` de seguridad aborta el cálculo inmediatamente si al evaluar $a$ o $b$ el resultado cae en los números imaginarios (ej. $\sqrt{-5}$). Evita bloqueos en funciones con restricciones de dominio.
3. **`if fa * fb > 0:`** La regla de oro (Teorema de Bolzano). Si los signos de $f(a)$ y $f(b)$ son iguales (su multiplicación es positiva), no podemos garantizar que haya una raíz. El sistema aborta y envía un error al usuario.
4. **Bucle `while`:** Calcula el punto medio $c = (a+b)/2$.
5. **`if fa * fc < 0:`** Si hay cambio de signo entre $a$ y $c$, la raíz está en el lado izquierdo. Entonces, $b = c$. Si no, la raíz está en el lado derecho y $a = c$.

#### `regla_falsa.py` (Falsa Posición)
Similar a bisección, pero en lugar de cortar el intervalo a la mitad rígida, traza una línea secante entre $(a, f(a))$ y $(b, f(b))$ y calcula el punto $c$ donde cruza el eje X.
* Usa la fórmula de interpolación lineal: $c = b - \frac{f(b) \cdot (a - b)}{f(a) - f(b)}$.
* **`if fa * fb > 0:`** Tiene la misma validación de Bolzano que Bisección.
* **`if abs(fc) < 1e-15:`** Un condicional que asume que si $f(c)$ es tan absurdamente cercano a 0, hemos dado con la raíz exacta y la iteración debe cortarse.

#### `newton_raphson.py` (Newton-Raphson)
Requiere una función continua y derivable. Traza rectas tangentes (usando la derivada analítica que calculó `utils.py`).
1. Evalúa el punto inicial $f(x_i)$ y la derivada $f'(x_i)$.
2. **`if abs(dfci) < 1e-12:`** (Derivada es igual a cero). Este `if` es crucial. Si la derivada es cero, la tangente es horizontal y jamás cruzará el eje X. Si esto ocurre, el algoritmo se detendría por división por cero. El sistema lo atrapa y devuelve un mensaje de error limpio: "Derivada igual a 0, la tangente es horizontal".
3. Calcula $x_{i+1} = x_i - \frac{f(x_i)}{f'(x_i)}$.

#### `secante.py` (Método de la Secante)
Se usa cuando la derivada analítica es imposible o muy costosa de procesar. Requiere dos valores iniciales $x_0$ y $x_1$, pero no requiere que encierren una raíz.
1. Evalúa $f(x_0)$ y $f(x_1)$.
2. **`if abs(f_x1 - f_x0) < 1e-12:`** Protege contra divisiones por cero. Si las funciones evaluadas de los dos últimos puntos son iguales, la pendiente trazada es 0 y el método explotaría.

#### `punto_fijo.py` (Método del Punto Fijo)
Itera utilizando la forma $x = g(x)$. Convierte internamente $f(x) = 0$ a $g(x) = f(x) + x$.
1. **`if iteracion == 0 and abs(g_prima) >= 1:`** Este `if` evalúa el Teorema de Convergencia local. Si la derivada absoluta de la función $g(x)$ en el punto inicial es mayor a 1, el método va a diverger (los números crecerán infinitamente). El sistema pausa y alerta al usuario con un `warning` para confirmar si desea obligar el cálculo o no.
2. Si el usuario envía el flag `force = True`, este `if` se salta e itera asumiendo los riesgos.

---

### 3. Raíces de Polinomios (Reales y Complejas)

#### `muller.py` (Método de Müller)
Traza una parábola a lo largo de 3 puntos iniciales ($x_0, x_1, x_2$) para encontrar intersecciones. Como las parábolas cruzan el plano imaginario si no tocan el eje X, extrae raíces complejas con facilidad.
1. Calcula las diferencias divididas ($h_0, h_1, \delta_0, \delta_1, a, b, c$).
2. **`if abs(b + rad) > abs(b - rad):`** La fórmula cuadrática tiene $\pm$. Para maximizar el denominador y evitar pérdida de precisión (cancelación catastrófica), Müller usa el signo que haga que el denominador sea el número mayor posible.

#### `bairstow.py` (Método de Bairstow)
Busca factores cuadráticos $(x^2 - rx - s)$ iterando divisores mediante división sintética doble. Acepta coeficientes puros, lo cual elimina errores generados por funciones trigonométricas.
1. Entra a un bucle `while` iterando $r$ y $s$.
2. **`if det == 0:`** Verifica si el Jacobiano del sistema en Bairstow es singular. Si el determinante de la matriz formada por las variaciones parciales es 0, no puede progresar.
3. Al encontrar factores, usa un **`if discriminante > 0:`** para determinar si las raíces que se acaban de extraer son dos raíces reales, si **`< 0`** extrae un par complejo conjugado, y si es **`== 0`** es una raíz real doble.

#### `horner_newton.py` (Horner generalizado)
Utiliza la división sintética (esquema de Horner) repetida no solo para evaluar el polinomio sino para encontrar el valor de su derivada $P'(x)$ en ese mismo punto rápidamente, para luego aplicar Newton-Raphson.
1. Itera usando Horner para hallar $P(r)$ y luego sobre ese vector hallar $P'(r)$.
2. **`if abs(ppr) < 1e-12:`** Al igual que Newton puro, evita dividir sobre una derivada evaluada en cero.

---

### 4. Sistemas de Múltiples Ecuaciones

#### `sistemas.py` (Newton-Raphson Multivariable)
Recibe $N$ ecuaciones con $N$ variables.
1. Utiliza un ciclo `for` y `sp.sympify` para interpretar cada cadena y detectar exactamente qué símbolos ($x_1, y, z$, etc.) introdujo el usuario, los cuales ordena alfabéticamente.
2. **`if len(simbolos) > n:`** Si el usuario indicó un sistema de $2\times2$, pero introdujo las variables $x, y, z$, el sistema aborta y le advierte del desbalance de grados de libertad.
3. Genera la Matriz Jacobiana dinámicamente: calcula la derivada de la ecuación 1 con el primer símbolo, luego con el segundo, y así para todas las filas y columnas.
4. Convierte las funciones a estructuras compiladas de `NumPy` por rendimiento.
5. Inicia el ciclo.
6. **`try: J_inv = np.linalg.inv(J_val)`**: El paso analítico definitivo. Intenta calcular la inversa de la matriz del Jacobiano en el punto actual $X$. Si las funciones forman un sistema que genera filas/columnas linealmente dependientes en ese punto preciso, Numpy lanzará un error de Algebra Lineal (`np.linalg.LinAlgError`). El sistema captura esta excepción con un `except` y evita que el servidor Flask colapse, mandándole el error legible al usuario ("La matriz Jacobiana no se puede invertir").

---

## 💻 Arquitectura de UI y Routing (`app.py` y `main.js`)

* **`app.py`:** Es un micro-orquestador en Flask. Cada endpoint POST (`/api/calcular_nl`, `/api/calcular_sis`, etc.) recupera el JSON. Contiene bloques `try / except` rigurosos de validación de tipos (`float()`). Si un usuario manda texto en la casilla de tolerancia, el sistema responde cordialmente con un error 400 simulado mediante JSON para renderizar en UI en lugar de retornar códigos de estado crudos (HTML 500 server crash).
* **`main.js`:** 
  * Captura las acciones del usuario.
  * Oculta o muestra dinámicamente elementos de interfaz (`if (val === 'Bisección') { muestra campos A y B }`).
  * Desempaqueta el JSON del backend e inyecta iterativamente cada celda en el DOM (`resultados.map(...)`).

## Conclusión
La Suite Numérica Pro es un proyecto robusto que antepone la estabilidad, protegiendo al motor matemático en cada paso mediante validaciones matemáticas exhaustivas para garantizar que los estudiantes e ingenieros no lidien con cuelgues, sino con respuestas algorítmicas claras.
