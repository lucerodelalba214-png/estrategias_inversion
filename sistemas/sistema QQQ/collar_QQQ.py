
#import numpy as np
import pandas as pd
import os
import itertools
from multiprocessing import Pool
#import math


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","descarga_datos", "historico_precios")
OUTPUT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)),"resultados_collar_QQQ")
OUTPUT_CSV2 = os.path.join(os.path.dirname(os.path.abspath(__file__)),"operaciones_collar_QQQ")
OUTPUT_CSV_CRASH1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash1_QQQ")
OUTPUT_CSV_CRASH2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash2_QQQ")

CAPITAL_inicial=100000
resultados= []
in_sample=("2012-01-01","2021-12-31")
out_sample1=("2022-01-01",None) 
out_sample2=("2000-01-01","2011-12-31")     #para incluir hasta el final del intervalo




qqq = pd.read_csv(os.path.join(DATA_DIR, "QQQ.csv"), parse_dates=['date'])
close = qqq.sort_values('date').set_index('date')['close']
open = qqq.sort_values('date').set_index('date')['open']


def estrategia_qqq(params,periodo=in_sample):
    k,l=params
    dias_invertido=0
    tipo_interes=round(0.03/365,5)   #tipo de interes     
    mercado_sano= close>close.rolling(k).mean()
    mercado_salida= close<close.rolling(l).mean()
    CAPITAL=CAPITAL_inicial
    capital_max=CAPITAL_inicial
    MAXDD=0
    acciones=0
    activo=False
    curva_capital = []
    operaciones=[]
    close_insample=close[periodo[0]:periodo[1]]     # cogemos in_sample para optimizar

    for date, precio in close_insample.items():
        if activo==False and mercado_sano[date]==True and mercado_salida[date]==False:      #bucle de compra
            activo=True
            entrada=precio                                  #se compra al precio de cierre
            fecha_entrada=date
            acciones=int(CAPITAL/entrada)
            CAPITAL=CAPITAL-acciones*entrada

        if activo==True and mercado_salida[date]==True:     #bucle de venta
            activo=False                                    #se vende al precio de cierre
            salida=precio
            fecha_salida=date
            CAPITAL=CAPITAL+acciones*salida
            operaciones.append((fecha_entrada,entrada,fecha_salida,salida,acciones,acciones*(salida-entrada))) #como quiero meter varios argumentos necesito una ducpla
            acciones=0
            dias_invertido+=(fecha_salida-fecha_entrada).days
            
        CAPITAL=CAPITAL*(1+tipo_interes)
        capital_hoy= CAPITAL+acciones*precio
        curva_capital.append(capital_hoy)  #voy cosstruyendo la curva de capital
        capital_max=max(capital_hoy,capital_max)
        if capital_max>capital_hoy:
            dd_hoy=abs((capital_max-capital_hoy)/capital_max)
        else:
            dd_hoy=0

        MAXDD=round(max(dd_hoy,MAXDD),2)   
        dias_total = (close_insample.index[-1] - close_insample.index[0]).days      
            #necesitamos el index que son numeros, la variable periodo son string 
  


    ROI=round((capital_hoy/CAPITAL_inicial-1)*100,2)  #retorno total
    CARD=round(((capital_hoy/CAPITAL_inicial)**(365/dias_total)-1)*100,2)  #retorno anualizado
    CARD_INVERTIDO=round(((capital_hoy/CAPITAL_inicial)**(365/dias_invertido)-1)*100,2)  #retorno anualizadotiempo invertido
    CALMAR=CARD/MAXDD
    WIN_RATE=round(100*(sum(1 for x in operaciones if x[5]>0))/(len(operaciones)),2) #el 5 es para acceder al 5 elemento de la tupla
    beneficios = pd.Series([x[5] for x in operaciones]) #hago una serie con la parte de la tupla que tiene el beneficio
    PROFIT_FACTOR = round(abs(beneficios[beneficios > 0].mean() / beneficios[beneficios < 0].mean()), 2)
    retornos = pd.Series(curva_capital).pct_change().dropna() #dropna es para ignorar los NaN
    SHARPE = round((retornos.mean() / retornos.std()) * (252**0.5), 2)

    return(k,l,ROI,CARD,CARD_INVERTIDO,MAXDD,CALMAR,WIN_RATE,PROFIT_FACTOR,SHARPE, round(dias_invertido/dias_total,2))


def operaciones_qqq(params,periodo=in_sample):
    k,l=params
    mercado_sano= close>close.rolling(k).mean()
    mercado_salida= close<close.rolling(l).mean()
    CAPITAL=CAPITAL_inicial
    MAXDD=0
    acciones=0
    activo=False
    operaciones=[]
    close_insample=close[periodo[0]:periodo[1]]

    for date, precio in close_insample.items():
        if activo==False and mercado_sano[date]==True and mercado_salida[date]==False:     
            activo=True
            entrada=precio                                 
            fecha_entrada=date
            acciones=int(CAPITAL/entrada)
            CAPITAL=CAPITAL-acciones*entrada

        if activo==True and mercado_salida[date]==True:    
            activo=False
            salida=precio
            fecha_salida=date
            CAPITAL=CAPITAL+acciones*salida
            operaciones.append((fecha_entrada,entrada,fecha_salida,salida,acciones,acciones*(salida-entrada))) #como quiero meter varios argumentos necesito una ducpla
            acciones=0
           
    return(operaciones)


if __name__ == "__main__":

    media_entrada=list(range(50,250,5))
    media_salida=list(range(50,250,5))

    print(f"calculando {len(media_entrada)*len(media_salida)} combinaciones")


    combinaciones=list( itertools.product(media_entrada,media_salida)) #creamos la lista de combinaciones

    #Pool sólo trabaja con un argumento por lo que la funcion que queremos multiprocesar
    #sólo debe tener un argumento y luego se desempaqueta dentro de la propia función

    with Pool() as pool:
        resultados = pool.map(estrategia_qqq, combinaciones)
     

    #df_operaciones = pd.DataFrame(resultados,columns=['fecha_entrada' ,'entrada','fecha_salida','salida','beneficio']).sort_values('fecha_entrada', ascending=False)
    #df_operaciones.to_csv(OUTPUT_CSV, index=False)
    #print(f"\nGuardado: {OUTPUT_CSV}  operaciones)")

    df_res = pd.DataFrame(resultados,columns=['sma_entrada', 'sma_salida', 'ROI', 'CARD', 'CARD_INVERTIDO',
                         'MAXDD','CALMAR' ,'WIN_RATE', 'PROFIT_FACTOR', 'SHARPE','pct_tiempo_invertido']).sort_values('CARD', ascending=False)
    #en la linea 64 sin el argumento columns da fallo
    df_res.to_csv(OUTPUT_CSV, index=False)
    print(f"\nGuardado: {OUTPUT_CSV}  ({len(df_res)} combinaciones)")

    mejor_params = (int(df_res.iloc[0]['sma_entrada']), int(df_res.iloc[0]['sma_salida']))

    operaciones=operaciones_qqq(mejor_params)

    df_oper=pd.DataFrame(operaciones,columns=['fecha_entrada', 'entrada', 'fecha_salida', 'salida', 'acciones',
                         'PnL'])
    df_oper.to_csv(OUTPUT_CSV2, index=False)
    print(f"\nGuardado: {OUTPUT_CSV2}  ({len(df_oper)} operaciones)")


    crash1=estrategia_qqq(mejor_params,out_sample1)
    df_crash1 = pd.DataFrame([crash1],columns=['sma_entrada', 'sma_salida', 'ROI', 'CARD', 'CARD_INVERTIDO',
                         'MAXDD','CALMAR' ,'WIN_RATE', 'PROFIT_FACTOR', 'SHARPE','pct_tiempo_invertido']).sort_values('CARD', ascending=False)
    df_crash1.to_csv(OUTPUT_CSV_CRASH1, index=False)
    print(f"\nGuardado: crash1)")

    crash2=estrategia_qqq(mejor_params,out_sample2)
    df_crash2 = pd.DataFrame([crash2],columns=['sma_entrada', 'sma_salida', 'ROI', 'CARD', 'CARD_INVERTIDO',
                         'MAXDD','CALMAR' ,'WIN_RATE', 'PROFIT_FACTOR', 'SHARPE','pct_tiempo_invertido']).sort_values('CARD', ascending=False)
    df_crash2.to_csv(OUTPUT_CSV_CRASH2, index=False)
    print(f"\nGuardado: crash2)")

