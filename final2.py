# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 12:57:48 2022

@author: gabri
"""
##Importar librerías
import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import plotly.graph_objects as go
import base64
import numpy as np


##Descargar bases de datos
def get_table_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="Accidentes Palmira.csv">Descargar base de datos Palmira csv</a>'
    return href

def get_table_download_Envigado(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="Accidentes Envigado.csv">Descargar base datos Envigado csv</a>'
    return href

def get_table_download_Medellin(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="Accidentes Medellín.csv">Descargar base de datos Medellín csv</a>'
    return href

# Utilizar la página completa en lugar de una columna central estrecha
st.set_page_config(layout="wide")

# Título principal, h1 denota el estilo del título 1
st.markdown("<h1 style='text-align: center; color: #951F0F;'>Accidentalidad Vial Palmira, Envigado y Medellín </h1>", unsafe_allow_html=True)

# Carga bases de datos
df1= pd.read_excel('Accidentes_de_transito_Palmira_2020.xlsx')
df2= pd.read_excel('Envigado.xlsx') 
df3= pd.read_excel('DATOS 2020.xlsx')
 
# Convertir columna FECHA a formato fecha
df1['FECHA'] = pd.to_datetime(df1['FECHA']) 
df2['FECHA'] = pd.to_datetime(df2['FECHA']) 
df3['FECHA_ACCIDENTE'] = pd.to_datetime(df3['FECHA_ACCIDENTE']).dt.date # convertir fecha a formato fecha y separar la hora de la fecha
df3['FECHA_ACCIDENTE'] = pd.to_datetime(df3['FECHA_ACCIDENTE'])

##Se renombran las columnas que tienen en comun las tres bases, para que todas queden con el mismo nombre
df3 = df3.rename(columns ={'GRAVEDAD_ACCIDENTE':'GRAVEDAD'})
df2 = df2.rename(columns ={'CLASE DE ACCIDENTE':'CLASE_ACCIDENTE'})
df1 = df1.rename(columns ={'CLASE DE SINIESTRO':'CLASE_ACCIDENTE'})
df3 = df3.rename(columns ={'FECHA_ACCIDENTE':'FECHA'}) 

#Para que todas las categorías de la columna GRAVEDAD de cada base queden iguales
df2['GRAVEDAD'] = df2['GRAVEDAD'].replace({'Solo latas':'DAÑOS','Heridos':'HERIDOS','Muertos':'MUERTO'})
df3['GRAVEDAD'] = df3['GRAVEDAD'].replace({'Solo daÃ±os':'DAÑOS','Con heridos':'HERIDOS','Con muertos':'MUERTO'})

#Para que todas las categorías de la columna CLASE_ACCIDENTE de cada base queden iguales
df1['CLASE_ACCIDENTE']=df1['CLASE_ACCIDENTE'].replace({'CHOQUE OBJETO FIJO':'CHOQUE','CHOQUE SEMOVIENTE':'CHOQUE','CHOQUE MURO':'CHOQUE'})
df1['CLASE_ACCIDENTE']=df1['CLASE_ACCIDENTE'].map(str.lower)
df2['CLASE_ACCIDENTE']=df2['CLASE_ACCIDENTE'].map(str.lower)
df3['CLASE_ACCIDENTE']=df3['CLASE_ACCIDENTE'].map(str.lower)

#Se cambian los nulos por la palabra Sin Inf
df3 = df3.fillna('Sin Inf') 

df4= pd.DataFrame(pd.date_range(start=df1['FECHA'].min(), end=df1['FECHA'].max())).rename(columns ={0:'FECHA'}) ##Serie de Tiempo de la ciudad de Palmira
df5= pd.DataFrame(pd.date_range(start=df2['FECHA'].min(), end=df2['FECHA'].max())).rename(columns ={0:'FECHA'})##Serie de tiempo Envigado
df6= pd.DataFrame(pd.date_range(start=df3['FECHA'].min(), end=df3['FECHA'].max())).rename(columns ={0:'FECHA'})##Serie de tiempo Medellín

#Se procede a unir la base de datos original con la serie de tiempo correspondiente, para esto se utiliza la funcion merge
df7= pd.merge(df4, df1, on ='FECHA', how ='left')##Palmira
df8= pd.merge(df5, df2, on ='FECHA', how ='left')##Envigado
df9= pd.merge(df6, df3, on ='FECHA', how ='left')##Medellín

#Luego se procede a agrupar la cantidad de accidentes por la fecha, gravedad y la clase de accidente y se hace un count para contar la cantidad de accidentes que hubo
palmira=df7.groupby(['FECHA','GRAVEDAD','CLASE_ACCIDENTE'])[['JORNADA']].count().reset_index()
envigado=df8.groupby(['FECHA','GRAVEDAD','CLASE_ACCIDENTE'])[['RADICADO']].count().reset_index()
medellin=df9.groupby(['FECHA','GRAVEDAD','CLASE_ACCIDENTE'])[['NUMCOMUNA']].count().reset_index()

#Se agrupan las tres bases de datos con el merge para observar la cantidad de accidentes que hubo en la ciudad de Palmira, Envigado y Medellín dependiendo de la fecha
bodega=pd.merge(palmira,envigado, on=['FECHA','GRAVEDAD','CLASE_ACCIDENTE'], how='outer').merge(medellin, on=['FECHA','GRAVEDAD','CLASE_ACCIDENTE'], how='outer').rename(columns ={'JORNADA':'PALMIRA','RADICADO':'ENVIGADO','NUMCOMUNA':'MEDELLIN'})
bodega= bodega.fillna(0.0)  #se cambian los nulos de la bodega de datos anterior por ceros

    
#------------------------------------------------------------------------------------------

#--------------- Palmira

c1, c2, c3 = st.columns((1,1,1)) # Dividir el ancho en 3 columnas de igual tamaño
c1.markdown("<h3 style='text-align: left; color: blue;'> Palmira </h3>", unsafe_allow_html=True)

##¿CÚAL ES LA CANTIDAD DE ACCIDENTES POR JORNADA EN LA CIUDAD DE PALMIRA?
Pal=df1.groupby(['JORNADA'])[['GRAVEDAD']].count().reset_index().sort_values('GRAVEDAD', ascending = False).rename(columns ={'GRAVEDAD':'CANTIDAD'})

indicadorpal = c1.selectbox('SELECCIONE UNA OPCIÓN', ['Accidentes por jornada',  'Accidentes según la condición de la victima' ],
                            format_func=lambda x: 'Seleccione una opción' if x == '' else x)
if indicadorpal =='Accidentes por jornada':
    fig = px.pie(Pal , values = 'CANTIDAD', names = 'JORNADA', title = '<b>% Accidentes según la jornada<b>',
                 hole = .5, width=500, height=450)

    cant_ed = Pal['CANTIDAD'].sum()


    # Poner detalles a la gráfica
    fig.update_layout(
        template = 'simple_white',
        legend_title = 'Jornada',
        title_x = 0.5,
        annotations = [dict(text = str(cant_ed), x=0.5, y = 0.5, font_size = 40, showarrow = False )])


    # Enviar gráfica a streamlit
    c1.plotly_chart(fig)
    if c1.checkbox('Visualizar tabla de cantidad accidentes por la jornada', False):
        c1.write(Pal)
       
    
elif indicadorpal =='Accidentes según la condición de la victima':
    con=df1.groupby(['CONDICION DE LA VICTIMA'])[['GRAVEDAD']].count().reset_index()
    fig = px.bar(con, x='GRAVEDAD', y='CONDICION DE LA VICTIMA', color = 'CONDICION DE LA VICTIMA', barmode= 'group', title ='<b>ACCIDENTES SEGÚN LA VICTIMA')

    # Agregar detalles a la gráfica
    fig.update_layout(
        xaxis_title = 'Cantidad de accidentes',
        yaxis_title = 'Tipo de Victima',
        template = 'plotly_dark',
        title_x = 0.5,
        legend_title = '<b>Tipo de victima<b>')
    
    c1.plotly_chart(fig)
    if c1.checkbox('Visualizar tabla de cantidad accidentes según la condición de la victima', False):
        c1.write(con)

    
#----------------------------------------------------------------------------

#--------------- Envigado

c2.markdown("<h3 style='text-align: left; color: blue;'> Envigado </h3>", unsafe_allow_html=True)

indicadorenv = c2.selectbox('SELECCIONE UNA OPCIÓN', ['Accidentes por sexo',  'Accidentes por tipo de servicio' ],
                            format_func=lambda x: 'Seleccione una opción' if x == '' else x)
if indicadorenv =='Accidentes por sexo':
    #¿CUAL ES LA PROPORCIÓN DE ACCIDENTES EN LA CIUDAD DE ENVIGADO TENIENDO EN CUENTA EL SEXO?
    sexo=df8.groupby(['SEXO'])[['RADICADO']].count().reset_index().rename(columns={'RADICADO':'ACCIDENTES'})
    #Se realiza el grafico de dataframe total
    fig = px.pie(sexo, values = 'ACCIDENTES', names = 'SEXO', title = '<b>% Accidentes según el sexo<b>', width=520, height=450)
    # Agregar detalles a la gráfica
    fig.update_layout(
        template = 'simple_white',
        legend_title = 'Sexo',
        title_x = 0.5)
    
    # Enviar gráfica a streamlit
    c2.plotly_chart(fig)
    if c2.checkbox('Visualizar tabla de cantidad accidentes por sexo', False):
        c2.write(sexo)

elif indicadorenv =='Accidentes por tipo de servicio':
    #¿SEGÚN EL TIPO DE SERVICIO, CÚAL ES LA FRECUENCIA DE ACCIDENTALIDAD EN LA CIUDAD DE ENVIGADO?
    
    #Se crea un dateframe con tipo de servicio y lo cuento con radicado, ordeno de manera descendente
    tipo_servicio=df8.groupby(['TIPO DE SERVICIO'])[['RADICADO']].count().sort_values('RADICADO', ascending = False).reset_index()
    tipo_servicio['TIPO DE SERVICIO']= tipo_servicio['TIPO DE SERVICIO'].str.upper() # se transforma la columna en mayuscula
    
    # Hacer la gráfica
    fig = px.pie(tipo_servicio , values = 'RADICADO', names = 'TIPO DE SERVICIO', title = '<b>% ACCIDENTES SEGUN EL TIPO DE SERVICIO<b>',
                  hole = .5)
    
    cant_ed = tipo_servicio['RADICADO'].sum()
    
     # Poner detalles a la gráfica
    fig.update_layout(
         template = 'simple_white',
         legend_title = 'Tipo de Servicio',
         title_x = 0.5,
         annotations = [dict(text = str(cant_ed), x=0.5, y = 0.5, font_size = 40, showarrow = False )])
    
     # Enviar gráfica a streamlit
    c2.plotly_chart(fig)
    if c2.checkbox('Visualizar tabla de cantidad accidentes según el tipo de servicio', False):
        c2.write(tipo_servicio)
   
#-------------------------------------------------------------------------------------

#---------------Medellín

c3.markdown("<h3 style='text-align: left; color: blue;'> Medellín </h3>", unsafe_allow_html=True)

df11= df3.copy()  #se crea una copia del dataframe df3(base original de medellín)
#Se renombraron algunos comunas de la columna comuna, para que queden siendo únicas
df11['COMUNA']=df11['COMUNA'].replace({'Corregimiento de San CristÃ³bal':'Corregimiento de San Cristobal','Corregimiento de San SebastiÃ¡n de Palmitas':'Corregimiento de San Sebastian de Palmitas','La AmÃ©rica':'La America','BelÃ©n':'Belen','0':'Sin Inf'})
df11= df11.drop(df11[df11['COMUNA']=='Sin Inf'].index)

#Se toma la columna location, se extraen los datos de longitud y latitud y se crean columnas nuevos con estos datos
df11['LONGITUD'] = df11['LOCATION'].apply (lambda x: x.strip('][').split(',')[0]).astype(float) 
df11['LATITUD'] = df11['LOCATION'].apply (lambda x: x.strip('][').split(',')[1]).astype(float)
indicadormed = c3.selectbox('SELECCIONE UNA OPCIÓN', ['Accidentalidad Medellín', 'Accidentes por comunas', 'Accidentes según el diseño de la vía' ],
                            format_func=lambda x: 'Seleccione una opción' if x == '' else x)
if indicadormed =='Accidentalidad Medellín':
    c3.write(pdk.Deck( # Código para crear el Set up del mapa
    
        map_style='mapbox://styles/mapbox/dark-v10',
        initial_view_state={
            'latitude' : df11['LATITUD'].mean(),
            'longitude': df11['LONGITUD'].mean(),
            'zoom' : 11.5,
            'pitch': 50
            },
        
        # Capa con información
        layers = [pdk.Layer(
            'HexagonLayer',
            data = df11[['NUMCOMUNA','LATITUD','LONGITUD']],
            get_position = ['LONGITUD','LATITUD'],
            radius = 80,
            extruded = True,
            elevation_scale = 10,
            elevation_range = [0,1000])]
        ))


elif indicadormed == 'Accidentes por comunas':
#¿CÚALES SON LAS COMUNAS DE MEDELLÍN EN DONDE SE PRESENTA MAYOR ACCIDENTALIDAD? 
    token_map = 'pk.eyJ1IjoibGF1cmF5YXJjZTE5IiwiYSI6ImNsN2k5eTJuNDBtYjQzb252dnpid3hkOGsifQ.4DM4nHHs4U5PEFlsADNrPQ'
    px.set_mapbox_access_token(token_map)
    # generar gráfica
    df12 = df11.dropna(subset =['COMUNA']) # Quitar valores nulos de COMUNA
    c3.plotly_chart(px.scatter_mapbox(df12, lat = 'LATITUD', lon = 'LONGITUD', color ='COMUNA', mapbox_style  = 'streets',width=700, height=450,
                      color_continuous_scale = px.colors.cyclical.IceFire, size_max = 30, zoom = 10))

elif indicadormed == 'Accidentes según el diseño de la vía':
#¿CÚAL ES LA CANTIDAD DE ACCIDENTES SEGÚN EL DISEÑO DE LA VIA DONDE FUE EL ACCIDENTE?
    df9=df9.rename(columns ={'DISEÃ\x91O':'DISEÑO'})  #Se renombra el titulo de la columna 
    df9['DISEÑO']=df9['DISEÑO'].replace({'PontÃ³n':'Ponton'})  #se reemplaza el nombre
    
    # Se crea un dataframe con la columna diseño, se cuenta con expediente y se ordena de manera descendente
    tramo_via = df9.groupby(['DISEÑO'])[['EXPEDIENTE']].count().sort_values('EXPEDIENTE', ascending = False).rename(columns={'EXPEDIENTE':'ACCIDENTES'})
    tramo_via['porcentaje'] = tramo_via.apply(lambda x: x.cumsum()/tramo_via['ACCIDENTES'].sum()) #Agregamos columna con el porcentaje acumulado segun la frecuencia de accidentes
    
    # importar paquete
    import plotly.graph_objects as go 
    
    # Se realiza gráfico de pareto
    fig = go.Figure([go.Bar(x=tramo_via.index, y=tramo_via['ACCIDENTES'], yaxis='y1', name='sessions id'),
                     go.Scatter(x=tramo_via.index, y=tramo_via['porcentaje'], yaxis='y2', name='accidentes de transito', hovertemplate='%{y:.1%}', marker={'color': '#000000'})])
    # Agregar detalles
    fig.update_layout(template='plotly_white', showlegend=False, hovermode='x', bargap=.3,
                      title={'text': '<b>Pareto accidentes de transito por diseño de la Via<b>', 'x': .5}, 
                      yaxis={'title': 'Accidentes'},
                      yaxis2={'rangemode': "tozero", 'overlaying': 'y', 'position': 1, 'side': 'right', 'title': 'Porcentaje', 'tickvals': np.arange(0, 1.1, .2), 'tickmode': 'array', 'ticktext': [str(i) + '%' for i in range(0, 101, 20)]})
    
    
    # Enviar gráfica a streamlit
    c3.plotly_chart(fig)
    ##Se crea checkbox para visualizar dataframe
    if c3.checkbox('Visualizar tabla de cantidad accidentes según el diseño de la vía', False):
        c3.write(tramo_via)

#-----------------------------------------------------------------------------------------
  
##Medellín-Envigado   

f1, f2 = st.columns((1,1))
f1.markdown("<h3 style='text-align: left; color: blue;'> Medellín-Envigado </h3>", unsafe_allow_html=True)
## Se agregan espacios para bajar gráfica
f1.markdown("<h3 style='text-align: left; color: blue;'>  </h3>", unsafe_allow_html=True)
f1.markdown("<h3 style='text-align: left; color: blue;'>  </h3>", unsafe_allow_html=True)
f1.markdown("<h3 style='text-align: left; color: blue;'>  </h3>", unsafe_allow_html=True)
f1.markdown("<h3 style='text-align: left; color: blue;'>  </h3>", unsafe_allow_html=True)

##Se saca el mes de la columna fecha
bodega['MES']=bodega['FECHA'].dt.strftime('%m')
bodeguita2=bodega.groupby(['MES'])[['ENVIGADO','MEDELLIN']].sum().reset_index()
bodeguita2['ENVIGADO']=bodeguita2['ENVIGADO'].astype(int)
bodeguita2['MEDELLIN']=bodeguita2['MEDELLIN'].astype(int)

# Definir gráfica
fig = px.line(bodeguita2, x='MES', y =['ENVIGADO','MEDELLIN'], title = '<b>Evolución de accidentes en Medellín y Envigado<b>',
              color_discrete_sequence=px.colors.qualitative.G10)

# Agregar detalles
fig.update_layout(
    template = 'plotly_dark',
    title_x = 0.5,
    xaxis_title = '<b>Mes<b>',
    yaxis_title = '<b>cantidad arrestos<b>',
)

f1.plotly_chart(fig)

##Se crea checkbox para visualizar dataframe
if f1.checkbox('Visualizar tabla de la evolución accidentes', False):
    f1.write(bodeguita2)
    
##-------------------------------------------------------------------

##PALMIRA Y ENVIGADO

f2.markdown("<h3 style='text-align: left; color: blue;'> Palmira-Envigado </h3>", unsafe_allow_html=True)
indicadorpalenv = f2.selectbox('SELECCIONE UNA OPCIÓN', ['Accidentes según el tipo de vehículo',  'Accidentes según el tipo de zona' ],
                            format_func=lambda x: 'Seleccione una opción' if x == '' else x)
if indicadorpalenv =='Accidentes según el tipo de vehículo':
    #¿CÚAL ES LA CANTIDAD DE ACCIDENTES SEGÚN LA CLASE DE VEHICULO EN LAS CIUDADES PALMIRA Y ENVIGADO?
    #Se crea dataframe de clase de vehículo y se cuentan con la columna radicado, además se organiza en forma descendente
    clase_vehiculoe=df8.groupby(['CLASE DE VEHICULO'])[['RADICADO']].count().reset_index().sort_values('RADICADO', ascending = False)
    clase_vehiculoe['CLASE DE VEHICULO']=clase_vehiculoe['CLASE DE VEHICULO'].str.upper() #se convierte la columna de clase de vehículo en MAYÚSCULA
    
    #Se renombras algunas categorías de la columna clase de vehículo de la base de datos de Palmira para que queden igual a la columna de clase de vehiculo de envigado
    df7['CLASE VEHICULO']=df7['CLASE VEHICULO'].replace({'MOTO':'MOTOCICLETA','TRACTO CAMION':'TRACTOCAMION','CICLISTA':'BICICLETA','MAQUINARIA':'NO APLICA'})
    
    #Se crea dataframe de clase de vehículo y se cuentan con la columna jornada, además se organiza en forma descendente
    clase_vehiculop=df7.groupby(['CLASE VEHICULO'])[['JORNADA']].count().reset_index().sort_values('JORNADA', ascending = False)
    clase_vehiculop=clase_vehiculop.rename(columns ={'CLASE VEHICULO':'CLASE DE VEHICULO'}) #se renombra la columna
    
    #Se concatenan por clase de vehículo
    clasevehiculos=pd.merge(clase_vehiculop,clase_vehiculoe, on=['CLASE DE VEHICULO'], how='outer').rename(columns ={'JORNADA':'PALMIRA','RADICADO':'ENVIGADO'})
    clasevehiculos= clasevehiculos.fillna(0) #se rellenan los nulos con ceros
    clasevehiculos['ENVIGADO']= clasevehiculos['ENVIGADO'].astype(int)
    clasevehiculos['TOTAL']=clasevehiculos['PALMIRA']+clasevehiculos['ENVIGADO'] #se crea una columna nueva
    clasevehiculos=clasevehiculos.sort_values('TOTAL', ascending = False) #se orden los datos de manera descendente de acuerdo a la columna TOTAL
    
    # Crear gráfica
    fig = px.bar(clasevehiculos, x='CLASE DE VEHICULO', y=['TOTAL'], title ='<b>Accidentes según el tipo de Vehículo<b>')
    
    # Agregar detalles a la gráfica
    fig.update_layout(
        xaxis_title = 'TIPO DE VEHÍCULO',
        yaxis_title = 'ACCIDENTES',
        template = 'simple_white',
        legend_title = '<b>Cantidad<b>',
        title_x = 0.5)
    
    # Enviar gráfica a streamlit
    f2.plotly_chart(fig)
    ##Se crea checkbox para visualizar dataframe
    if f2.checkbox('Visualizar tabla de accidentes según la clase de vehículo', False):
        f2.write(clasevehiculos)

elif indicadorpalenv ==  'Accidentes según el tipo de zona':
#¿CÚAL ES LA CANTIDAD DE ACCIDENTES SEGUN EL TIPO DE ZONA (COMUNA)? TOMANDO SOLO PALMIRA Y ENVIGADO

#se crea dataframe de palmira con fecha, zona y se cuenta con jornada
    zona_palmira=df7.groupby(['FECHA','ZONA'])[['JORNADA']].count().reset_index().rename(columns ={'JORNADA':'PALMIRA'})
    df8=df8.rename(columns ={'AREA':'ZONA'}) #se renombra el nombre de AREA
    df8['ZONA']=df8['ZONA'].str.upper() #se convierten todos los datos de la columna ZONA en MAYUSCULA
    zona_envigado=df8.groupby(['FECHA','ZONA'])[['RADICADO']].count().reset_index().rename(columns ={'RADICADO':'ENVIGADO'})
    zonas=pd.merge(zona_palmira,zona_envigado, on=['FECHA','ZONA'], how='outer')
    zonas = zonas.fillna(0.0) 
    zonas1 = zonas.groupby(['ZONA'])[['PALMIRA','ENVIGADO']].sum().reset_index()
    # Definir gráfica
    fig = px.bar(zonas1, x='ZONA', y=['PALMIRA','ENVIGADO'], barmode= 'group', title ='<b>Accidentes segun el tipo de zona<b>',
                color_discrete_sequence=["#ffdd88", "#88dd44"])

    px.bar()
    
    # Agregar detalles a la gráfica
    fig.update_layout(
        xaxis_title = 'Tipo de zona',
        yaxis_title = 'Cantidad de Accidentes',
        template = 'simple_white',
        title_x = 0.5,
        legend_title = '<b>Ciudades<b>')


# Enviar gráfica a streamlit
    f2.plotly_chart(fig)
    ##Se crea checkbox para visualizar dataframe
    if f2.checkbox('Visualizar tabla de accidentes según el tipo de zona', False):
        f2.write(zonas1)

#-----------------------------------------------------------------------------------------
    
##Las 3 ciudades
st.markdown("<h1 style='text-align: center; color: blue;'>Palmira, Medellín y Envigado </h1>", unsafe_allow_html=True)
mess = st.slider('Mes en el que se presentaron accidentes', 1, 12)
   
m1, m2, m3 = st.columns((1,1,1))
#¿CÚAL ES LA CANTIDAD DE ACCIDENTES SEGÚN EL TIPO DE GRAVEDAD EN LAS 3 CIUDADES?
# se crea un datafrime nuevo igual a bodega pero  sin la fecha
HOLA = bodega.groupby([bodega['FECHA'].dt.month, 'GRAVEDAD'])[['PALMIRA','ENVIGADO','MEDELLIN']].sum().reset_index().rename(columns ={'FECHA':'MES'})
HOLA['ENVIGADO']=HOLA['ENVIGADO'].astype(int)
HOLA['MEDELLIN']=HOLA['MEDELLIN'].astype(int)
HOLA['PALMIRA']=HOLA['PALMIRA'].astype(int)

#Definir gráfica

fig = px.bar(HOLA[HOLA['MES']==mess], x='GRAVEDAD', y=['PALMIRA','ENVIGADO','MEDELLIN'], barmode= 'group', title ='<b>Accidentes según el tipo de gravedad<b>',
             width=580, height=450)
    
px.bar()

#Agregar detalles a la gráfica
fig.update_layout(
    xaxis_title = 'Tipo de Gravedad',
    yaxis_title = 'Cantidad de Accidentes',
    template = 'simple_white',
    title_x = 0.5,
    legend_title = '<b>Ciudades<b>')

# Enviar gráfica a streamlit
m1.plotly_chart(fig)

##Se crea checkbox para visualizar dataframe
if m1.checkbox('Visualizar tabla de accidentes en las tres ciudades según el tipo de gravedad', False):
    m1.write(HOLA)

#---------------------------------------------------------------------------
##las 3 ciudades

#¿QUÉ DÍA DE LA SEMANA SE ACCIDENTAN MAS LAS PERSONAS EN LAS TRES CIUDADES?
#se agrega una columna llamada día semana a la bodega usando la función strftime('%a') para extraer el nombre del dia de la semana de la columna fecha
bodega['DIA SEMANA']=bodega['FECHA'].dt.strftime('%a')

#Se crea un dataframe con dia semana y se cuenta con gravedad, se organiza de forma descendente
bodeguita=bodega.groupby([bodega['FECHA'].dt.month,'DIA SEMANA'])[['ENVIGADO','PALMIRA','MEDELLIN']].sum().reset_index().rename(columns ={'FECHA':'MES'})
bodeguita['ENVIGADO']=bodeguita['ENVIGADO'].astype(int)
bodeguita['MEDELLIN']=bodeguita['MEDELLIN'].astype(int)
bodeguita['PALMIRA']=bodeguita['PALMIRA'].astype(int)

dic={'Mon':'1','Tue':'2','Wed':'3','Thu':'4','Fri':'5','Sat':'6','Sun':'7'}
bodeguita['DIA SEMANA']=bodeguita['DIA SEMANA'].replace(dic)
bodeguita=bodeguita.sort_values('DIA SEMANA',ascending=True)

##Se hace un diccionario para ordenar los días de lunes a domingo
dic={'1':'Mon','2':'Tue','3':'Wed','4':'Thu','5':'Fri','6':'Sat','7':'Sun'}
bodeguita['DIA SEMANA']=bodeguita['DIA SEMANA'].replace(dic)

# Crear gráfica
fig = px.bar(bodeguita[bodeguita['MES']==mess], x='DIA SEMANA', y=['ENVIGADO','PALMIRA','MEDELLIN'], barmode= 'group', title ='<b>Cantidad de accidentes según el Día de la Semana<b>',
             width=580, height=450)

# Agregar detalles a la gráfica
fig.update_layout(
    xaxis_title = 'Accidentes',
    yaxis_title = 'Día de la semana',
    legend_title = 'Suma 3 ciudades',
    template = 'simple_white',

    title_x = 0.5)

# Enviar gráfica a streamlit
m2.plotly_chart(fig)

##Se crea checkbox para visualizar dataframe
if m2.checkbox('Visualizar tabla de accidentes en las tres ciudades según el día de la semana', False):
    m2.write(bodeguita)
    
#---------------------------------------------------------
### LAS 3 CIUDADES
#¿CÚAL ES EL PORCENTAJE DE ACCIDENTES QUE HAY EN LAS TRES CIUDADES DEPENDIENDO DE LA CLASE DEL ACCIDENTE?

total=bodega.groupby([bodega['FECHA'].dt.month,'CLASE_ACCIDENTE'])[['GRAVEDAD']].count().reset_index().rename(columns ={'GRAVEDAD':'CANTIDAD','FECHA':'MES'})

#Se realiza el grafico de dataframe total
fig = px.pie(total[total['MES']==mess] , values = 'CANTIDAD', names = 'CLASE_ACCIDENTE', title = '<b>% Accidentes según el tipo de accidente<b>',
             width=580, height=450)

# Agregar detalles a la gráfica
fig.update_layout(
    template = 'simple_white',
    legend_title = 'Clase de Accidente',
    title_x = 0.5)

# Enviar gráfica a streamlit
m3.plotly_chart(fig)

##Se crea checkbox para visualizar dataframe
if m3.checkbox('Visualizar tabla de accidentes en las tres ciudades según la clase de accidente', False):
    m3.write(total)

#------------------------------------------------------------------
## Agregar espacio 
st.markdown("<h3 style='text-align: left; color: blue;'>  </h3>", unsafe_allow_html=True)
## Descargar bases de datos
st.markdown(get_table_download_link(df7), unsafe_allow_html=True)

st.markdown(get_table_download_Envigado(df8), unsafe_allow_html=True)

st.markdown(get_table_download_Medellin(df9), unsafe_allow_html=True)








