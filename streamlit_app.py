import streamlit as st
import numpy as np
import pandas as pd
import numpy_financial as npf

# Título de la aplicación
st.title("Análisis de Flujos de Caja con Valor de Rescate y Crecimiento Variable")

# Entrada de datos
n_años = st.number_input("Número de años del proyecto:", min_value=1, value=5, step=1)
inversion_inicial = st.number_input("Inversión inicial:", value=65000.00)
tasa_descuento = st.number_input("Tasa de descuento (%):", value=20.0) / 100
valor_rescate = st.number_input("Valor de rescate al final del proyecto:", value=15000.0)

# Entrada del crecimiento porcentual por separado
crecimiento_ingresos = st.number_input("Crecimiento anual de ingresos (%):", value=5.0) / 100
crecimiento_costo_variable = st.number_input("Crecimiento anual de costo variable (%):", value=5.0) / 100
crecimiento_gastos_fijos = st.number_input("Crecimiento anual de gastos fijos (%):", value=5.0) / 100

# Crear contenedores para flujos de caja y gastos
ingresos = []
costos_variables = []
gastos_fijos = []

st.subheader("Ingresar los flujos de caja")

# Ingresar ingresos, costos variables y gastos fijos para cada año
ingreso_base = st.number_input("Ingresos para el primer año:", value=100000.00)
costo_variable_base = st.number_input("Porcentaje de costo variable para el primer año (%):", value=40.0) / 100
gasto_fijo_base = st.number_input("Gastos fijos para el primer año:", value=20000.00)

for i in range(n_años):
    # Aplicar el crecimiento a ingresos, costos variables y gastos fijos
    ingreso_anual = ingreso_base * ((1 + crecimiento_ingresos) ** i)
    ingresos.append(ingreso_anual)
    
    # Cálculo del costo de ventas con crecimiento
    costo_variable_anual = costo_variable_base * ((1 + crecimiento_costo_variable) ** i)
    costos_variables.append(costo_variable_anual)
    
    # Cálculo del gasto fijo con crecimiento
    gasto_fijo_anual = gasto_fijo_base * ((1 + crecimiento_gastos_fijos) ** i)
    gastos_fijos.append(gasto_fijo_anual)

# Sumar el valor de rescate al último año en los ingresos
ingresos[-1] += valor_rescate

# Calcular el costo de ventas y utilidad neta
costos_de_ventas = [ingreso * cv for ingreso, cv in zip(ingresos, costos_variables)]
total_egresos = [cv + gf for cv, gf in zip(costos_de_ventas, gastos_fijos)]
utilidad_neta = [ingreso - egreso for ingreso, egreso in zip(ingresos, total_egresos)]

# Añadir la inversión inicial como una pérdida en el año 0
utilidad_neta.insert(0, -inversion_inicial)

# Calcular el Valor Actual (VA)
valores_actuales = [utilidad_neta[0]]
for i in range(1, n_años + 1):
    valor_actual = npf.pv(rate=tasa_descuento, nper=i, pmt=0, fv=utilidad_neta[i])
    valores_actuales.append(abs(valor_actual))

# Inicializar correctamente la lista de "Recuperación" (valores acumulados)
valores_acumulados = [valores_actuales[0]]

# Cálculo de la recuperación para cada año
for i in range(1, len(valores_actuales)):
    valores_acumulados.append(valores_acumulados[i - 1] + valores_actuales[i])

# Crear DataFrame para la tabla de resultados
tabla = pd.DataFrame({
    "Año": [f"Año {i}" for i in range(n_años + 1)],
    "Ingresos": [0] + ingresos,
    "Costo Variable (%)": [0] + [cv * 100 for cv in costos_variables],
    "Costo de Ventas": [0] + costos_de_ventas,
    "Gastos Fijos": [0] + gastos_fijos,
    "Total Egresos": [inversion_inicial] + total_egresos,
    "Utilidad Neta": utilidad_neta,
    "Valor Actual (VA)": valores_actuales,
    "Recuperación": valores_acumulados
})

# Mostrar tabla de resultados
st.subheader("Tabla de Flujos de Caja (Escenario Original)")
st.dataframe(tabla)

# Calcular VAN, TIR y VAE
van = npf.npv(tasa_descuento, utilidad_neta)
tir = npf.irr(utilidad_neta)
vae = van * tasa_descuento / (1 - (1 + tasa_descuento) ** -n_años)

# Mostrar VAN, TIR, VAE y Payback
st.subheader("Resultados Escenario Original")
st.write(f"**Valor Actual Neto (VAN):** ${van:,.2f}")
st.write(f"**Tasa Interna de Retorno (TIR):** {tir * 100:.2f}%")
st.write(f"**Valor Anual Equivalente (VAE):** ${vae:,.2f}")

# Cálculo del periodo de recuperación (Payback)
payback = None
for i, acumulado in enumerate(valores_acumulados):
    if acumulado >= 0:
        payback = i
        break

if payback is not None:
    meses = abs((valores_acumulados[payback - 1] * 12) / (valores_acumulados[payback] - valores_acumulados[payback - 1]))
    st.write(f"**Periodo de recuperación (Payback):** {abs(payback - 1)} años, {int(abs(meses))} meses, {int(abs((meses % 1) * 30))} días")
else:
    st.write("**Periodo de recuperación (Payback):** No se recupera la inversión")

# Calcular VAN de ingresos y egresos por separado
van_ingresos = npf.npv(tasa_descuento, [0] + ingresos)
van_egresos = npf.npv(tasa_descuento, [inversion_inicial] + total_egresos)
st.write(f"**VAN Ingresos:** ${van_ingresos:,.2f}")
st.write(f"**VAN Egresos:** ${van_egresos:,.2f}")

# Calcular la razón VAN ingresos/egresos
razon_van = van_ingresos / van_egresos
st.write(f"**Razón VAN Ingresos/VAN Egresos:** {razon_van:.2f}")

# Escenario pesimista: Agregar opción de ajuste
st.subheader("Escenario Pesimista")
ajuste_opcion = st.selectbox("Seleccione qué variable desea ajustar:", ["Ingresos", "Costo Variable", "Gastos Fijos"])

van_objetivo = st.number_input("VAN objetivo (0 para VAN igual a cero):", value=0.0)
nuevo_ingreso_base = ingreso_base
nuevo_costo_variable_base = costo_variable_base
nuevo_gasto_fijo_base = gasto_fijo_base
tolerancia = 0.01
diferencia_van = np.inf

while abs(diferencia_van) > tolerancia:
    if ajuste_opcion == "Ingresos":
        ingresos_pesimistas = [nuevo_ingreso_base * ((1 + crecimiento_ingresos) ** i) for i in range(n_años)]
        ingresos_pesimistas[-1] += valor_rescate
    else:
        ingresos_pesimistas = [ingreso_base * ((1 + crecimiento_ingresos) ** i) for i in range(n_años)]
        ingresos_pesimistas[-1] += valor_rescate

    if ajuste_opcion == "Costo Variable":
        costos_variables_pesimista = [nuevo_costo_variable_base * ((1 + crecimiento_costo_variable) ** i) for i in range(n_años)]
    else:
        costos_variables_pesimista = [costo_variable_base * ((1 + crecimiento_costo_variable) ** i) for i in range(n_años)]

    if ajuste_opcion == "Gastos Fijos":
        gastos_fijos_pesimista = [nuevo_gasto_fijo_base * ((1 + crecimiento_gastos_fijos) ** i) for i in range(n_años)]
    else:
        gastos_fijos_pesimista = [gasto_fijo_base * ((1 + crecimiento_gastos_fijos) ** i) for i in range(n_años)]

    costos_de_ventas_pesimista = [ingreso * cv for ingreso, cv in zip(ingresos_pesimistas, costos_variables_pesimista)]
    total_egresos_pesimista = [cv + gf for cv, gf in zip(costos_de_ventas_pesimista, gastos_fijos_pesimista)]
    utilidad_neta_pesimista = [ingreso - egreso for ingreso, egreso in zip(ingresos_pesimistas, total_egresos_pesimista)]
    utilidad_neta_pesimista.insert(0, -inversion_inicial)
    van_pesimista = npf.npv(tasa_descuento, utilidad_neta_pesimista)
    diferencia_van = van_pesimista - van_objetivo

    # Ajustar la variable seleccionada
    if ajuste_opcion == "Ingresos":
        nuevo_ingreso_base -= diferencia_van / 100
    elif ajuste_opcion == "Costo Variable":
        nuevo_costo_variable_base += diferencia_van / 100
    elif ajuste_opcion == "Gastos Fijos":
        nuevo_gasto_fijo_base += diferencia_van / 100

# Mostrar resultados del ajuste
if ajuste_opcion == "Ingresos":
    st.write(f"Para que el VAN sea igual a ${van_objetivo:,.2f},  los ingresos en el año 1 deberían ser de ${nuevo_ingreso_base:,.2f}.")
elif ajuste_opcion == "Costo Variable":
    st.write(f"Para que el VAN sea igual a ${van_objetivo:,.2f}, el costo variable en el año 1 debería ser de {nuevo_costo_variable_base * 100:.2f}%.")
elif ajuste_opcion == "Gastos Fijos":
    st.write(f"Para que el VAN sea igual a ${van_objetivo:,.2f}, los gastos fijos en el año 1 deberían ser de ${nuevo_gasto_fijo_base:,.2f}.")
