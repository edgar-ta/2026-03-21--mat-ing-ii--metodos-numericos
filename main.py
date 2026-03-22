import random
import math
import matplotlib.pyplot as plt


# ============================================================
# NIVEL 1: HERRAMIENTAS NUMÉRICAS
# ============================================================

def exp_taylor_anidada(x, terminos=20):
    """
    Aproxima e^x usando la forma anidada de Taylor.
    """
    resultado = 1.0
    for k in range(terminos, 0, -1):
        resultado = 1.0 + (x / k) * resultado
    return resultado


def ln10_newton_raphson(tol=1e-10, max_iter=100):
    """
    Calcula ln(10) resolviendo e^y - 10 = 0 con Newton-Raphson.
    """
    y = 2.3
    for _ in range(max_iter):
        ey = exp_taylor_anidada(y, terminos=30)
        f = ey - 10.0
        fp = ey
        y_nuevo = y - f / fp
        if abs(y_nuevo - y) < tol:
            return y_nuevo
        y = y_nuevo
    return y


LN10 = ln10_newton_raphson()


def normalizar_numero(n):
    """
    Escribe n = m * 10^k con 1 <= m < 10.
    """
    m = float(n)
    k = 0

    while m >= 10.0:
        m /= 10.0
        k += 1

    while m < 1.0:
        m *= 10.0
        k -= 1

    return m, k


def ln_gregory_vera(z, tol=1e-12, max_iter=10000):
    """
    Calcula ln(z) usando la serie de Gregory-Vera:
        ln(z) = 2 * (x + x^3/3 + x^5/5 + ...)
    donde:
        x = (z - 1)/(z + 1)

    Se acelera con:
        z = m * 10^k
        ln(z) = ln(m) + k * ln(10)
    """
    if z <= 0:
        raise ValueError("ln(z) solo está definido para z > 0.")

    m, k = normalizar_numero(z)
    x = (m - 1.0) / (m + 1.0)

    suma = 0.0
    potencia = x
    n = 0

    while n < max_iter:
        termino = potencia / (2 * n + 1)
        suma += termino

        if abs(termino) < tol:
            break

        potencia *= x * x
        n += 1

    return 2.0 * suma + k * LN10


def log10_aproximado(n):
    """
    Calcula log10(n) = ln(n) / ln(10)
    """
    return ln_gregory_vera(n) / LN10


# ============================================================
# NIVEL 2: INTERPOLACIÓN DE NEWTON
# ============================================================

def diferencias_divididas(xs, ys):
    """
    Construye coeficientes del polinomio de Newton.
    """
    n = len(xs)
    tabla = [y for y in ys]
    coeficientes = [tabla[0]]

    for j in range(1, n):
        nueva = []
        for i in range(n - j):
            valor = (tabla[i + 1] - tabla[i]) / (xs[i + j] - xs[i])
            nueva.append(valor)
        tabla = nueva
        coeficientes.append(tabla[0])

    return coeficientes


def evaluar_newton(xs, coeficientes, x):
    """
    Evalúa el polinomio de Newton en x.
    """
    resultado = coeficientes[0]
    producto = 1.0

    for i in range(1, len(coeficientes)):
        producto *= (x - xs[i - 1])
        resultado += coeficientes[i] * producto

    return resultado


def diferencia_media(y0, y1, x0, x1):
    """
    Pendiente local promedio.
    """
    return (y1 - y0) / (x1 - x0)


# ============================================================
# FORMATO HISTÓRICO DE LA TABLA
# ============================================================

def mantisa_y_caracteristica(valor_log):
    """
    Separa el logaritmo en:
    - característica (parte entera)
    - mantisa entera de 6 dígitos
    """
    caracteristica = int(valor_log)
    mantisa = valor_log - caracteristica
    mantisa_entera = int(round(mantisa * 1_000_000))

    # Control por si redondea a 1.000000
    if mantisa_entera >= 1_000_000:
        mantisa_entera = 999999

    return caracteristica, mantisa_entera


def prefijo_y_sufijo_mantisa(valor_log):
    """
    Devuelve:
    - prefijo: dos primeros dígitos de la mantisa
    - sufijo: últimos cuatro dígitos de la mantisa
    """
    _, mantisa = mantisa_y_caracteristica(valor_log)
    texto = f"{mantisa:06d}"
    prefijo = texto[:2]
    sufijo = texto[2:]
    return prefijo, sufijo


def formatear_columna0(valor_log):
    """
    En columna 0 se imprime la mantisa completa de 6 dígitos.
    """
    _, mantisa = mantisa_y_caracteristica(valor_log)
    return f"{mantisa:06d}"


def formatear_columna_historica(valor_log, prefijo_base):
    """
    Formato estricto histórico para columnas 1..9.

    Reglas:
    - si el prefijo coincide con el de la columna 0, se imprime solo el sufijo;
    - si el prefijo cambia, se sustituyen los dígitos del prefijo por puntos negros
      y se conserva el sufijo.
      Ejemplo:
        mantisa completa = 770042
        prefijo_base = 76
        resultado = ••42
    """
    prefijo_actual, sufijo = prefijo_y_sufijo_mantisa(valor_log)

    if prefijo_actual == prefijo_base:
        return sufijo

    # Cambio real de prefijo: estilo estricto con puntos negros
    return "••" + sufijo[-2:]


def escapar_latex(texto):
    """
    Convierte el punto negro para LaTeX.
    """
    return str(texto).replace("•", r"$\bullet$")


# ============================================================
# IMPRESIÓN EN CONSOLA
# ============================================================

def imprimir_tabla_bloque(inicio_bloque, filas_bloque, indice_bloque, d_vals):
    print(f"\nBloque {indice_bloque + 1} (N = {inicio_bloque} a {inicio_bloque + 9})")
    print("-" * 84)
    print(f"{'N':>5} {'0':>8} {'1':>6} {'2':>6} {'3':>6} {'4':>6} {'5':>6} {'6':>6} {'7':>6} {'8':>6} {'9':>6} {'D':>6}")
    print("-" * 84)

    for fila in range(10):
        n_base = inicio_bloque + fila
        fila_impresa = f"{n_base:>5}"

        prefijo_base, _ = prefijo_y_sufijo_mantisa(filas_bloque[fila][0])

        for col in range(10):
            valor = filas_bloque[fila][col]
            if col == 0:
                celda = formatear_columna0(valor)
                fila_impresa += f" {celda:>8}"
            else:
                celda = formatear_columna_historica(valor, prefijo_base)
                fila_impresa += f" {celda:>6}"

        fila_impresa += f" {d_vals[fila]:>6}"
        print(fila_impresa)

    print("-" * 84)


# ============================================================
# GENERACIÓN DE TABLAS
# ============================================================

def tabla_log(n_inicial):
    """
    Genera 6 bloques de 10 renglones.
    Devuelve:
    - datos_columna_0: [(N, log10_aprox), ...]
    - bloques_latex: estructura lista para exportar a LaTeX
    """
    datos_columna_0 = []
    bloques_latex = []

    for bloque in range(6):
        inicio_bloque = n_inicial + bloque * 10

        # Puntos base: 11 nodos para interpolar 10 filas
        xs = [inicio_bloque + i for i in range(11)]
        ys = [log10_aproximado(x) for x in xs]

        # Columna 0 de las 10 filas visibles
        for i in range(10):
            datos_columna_0.append((xs[i], ys[i]))

        coef = diferencias_divididas(xs, ys)

        filas_bloque = []
        d_vals = []

        for fila in range(10):
            n_base = inicio_bloque + fila
            fila_vals = []

            for col in range(10):
                x_eval = n_base + col / 10.0
                y_eval = evaluar_newton(xs, coef, x_eval)
                fila_vals.append(y_eval)

            filas_bloque.append(fila_vals)

            y0 = ys[fila]
            y1 = ys[fila + 1]
            d = diferencia_media(y0, y1, xs[fila], xs[fila + 1])

            # Diferencia media estilo histórico sobre mantisa
            d_mantisa = int(round(d * 1_000_000 / 10.0))
            d_vals.append(d_mantisa)

        imprimir_tabla_bloque(inicio_bloque, filas_bloque, bloque, d_vals)

        bloque_para_latex = []
        for fila in range(10):
            n_base = inicio_bloque + fila
            fila_latex = [str(n_base)]

            prefijo_base, _ = prefijo_y_sufijo_mantisa(filas_bloque[fila][0])

            for col in range(10):
                valor = filas_bloque[fila][col]
                if col == 0:
                    fila_latex.append(formatear_columna0(valor))
                else:
                    fila_latex.append(formatear_columna_historica(valor, prefijo_base))

            fila_latex.append(str(d_vals[fila]))
            bloque_para_latex.append(fila_latex)

        bloques_latex.append({
            "inicio": inicio_bloque,
            "filas": bloque_para_latex
        })

    return datos_columna_0, bloques_latex


# ============================================================
# EXPORTACIÓN A LATEX
# ============================================================

def guardar_tablas_en_latex(bloques_latex, nombre_archivo, titulo="Tabla de logaritmos"):
    """
    Guarda una o varias tablas en archivo .tex
    """
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(r"\section*{" + titulo + "}" + "\n\n")

        for i, bloque in enumerate(bloques_latex, start=1):
            inicio = bloque["inicio"]

            f.write(r"\subsection*{Bloque " + str(i) +
                    f" (N = {inicio} a {inicio + 9})" + "}\n")
            f.write(r"\begin{center}" + "\n")
            f.write(r"\small" + "\n")
            f.write(r"\begin{tabular}{|r|r|r|r|r|r|r|r|r|r|r|r|}" + "\n")
            f.write(r"\hline" + "\n")
            f.write(r"$N$ & $0$ & $1$ & $2$ & $3$ & $4$ & $5$ & $6$ & $7$ & $8$ & $9$ & $D$ \\" + "\n")
            f.write(r"\hline" + "\n")

            for fila in bloque["filas"]:
                fila_tex = " & ".join(escapar_latex(x) for x in fila)
                f.write(fila_tex + r" \\" + "\n")

            f.write(r"\hline" + "\n")
            f.write(r"\end{tabular}" + "\n")
            f.write(r"\end{center}" + "\n\n")


# ============================================================
# ANÁLISIS DE ERROR
# ============================================================

def calcular_errores_relativos(datos_columna_0):
    """
    Compara cada valor aproximado de la columna 0 contra math.log10(N).
    """
    errores = []

    for n, valor_aprox in datos_columna_0:
        valor_real = math.log10(n)

        if valor_real != 0:
            error_relativo = abs(valor_aprox - valor_real) / abs(valor_real)
        else:
            error_relativo = 0.0

        errores.append((n, valor_aprox, valor_real, error_relativo))

    return errores


def imprimir_resumen_errores(errores_info):
    print("\nResumen de errores relativos")
    print("-" * 78)
    print(f"{'N':>6} {'Aprox':>15} {'Real':>15} {'Error relativo':>18}")
    print("-" * 78)

    for n, aprox, real, err in errores_info:
        print(f"{n:>6} {aprox:>15.8f} {real:>15.8f} {err:>18.10e}")

    errores = [err for _, _, _, err in errores_info]
    if errores:
        print("-" * 78)
        print(f"Error mínimo : {min(errores):.10e}")
        print(f"Error máximo : {max(errores):.10e}")
        print(f"Error promedio: {sum(errores)/len(errores):.10e}")


# ============================================================
# HISTOGRAMA CON ETIQUETAS DE CLASE
# ============================================================

def graficar_histograma(errores_relativos, nombre_archivo="histograma_errores.png", bins=10):
    plt.figure(figsize=(12, 6))

    frecuencias, bordes, barras = plt.hist(
        errores_relativos,
        bins=bins,
        edgecolor='black'
    )

    plt.title("Histograma de errores relativos (columna 0)")
    plt.xlabel("Error relativo")
    plt.ylabel("Frecuencia")
    plt.grid(True, alpha=0.3)

    max_freq = max(frecuencias) if len(frecuencias) > 0 else 1

    for i, barra in enumerate(barras):
        x_izq = bordes[i]
        x_der = bordes[i + 1]
        altura = barra.get_height()
        x_centro = barra.get_x() + barra.get_width() / 2

        etiqueta_clase = f"[{x_izq:.2e}, {x_der:.2e})"

        if altura > 0:
            plt.text(
                x_centro,
                altura + max_freq * 0.04,
                etiqueta_clase,
                ha='center',
                va='bottom',
                rotation=45,
                fontsize=8
            )
            plt.text(
                x_centro,
                altura + max_freq * 0.01,
                f"f={int(altura)}",
                ha='center',
                va='bottom',
                fontsize=8
            )

    plt.tight_layout()
    plt.savefig(nombre_archivo, dpi=300)
    plt.show()


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def main():
    print("=" * 68)
    print("FÁBRICA DE LOGARITMOS - MÉTODO DE PRONY")
    print("=" * 68)
    print(f"ln(10) calculado por Newton-Raphson = {LN10:.10f}")
    print("\nOpciones:")
    print("1) Generar una tabla desde un valor N")
    print("2) Generar 5 tablas aleatorias + histograma + LaTeX")
    print("3) Salir")

    while True:
        opcion = input("\nElige una opción: ").strip()

        if opcion == "1":
            try:
                n_inicial = int(input("Ingresa el valor inicial N (1 a 999): "))
                if not (1 <= n_inicial <= 999):
                    print("Error: N debe estar entre 1 y 999.")
                    continue

                datos_columna_0, bloques_latex = tabla_log(n_inicial)

                nombre_tex = f"tabla_log_{n_inicial:03d}.tex"
                guardar_tablas_en_latex(
                    bloques_latex,
                    nombre_tex,
                    titulo=f"Tabla de logaritmos desde N = {n_inicial}"
                )

                errores_info = calcular_errores_relativos(datos_columna_0)
                imprimir_resumen_errores(errores_info)

                lista_errores = [err for _, _, _, err in errores_info]
                nombre_hist = f"histograma_{n_inicial:03d}.png"
                graficar_histograma(lista_errores, nombre_hist)

                print(f"\nArchivo LaTeX guardado como: {nombre_tex}")
                print(f"Histograma guardado como: {nombre_hist}")
                break

            except ValueError:
                print("Error: Debes ingresar un entero válido.")

        elif opcion == "2":
            valores = random.sample(range(1, 1000), 5)
            todos_los_datos = []
            todos_los_bloques = []

            print("\nValores aleatorios seleccionados:", valores)

            for i, n in enumerate(valores, start=1):
                print("\n" + "=" * 68)
                print(f"TABLA {i} - N inicial = {n}")
                print("=" * 68)

                datos_columna_0, bloques_latex = tabla_log(n)
                todos_los_datos.extend(datos_columna_0)
                todos_los_bloques.extend(bloques_latex)

                nombre_tex_individual = f"tabla_log_{n:03d}.tex"
                guardar_tablas_en_latex(
                    bloques_latex,
                    nombre_tex_individual,
                    titulo=f"Tabla de logaritmos desde N = {n}"
                )

            errores_info = calcular_errores_relativos(todos_los_datos)
            imprimir_resumen_errores(errores_info)

            lista_errores = [err for _, _, _, err in errores_info]
            graficar_histograma(lista_errores, "histograma_5_tablas.png")

            guardar_tablas_en_latex(
                todos_los_bloques,
                "todas_las_tablas.tex",
                titulo="Conjunto de tablas de logaritmos"
            )

            print("\nArchivos generados:")
            print("- todas_las_tablas.tex")
            print("- histograma_5_tablas.png")
            print("- además de un .tex individual por cada tabla")
            break

        elif opcion == "3":
            print("Programa finalizado.")
            break

        else:
            print("Opción no válida. Intenta de nuevo.")


if __name__ == "__main__":
    main()