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

# Calcular el Valor Actual (VA), donde el año 0 es negativo y los demás años positivos
valores_actuales = [utilidad_neta[0]]  # Incluir la inversión inicial como valor negativo en el VA
for i in range(1, n_años + 1):
    valor_actual = npf.pv(rate=tasa_descuento, nper=i, pmt=0, fv=utilidad_neta[i])
    valores_actuales.append(abs(valor_actual))  # Los VA a partir del año 1 deben ser positivos

# Inicializar correctamente la lista de "Recuperación" (valores acumulados)
valores_acumulados = [valores_actuales[0]]  # Empezamos con el valor inicial (negativo) de la inversión

# Cálculo de la recuperación para cada año (siguiendo la fórmula correcta)
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
    "Valor Actual (VA)": valores_actuales,  # Los valores actuales ahora son positivos a partir del año 1
    "Recuperación": valores_acumulados  # Valores acumulados corregidos con la fórmula adecuada
})

# Mostrar tabla de resultados
st.subheader("Tabla de Flujos de Caja")
st.dataframe(tabla)

# Calcular VAN, TIR y VAE
van = npf.npv(tasa_descuento, utilidad_neta)
tir = npf.irr(utilidad_neta)
vae = van * tasa_descuento / (1 - (1 + tasa_descuento) ** -n_años)

# Calcular el periodo de recuperación (payback) usando la columna "Recuperación"
recuperacion_positiva = [i for i, va in enumerate(valores_acumulados) if va >= 0]

if recuperacion_positiva:
    año_recuperacion = recuperacion_positiva[0]  # El año en el que se empieza a recuperar
    flujo_acumulado_anterior = valores_acumulados[año_recuperacion - 1]  # El saldo acumulado negativo
    flujo_siguiente_valor_actual = valores_actuales[año_recuperacion]  # El flujo que permite recuperarse
    
    # Corrección de cálculo de la fracción del año, el cálculo ahora se hace sobre el valor anterior y el siguiente flujo
    fraccion_año = abs(flujo_acumulado_anterior) / flujo_siguiente_valor_actual
    fraccion_dias = fraccion_año * 365  # Multiplicamos por los días del año
    payback_meses = fraccion_dias // 30  # Convertimos a meses
    payback_dias = fraccion_dias % 30  # El resto son los días

    payback_años = año_recuperacion - 1  # Ajuste: el payback ocurre en el año anterior (año 2)
    payback_meses = int(payback_meses)
    payback_dias = int(payback_dias)
else:
    payback_años = payback_meses = payback_dias = "No se recupera"

# Mostrar el resultado del periodo de recuperación
st.write(f"**Periodo de recuperación (Payback):** {payback_años} años, {payback_meses} meses, {payback_dias} días")

# Mostrar VAN, TIR, VAE y Payback
st.subheader("Resultados")
st.write(f"**Valor Actual Neto (VAN):** ${van:,.2f}")
st.write(f"**Tasa Interna de Retorno (TIR):** {tir * 100:.2f}%")
st.write(f"**Valor Anual Equivalente (VAE):** ${vae:,.2f}")
st.write(f"**Periodo de recuperación (Payback):** {payback_años} años, {payback_meses} meses, {payback_dias} días")

# Calcular VAN Ingresos y VAN Egresos
van_ingresos = npf.npv(tasa_descuento, [0] + ingresos)
van_egresos = npf.npv(tasa_descuento, [inversion_inicial] + total_egresos)
razon_van = van_ingresos / van_egresos if van_egresos != 0 else float('inf')

# Mostrar VAN Ingresos, VAN Egresos y razón entre ellos
st.write(f"**VAN Ingresos:** ${van_ingresos:,.2f}")
st.write(f"**VAN Egresos:** ${van_egresos:,.2f}")
st.write(f"**Razón VAN Ingresos/VAN Egresos:** {razon_van:.2f}")
