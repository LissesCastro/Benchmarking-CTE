import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

st.title(":green[Visualização de dados de Benchmarking - O+M CTE]")
st.subheader("Para começar, selecione o arquivo com os dados de benchmarking")
csv_file = st.file_uploader('Selecione o arquivo :green[.csv] da planilha de benchmarking', type='csv')

variaveis_indice = ['Área construída [m²]', 'FTE', 'Consumo [m³]', 'Água_Custo[R$]', 
                        'Consumo [kWh]', 'Demanda [kW]', 'Geração [kg]', 'Medição CO2 [ppm]', 
                        'Medição TVOC  [µg/m³]', 'Kg_Nao_Reciclavel', 'Kg_Reciclavel', 'kWh/habitante/dia', 
                        'litros/habitante/dia', 'residuos/habitante/dia']

variaveis_separador = ['Projeto', 'Cidade', 'UF', 'Tipologia', 'HVAC', 'Torre de resfriamento', 'ETE', 
                       'Nível', 'Fonte', 'Fornecedor - Mercado livre']

if csv_file is not None:
    df = pd.read_csv(csv_file, encoding='latin-1', delimiter=';', decimal=',')

    for var in ['Consumo [m³]', 'Consumo [kWh]', 'Geração [kg]', 'Kg_Nao_Reciclavel', 'Kg_Reciclavel']:
        mean_values = df.groupby('Projeto')[var].mean()
        df[var] = df.apply(lambda x: x[var] if not pd.isna(x[var]) else mean_values[x['Projeto']], axis=1)

    for var in ['Geração [kg]']:
        sum_values = df.groupby('Projeto')[var].sum()
        df[var+'_total'] = df.groupby('Projeto')[var].transform('sum')

    df['kWh/habitante/dia'] = df['Consumo [kWh]']/df['FTE']/22
    df['litros/habitante/dia'] = (df['Consumo [m³]']*1000)/df['FTE']/22
    df['residuos/habitante/dia'] = df['Geração [kg]_total']/df['FTE']/22

    st.header('O benchmarking possui :green[{}] projetos diferentes'.format(df['Projeto'].nunique()))
    st.write('Abaixo a planilha contendo todos os dados')
    st.write(df)

    projetos = df['Projeto'].unique()
    df_agrupada = df.groupby(['Projeto']).mean().reset_index().round(2)
    df_somas = df.groupby(['Projeto']).sum().reset_index().round(2)

    st.write('#')
    st.write('#')
    st.title(':green[Visão Geral]')
    st.subheader('Selecione uma variável numérica e uma variável categórica para entender a distribuição dos empreendimentos por categoria')
    st.caption('Os valores dizem respeito às :green[médias] das variáveis numéricas selecionadas, a variável "resíduos/habitantes/dia considera a média de toda a geração durante o período de monitoramento. As variáveis de dia consideram :green[22 dias úteis]')


    col1, col2= st.columns(2)    
    with col1:
        indice_1 = st.selectbox('**Selecione uma variável**', variaveis_indice)
    with col2:
        separador_1 = st.selectbox('**Selecione um separador**', variaveis_separador)
    
    if indice_1 and separador_1 is not None:

        df_separada = df.groupby([separador_1]).mean().reset_index().round(2)

        col_1, col_2, col_3 = st.columns(3)   
        col_1.metric("Média: ", df_separada[indice_1].mean().round(2))
        col_2.metric("25%: ", df_separada[indice_1].quantile(0.25).round(2))
        col_3.metric("75%: ", df_separada[indice_1].quantile(0.75).round(2))

        fig_filtro = px.bar(df_separada,x=separador_1, y=indice_1, text=indice_1)
        fig_filtro.add_hline(y=df_separada[indice_1].mean(), line_color='red', line_dash='dash')
        fig_filtro.add_hline(y=df_separada[indice_1].quantile(0.25), line_color='purple', line_dash='dash')
        fig_filtro.add_hline(y=df_separada[indice_1].quantile(0.75), line_color='purple', line_dash='dash')
        fig_filtro.update_traces(marker_color='#21F1A2')
        st.plotly_chart(fig_filtro)


    st.write('#')
    st.write('#')
    st.title('Comparação entre projetos')
    col1, col2 = st.columns(2)
    with col1:
        projeto_1 = st.selectbox('**Escolha um projeto**', projetos)
    with col2:    
        projeto_2 = st.selectbox('**Escolha outro projeto para comparação**', projetos)
    projetos_selecionados = [projeto_1, projeto_2]
    indice = st.selectbox('**Selecione um índice**', variaveis_indice)


    if projeto_1 and projeto_2 is not None:

            df_filtro = df_agrupada[df_agrupada['Projeto'].isin(projetos_selecionados)]
            fig_filtro = px.bar(df_filtro,x='Projeto', y=indice, text=indice)
            fig_filtro.add_hline(y=df_agrupada[indice].mean(), line_color='red', line_dash='dash')
            fig_filtro.add_hline(y=df_agrupada[indice].quantile(0.25), line_color='purple', line_dash='dash')
            fig_filtro.add_hline(y=df_agrupada[indice].quantile(0.75), line_color='purple', line_dash='dash')
            fig_filtro.update_traces(marker_color='#21F1A2')
            st.plotly_chart(fig_filtro)

    prj_unico = st.selectbox('**Escolha um projeto**', projetos, key=2)

    if prj_unico is not None:
        df_filtro_unico = df_agrupada[df_agrupada['Projeto'] == prj_unico]

        col_1_a, col_1_b, col_1_c, col_1_d = st.columns(4)
        col_1_a.metric(label='FTE', value=df_filtro_unico['FTE'], delta='{}%'.format(round(((df_filtro_unico['FTE'].mean() - df_agrupada['FTE'].mean())/df_agrupada['FTE'].mean())*100, 2)))
        col_1_b.metric(label='kWh/habitante/dia', value=df_filtro_unico['kWh/habitante/dia'], delta='{}%'.format(round(((df_filtro_unico['kWh/habitante/dia'].mean() - df_agrupada['kWh/habitante/dia'].mean())/df_agrupada['kWh/habitante/dia'].mean())*100, 2)), delta_color="inverse")
        col_1_c.metric(label='litros/habitante/dia', value=df_filtro_unico['litros/habitante/dia'], delta='{}%'.format(round(((df_filtro_unico['litros/habitante/dia'].mean() - df_agrupada['litros/habitante/dia'].mean())/df_agrupada['litros/habitante/dia'].mean())*100, 2)), delta_color="inverse")
        col_1_d.metric(label='residuos/habitante/dia', value=df_filtro_unico['residuos/habitante/dia'], delta='{}%'.format(round(((df_filtro_unico['residuos/habitante/dia'].mean() - df_agrupada['residuos/habitante/dia'].mean())/df_agrupada['residuos/habitante/dia'].mean())*100, 2)), delta_color="inverse")