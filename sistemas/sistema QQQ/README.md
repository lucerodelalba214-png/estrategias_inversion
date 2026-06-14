# Sistema de Trend Following sobre QQQ

Sistema cuantitativo de seguimiento de tendencia aplicado al ETF **Invesco QQQ (Nasdaq 100)**. Utiliza dos medias móviles simples con lógica asimétrica de entrada y salida.

## Lógica del sistema

**Entrada** (al cierre): el precio cruza por encima de la SMA de entrada **y** no está ya por debajo de la SMA de salida (evita entrar el mismo día que se activa una señal de salida).

**Salida** (al cierre): el precio cae por debajo de la SMA de salida.

El capital no invertido genera un 3% anual (tipo de interés libre de riesgo).

## Optimización

Grid search sobre 1.600 combinaciones de parámetros (SMA entrada y salida de 50 a 245, paso 5). Optimizado por **CARD (rentabilidad anualizada)** sobre el periodo in-sample 2012–2021.

**Parámetros óptimos: SMA entrada = 100 | SMA salida = 205**

La SMA de salida mayor que la de entrada es intencional: permite aguantar correcciones sin ser expulsado del mercado, saliendo solo ante tendencias bajistas sostenidas.

## Resultados

| Periodo | Rol | CARD sistema | CARD QQQ | MAXDD sistema | MAXDD QQQ | Calmar | Win Rate | Profit Factor |
|---------|-----|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 2012–2021 | In-sample | 18.92% | 22.7% | 21% | 29% | 90 | 46% | 15.4 |
| 2022–hoy | Out-of-sample | 16.77% | 14.8% | 14% | 35% | 119 | 29% | 13.2 |
| 2000–2011 | Stress test* | 2.71% | -4.5% | 26% | 80% | 10 | 13% | 8.5 |

*El periodo 2000–2011 incluye la burbuja dotcom (QQQ –80% desde máximos) y la crisis financiera de 2008 (–53%). Se usa como stress test extremo, no como out-of-sample real.

En el bull market del IS el sistema cede algo de rentabilidad al índice a cambio de menor drawdown. En los periodos difíciles (OOS y stress test) supera al QQQ tanto en rentabilidad como en drawdown.

## Estructura

```
collar_QQQ.py              # script principal
resultados_collar_QQQ      # ranking de todas las combinaciones IS
operaciones_collar_QQQ     # operaciones de los parámetros óptimos
crash1_QQQ                 # métricas OOS 2022–hoy
crash2_QQQ                 # métricas stress test 2000–2011
```

## Uso

```bash
python collar_QQQ.py
```

Requiere el CSV de precios de QQQ en `../descarga_datos/historico_precios/QQQ.csv` con columnas `date`, `open`, `close`.
