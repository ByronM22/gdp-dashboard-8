import numpy as np

# Definir las funciones para los cálculos
def calcular_costo_venta(ingresos, costos_variables_pct):
    return ingresos * costos_variables_pct

def calcular_total_egresos(costo_venta, gastos_fijos):
    return costo_venta + gastos_fijos

def calcular_utilidad_bruta(ingresos, total_egresos):
    return ingresos - total_egresos

def calcular_valor_actual(utilidad_bruta, tasa_descuento, año):
    return utilidad_bruta / (1 + tasa_descuento) ** año

def calcular_recuperacion_acumulada(valor_actual, recuperacion_anterior):
    return recuperacion_anterior + valor_actual

# Solicitar qué variable ajustar
print("Seleccione la variable que desea ajustar: Ingresos, Gastos, o Costo Variable")
variable_ajustada = input().lower()

# Ingresar los datos base
inversion_inicial = float(input("Ingrese la inversión inicial: "))
tasa_descuento = float(input("Ingrese la tasa de descuento (ejemplo: 0.1 para 10%): "))
años = int(input("Ingrese la cantidad de años a calcular: "))

# Ingresar las listas vacías
ingresos = []
costos_variables_pct = []
gastos_fijos = []
costos_venta = []
total_egresos = []
utilidad_bruta = []
valor_actual = []
recuperacion = []

# Ciclo para ingresar los valores por año
for i in range(años + 1):
    if variable_ajustada == "ingresos":
        ingresos_anuales = float(input(f"Ingrese los ingresos para el año {i}: "))
        ingresos.append(ingresos_anuales)
        costos_variables_pct.append(float(input(f"Ingrese el porcentaje de costo variable para el año {i} (ej. 0.5554 para 55.54%): ")))
        gastos_fijos.append(float(input(f"Ingrese los gastos fijos para el año {i}: ")))

    elif variable_ajustada == "gastos":
        gastos_fijos_anuales = float(input(f"Ingrese los gastos fijos para el año {i}: "))
        gastos_fijos.append(gastos_fijos_anuales)
        ingresos.append(float(input(f"Ingrese los ingresos para el año {i}: ")))
        costos_variables_pct.append(float(input(f"Ingrese el porcentaje de costo variable para el año {i}: ")))

    elif variable_ajustada == "costo variable":
        costos_variables_pct.append(float(input(f"Ingrese el porcentaje de costo variable para el año {i} (ej. 0.5554 para 55.54%): ")))
        ingresos.append(float(input(f"Ingrese los ingresos para el año {i}: ")))
        gastos_fijos.append(float(input(f"Ingrese los gastos fijos para el año {i}: ")))

# Cálculos para cada año
for i in range(años + 1):
    if i == 0:
        # Año 0 - inversión inicial
        costos_venta.append(0)
        total_egresos.append(inversion_inicial)
        utilidad_bruta.append(-inversion_inicial)
        valor_actual.append(-inversion_inicial)
        recuperacion.append(-inversion_inicial)
    else:
        # Calcular costo de venta
        costo_venta = calcular_costo_venta(ingresos[i], costos_variables_pct[i])
        costos_venta.append(costo_venta)
        
        # Calcular total de egresos
        egresos = calcular_total_egresos(costo_venta, gastos_fijos[i])
        total_egresos.append(egresos)
        
        # Calcular utilidad bruta
        utilidad = calcular_utilidad_bruta(ingresos[i], egresos)
        utilidad_bruta.append(utilidad)
        
        # Calcular valor actual
        valor_actual_actualizado = calcular_valor_actual(utilidad, tasa_descuento, i)
        valor_actual.append(valor_actual_actualizado)
        
        # Calcular recuperación acumulada
        recuperacion_acumulada = calcular_recuperacion_acumulada(valor_actual[i], recuperacion[-1])
        recuperacion.append(recuperacion_acumulada)

# Imprimir resultados
print(f"\n{'Año':<10} {'Ingresos':<15} {'Costo Variable (%)':<20} {'Costo de Venta':<20} {'Gastos Fijos':<15} {'Total Egresos':<20} {'Utilidad Bruta':<20} {'Valor Actual':<20} {'Recuperación':<20}")
for i in range(len(ingresos)):
    print(f"{i:<10} {ingresos[i]:<15,.2f} {costos_variables_pct[i]*100:<20.2f} {costos_venta[i]:<20,.2f} {gastos_fijos[i]:<15,.2f} {total_egresos[i]:<20,.2f} {utilidad_bruta[i]:<20,.2f} {valor_actual[i]:<20,.2f} {recuperacion[i]:<20,.2f}")
