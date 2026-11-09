import io
import math
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title='FiolaLab | Densidad específica', page_icon='⚗️', layout='wide')
st.markdown('''<style>.block-container{padding-top:1.5rem}.stMetric{background:#eef7f5;border-radius:12px;padding:14px}</style>''', unsafe_allow_html=True)
st.title('⚗️ FiolaLab')
st.caption('Simulador educativo de densidad específica por el método de fiola | Tres ensayos')
st.info('Ingrese las pesadas en gramos. Los valores precargados son únicamente un ejemplo simulado. Todas las pesadas deben hacerse con la fiola aforada al mismo volumen y a temperatura controlada.')

with st.sidebar:
    st.header('Parámetros')
    water_density = st.number_input('Densidad del agua a temperatura de ensayo (g/cm³)', min_value=0.9000, max_value=1.0500, value=0.9970, step=0.0001, format='%.4f', help='Introduzca un valor medido o de tablas acorde con la temperatura del ensayo; no se calcula automáticamente aquí.')
    ref_text = st.text_input('GE de referencia (opcional)', placeholder='Por ejemplo: 2.70')
    st.caption('Sin GE de referencia no se puede calcular el error relativo respecto a un valor aceptado. La dispersión entre pruebas sí se calcula.')

st.subheader('1. Datos de las tres pruebas')
inputs=[]
example = [(120.0,370.0,180.0,407.78),(120.0,370.0,180.0,407.69),(120.0,370.0,180.0,407.86)]
tabs=st.tabs(['Prueba 1','Prueba 2','Prueba 3'])
for i,tab in enumerate(tabs):
    with tab:
        st.markdown('**Pesadas de laboratorio (g)**')
        c1,c2=st.columns(2)
        with c1:
            w1=st.number_input('W1: Fiola vacía',value=example[i][0],step=0.01,key=f'w1_{i}')
            w2=st.number_input('W2: Fiola + agua',value=example[i][1],step=0.01,key=f'w2_{i}')
        with c2:
            w3=st.number_input('W3: Fiola + muestra seca',value=example[i][2],step=0.01,key=f'w3_{i}')
            w4=st.number_input('W4: Fiola + muestra + agua',value=example[i][3],step=0.01,key=f'w4_{i}')
        inputs.append((w1,w2,w3,w4))

st.subheader('2. Resultados y gráficos')
records=[]
errors=[]
for i,(w1,w2,w3,w4) in enumerate(inputs,1):
    ms=w3-w1
    mw=w2-w1
    added=w4-w3
    displaced=mw-added
    if min(w1,w2,w3,w4)<0 or ms<=0 or mw<=0 or added<=0 or displaced<=0 or displaced>=mw:
        errors.append(f'Prueba {i}: revise las pesadas; la masa seca y las masas de agua deben ser físicamente positivas, con desplazamiento menor que el agua de aforo.')
    else:
        ge=ms/displaced
        records.append({'Prueba':f'Prueba {i}', 'Muestra seca (g)':ms, 'Agua desplazada (g)':displaced, 'GE':ge,'Densidad (g/cm³)':ge*water_density})

reference=None
if ref_text.strip():
    try:
        reference=float(ref_text.replace(',','.'))
        if not math.isfinite(reference) or reference<=0:
            raise ValueError
    except ValueError:
        errors.append('La GE de referencia debe ser un número mayor que cero.')
if errors:
    for err in errors: st.error(err)
else:
    df=pd.DataFrame(records)
    avg=df['GE'].mean()
    std=df['GE'].std(ddof=1)
    cv=std/avg*100
    se=std/math.sqrt(3)
    c1,c2,c3,c4=st.columns(4)
    c1.metric('GE promedio',f'{avg:.4f}')
    c2.metric('Densidad promedio',f'{avg*water_density:.4f} g/cm³')
    c3.metric('Desv. estándar (GE)',f'{std:.4f}')
    c4.metric('Coef. variación',f'{cv:.2f} %')
    if reference is not None:
        st.metric('Error relativo frente a GE de referencia',f'{abs(avg-reference)/reference*100:.3f} %')
    st.caption(f'Error estándar estimado de la media: {se:.4f}. La desviación estándar y el CV evalúan repetibilidad, no exactitud. No se aplica una corrección instrumental sin datos de calibración.')
    st.dataframe(df.style.format({'Muestra seca (g)':'{:.2f}','Agua desplazada (g)':'{:.3f}','GE':'{:.4f}','Densidad (g/cm³)':'{:.4f}'}),use_container_width=True,hide_index=True)
    chart1,chart2=st.columns(2)
    with chart1:
        fig,ax=plt.subplots(figsize=(5,3))
        ax.bar(df['Prueba'],df['GE'],color='#0f766e')
        ax.axhline(avg,color='#c2410c',linestyle='--',label=f'Promedio: {avg:.4f}')
        ax.set_ylabel('Gravedad específica (sin unidades)')
        ax.set_title('Comparación entre las pruebas')
        ax.legend(fontsize=8)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    with chart2:
        fig,ax=plt.subplots(figsize=(5,3))
        ax.bar(df['Prueba'],df['Agua desplazada (g)'],color='#2563eb')
        ax.set_ylabel('Masa de agua desplazada (g)')
        ax.set_title('Agua desplazada por la muestra')
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    csv=df.to_csv(index=False).encode('utf-8-sig')
    st.download_button('⬇️ Descargar resultados CSV (abre en Excel)',csv,'fiolalab_resultados.csv','text/csv')

with st.expander('📘 Fundamento y esquema del método'):
    st.latex(r'GE = \frac{W_3-W_1}{(W_2-W_1)-(W_4-W_3)}')
    st.write('W1: fiola vacía; W2: fiola con agua hasta aforo; W3: fiola con muestra seca; W4: fiola con muestra y agua hasta aforo.')
    st.write('GE es adimensional. Densidad del sólido (g/cm³) = GE × densidad del agua (g/cm³).')
    st.write('Esquema del procedimiento:')
    st.code('Fiola vacía (W1)  →  Fiola + agua (W2)\n         ↓\nFiola + muestra seca (W3)  →  Fiola + muestra + agua (W4)')
    st.warning('Evite burbujas y pérdida de sólido; controle la temperatura y utilice la misma marca de aforo. La incertidumbre de la balanza exige datos de calibración si se desea estimar la incertidumbre instrumental.')
