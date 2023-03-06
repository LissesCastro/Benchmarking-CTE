#IMPORTANDO AS BIBLIOTECAS UTILIZADAS NO PROJETO

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import matplotlib.pyplot as plt
import seaborn as sns 

#st.sidebar.header(':green[Teste]')

#HEADER E UPLOADER DO ARQUIVO CSV DE BENCHMARKING
st.title(":green[Visualização de dados de Benchmarking - O+M CTE]")
st.subheader("Para começar, selecione o arquivo com os dados de benchmarking")
csv_file = st.file_uploader('Selecione o arquivo :green[.csv] da planilha de benchmarking', type='csv')

#INDICAÇÃO DAS VARIÁVEIS QUE APARECERÃO NOS DROPDOWNS UTILIZADOS NO PROJETO. VARIÁVEIS ÍNDICE SÃO NUMÉRICAS E
#VARIÁVEIS SEPARADORES SÃO CATEGÓRICAS
variaveis_indice = ['Área construída [m²]', 'FTE', 'Consumo [m³]', 'Água_Custo[R$]', 
                        'Consumo [kWh]', 'Demanda [kW]', 'Geração [kg]', 'Medição CO2 [ppm]', 
                        'Medição TVOC  [µg/m³]', 'Kg_Nao_Reciclavel', 'Kg_Reciclavel', 
                        'kWh/habitante/dia', 'litros/habitante/dia', 'residuos/habitante/dia']

variaveis_separador = ['Projeto', 'Cidade', 'UF', 'Tipologia', 'HVAC', 'Torre de resfriamento', 'ETE', 
                       'Nível', 'Fonte', 'Fornecedor - Mercado livre', 'Ano_Benchmarking']

#O IF NESSE CASO É USADO COMO CONDICIONARL PARA QUE O BENCHMARKING SÓ APAREÇA APÓS UPLOAD DO ARQUIVO
if csv_file is not None:
    df = pd.read_csv(csv_file, encoding='latin-1', delimiter=';', decimal=',') 

    #check_salvalus = st.checkbox('Remover Salvalus?')
    #if check_salvalus == True:
    #    df.drop(df[df['Projeto'] == 'Hospital Salvalus'].index, inplace = True)

    df['Ano_Benchmarking'] = df['Ano_Benchmarking'].astype('string')
    df['kWh/habitante/dia'] = df['Consumo [kWh]']/df['FTE']/22
    df['litros/habitante/dia'] = (df['Consumo [m³]']*1000)/df['FTE']/22
    df['residuos/habitante/dia'] = df['Geração [kg]']/df['FTE']/22

    #HEADER FALANDO DO NÚMERO DE PROJETOS
    st.header('O benchmarking possui :green[{}] projetos diferentes'.format(df['Projeto'].nunique()+1))
    st.write('Abaixo a planilha contendo todos os dados')
    st.write(df)

    projetos = df['Projeto'].unique()
    df_agrupada = df.groupby(['Projeto', 'Cidade', 'UF', 'Tipologia', 'Ano_Benchmarking']).mean().reset_index().round(2)
    df_agrupada_ano = df_agrupada.groupby('Ano_Benchmarking').count().reset_index()

    #st.write(df_agrupada['Consumo [m³]'].value_counts())
    st.write('#')
    st.write('#')
    st.title('Visão Geral')


    fig = px.bar(df_agrupada_ano, x='Ano_Benchmarking', y='Projeto')
    fig.update_layout(title='Projetos realizados por ano', title_x = 0.33)
    fig.update_traces(marker_color='#21F1A2')
    st.plotly_chart(fig)

    st.subheader('Selecione uma variável numérica e uma variável categórica para entender a distribuição dos empreendimentos por categoria')
    st.caption('Os valores dizem respeito às :green[médias] das variáveis numéricas selecionadas. As variáveis de dia consideram :green[22 dias úteis]')

 

    #SELEÇÃO DOS DA VARIÁVEL E SEPARADOR
    col1, col2= st.columns(2)    
    with col1:
        indice_1 = st.selectbox('**Selecione uma variável**', variaveis_indice)
    with col2:
        separador_1 = st.selectbox('**Selecione um separador**', variaveis_separador)
 
    #SELEÇÃO DA OPÇÃO DE LIMITAR AO PERCENTIL
    checkbox_percentil = st.checkbox('Remover dados extremos? (1% maiores)')


    #ESSE TRECHO MONTA O GRÁFICO DA DISTRIBUIÇÃO POR VARIÁVEL E SEPARADOR. TAMBÉM FAZ O PRIMEIRO QUARTIL, A MÉDIA E O TERCEIRO QUARTIL
    if indice_1 and separador_1 is not None:

        df_separada = df.groupby([separador_1]).mean().reset_index().round(2)

        #COLOCAR LIMITES NOS DADOS DEPENDENDO DOS QUARTIS
        perc_99 = df_separada[indice_1].quantile(0.95)
        if checkbox_percentil == True:
            df_separada = df_separada[df_separada[indice_1] < perc_99]

        col_1, col_2, col_3 = st.columns(3)   
        col_1.metric("25%: ", df_separada[indice_1].quantile(0.25).round(2))
        col_2.metric("Média: ", df_separada[indice_1].mean().round(2))
        col_3.metric("75%: ", df_separada[indice_1].quantile(0.75).round(2))

        fig_filtro = px.bar(df_separada,x=separador_1, y=indice_1, text=indice_1)
        fig_filtro.add_hline(y=df_separada[indice_1].mean(), line_color='red', line_dash='dash')
        fig_filtro.add_hline(y=df_separada[indice_1].quantile(0.25), line_color='purple', line_dash='dash')
        fig_filtro.add_hline(y=df_separada[indice_1].quantile(0.75), line_color='purple', line_dash='dash')
        fig_filtro.update_traces(marker_color='#21F1A2')
        fig_filtro.update_layout(title='Relação de {} por {}'.format(indice_1, separador_1), title_x = 0.29)
        st.plotly_chart(fig_filtro)


    st.write('#')
    st.write('#')
    st.title('Comparação entre projetos')
    st.subheader('Selecione os projetos desejados e análise as diferenças entre eles a partir da variável selecionada.')
    #FAZ O SELECIONADOR DE VÁRIOS PROJETOS
    selecao = st.multiselect("Escolha os projetos", df_agrupada['Projeto'].unique())
    projetos_selecionados = selecao 
    indice = st.selectbox('**Selecione um índice**', variaveis_indice)
    #PLOTA OS GRÁFICOS DOS PROJETOS SELECIONADOS PARA A VARIÁVEL ESCOLHIDA
    if selecao is not None:
        df_filtro = df_agrupada[df_agrupada['Projeto'].isin(selecao)]
        fig_filtro = px.bar(df_filtro,x='Projeto', y=indice, text=indice)
        fig_filtro.add_hline(y=df_agrupada[indice].mean(), line_color='red', line_dash='dash')
        fig_filtro.add_hline(y=df_agrupada[indice].quantile(0.25), line_color='purple', line_dash='dash')
        fig_filtro.add_hline(y=df_agrupada[indice].quantile(0.75), line_color='purple', line_dash='dash')
        fig_filtro.update_traces(marker_color='#21F1A2')
        fig_filtro.update_layout(title='Comparação entre projetos selecionados', title_x = 0.33)
        st.plotly_chart(fig_filtro)
    
    
    #O SELECIONADOR ESCOLHE O PROJETO E FILTRA AS BASES A PARTIR DESSES. SE O CHECKLIST DE TIPOLOGIA FOR UTILIZADO
    #ENTÃO A COMPARAÇÃO OCORRE COM UM DATAFRAME QUE CONTEM APENAS AS LINHAS CUJO A TIPOLOGIA EQUIVALE A DO PROJETO SELECIONADO
    st.write('#')
    st.write('#')
    st.title('Performance de projeto')
    st.subheader('Selecione um projeto e verifique a performance dele em comparação à média de todos os projetos da base do cte ou apenas dos projetos com mesma tipologia')

    prj_unico = st.selectbox('**Escolha um projeto**', projetos, key=2)
    df_filtro_unico = df_agrupada[df_agrupada['Projeto'] == prj_unico]
    st.write(df_filtro_unico.shape)
    prj_unico_tipologia = df_filtro_unico.iloc[0]['Tipologia']
    df_tipologia_igual = df_agrupada[df_agrupada['Tipologia'] == prj_unico_tipologia]
    check_tipologia = st.checkbox('Comparar apenas com mesma tipologia')

    #PLOTA AS MÉTRICAS A PARTIR DA COMPARAÇÃO PERCENTUAL COM OS VALORES DAS BASES ORIGINAIS

    if prj_unico is not None:
        col_1_a, col_1_b, col_1_c, col_1_d = st.columns(4)
        if check_tipologia == True:
            col_1_a.metric(label='FTE', value=df_filtro_unico['FTE'], delta='{}%'.format(round(((df_filtro_unico['FTE'].mean() - df_tipologia_igual['FTE'].mean())/df_tipologia_igual['FTE'].mean())*100, 2)))
            col_1_b.metric(label='kWh/habitante/dia', value=df_filtro_unico['kWh/habitante/dia'], delta='{}%'.format(round(((df_filtro_unico['kWh/habitante/dia'].mean() - df_tipologia_igual['kWh/habitante/dia'].mean())/df_tipologia_igual['kWh/habitante/dia'].mean())*100, 2)), delta_color="inverse")
            col_1_c.metric(label='litros/habitante/dia', value=df_filtro_unico['litros/habitante/dia'], delta='{}%'.format(round(((df_filtro_unico['litros/habitante/dia'].mean() - df_tipologia_igual['litros/habitante/dia'].mean())/df_tipologia_igual['litros/habitante/dia'].mean())*100, 2)), delta_color="inverse")
            col_1_d.metric(label='residuos/habitante/dia', value=df_filtro_unico['residuos/habitante/dia'], delta='{}%'.format(round(((df_filtro_unico['residuos/habitante/dia'].mean() - df_tipologia_igual['residuos/habitante/dia'].mean())/df_tipologia_igual['residuos/habitante/dia'].mean())*100, 2)), delta_color="inverse")
        else:
            col_1_a.metric(label='FTE', value=df_filtro_unico['FTE'], delta='{}%'.format(round(((df_filtro_unico['FTE'].mean() - df_agrupada['FTE'].mean())/df_agrupada['FTE'].mean())*100, 2)))
            col_1_b.metric(label='kWh/habitante/dia', value=df_filtro_unico['kWh/habitante/dia'], delta='{}%'.format(round(((df_filtro_unico['kWh/habitante/dia'].mean() - df_agrupada['kWh/habitante/dia'].mean())/df_agrupada['kWh/habitante/dia'].mean())*100, 2)), delta_color="inverse")
            col_1_c.metric(label='litros/habitante/dia', value=df_filtro_unico['litros/habitante/dia'], delta='{}%'.format(round(((df_filtro_unico['litros/habitante/dia'].mean() - df_agrupada['litros/habitante/dia'].mean())/df_agrupada['litros/habitante/dia'].mean())*100, 2)), delta_color="inverse")
            col_1_d.metric(label='residuos/habitante/dia', value=df_filtro_unico['residuos/habitante/dia'], delta='{}%'.format(round(((df_filtro_unico['residuos/habitante/dia'].mean() - df_agrupada['residuos/habitante/dia'].mean())/df_agrupada['residuos/habitante/dia'].mean())*100, 2)), delta_color="inverse")
    
    #HISTOGRAMAS
    st.write('#')
    st.write('#')
    st.title('Histogramas das variáveis')
    st.subheader('Selecione uma variável para entender a dispersão de seus valores entre todos os projetos da base')
    indice_3 = st.selectbox('**Selecione uma variável**', variaveis_indice, key=3)
    if indice_3 is not None:
        fig_hist = px.histogram(x=df_agrupada[indice_3], nbins=35, hover_name=df_agrupada['Projeto'])
        fig_hist.update_traces(marker_color='#21F1A2')
        fig_hist.update_layout(title='{}: Distribuição ao longo dos projetos'.format(indice_3), title_x = 0.33)
        st.plotly_chart(fig_hist)

    #SCATTERPLOTS
    st.write('#')
    st.write('#')
    st.title('Relação entre variáveis numéricas')
    st.subheader('Selecione duas variáveis numéricas para entender a relação de dispersão entre elas')
    col_2_a, col_2_b = st.columns(2)
    with col_2_a:    
        indice_4 = st.selectbox('**Selecione uma variável**', variaveis_indice, key=4)
    with col_2_b:
        indice_5 = st.selectbox('**Selecione uma variável**', variaveis_indice, key=5)

    fig = px.scatter(x=df_agrupada[indice_4], y=df_agrupada[indice_5], hover_name=df_agrupada['Projeto'])
    fig.update_traces(marker=dict(size=12))
    fig.update_traces(marker_color='#21F1A2')
    fig.update_layout(title='Relação de crescimento entre {} e {}'.format(indice_4, indice_5), title_x = 0.2)
    st.plotly_chart(fig)