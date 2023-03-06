import pandas as pd
import numpy as np
#from janitor import xlsx_table
#from openpyxl import load_workbook
#from openpyxl.utils.dataframe import dataframe_to_rows
import glob
import os
#import regex


def alimentar_base(arquivos, df_base):
  
  '''Essa função cria um novo dataframe concatenando todos os dataframes
   que encontrar nas planilhas dentro do diretório especificado. 
   Na prática, ela vai em cada workbook e passa pelas planilhas,
   recolhe os dados das tabelas e joga pros locais específicos na
   planilha de benchmark. Ela retorna uma tabela com a união dos
   valores antigos e novos.
   
   Ela só funciona se não existir nenhum arquivo que contenha o nome
   "Benchmark" dentro do diretório das planilhas de monitoramento. Fiz 
   isso pra que uma vez feito o processo (e exportada uma planilha de benchmark)
   ele não seja refeito novamente (por algum motivo) e acabe concatenando novamente
   os mesmos dados'''

  global df_benchmark_final
  d = pd.DataFrame()

  print(arquivos)

  if any('Benchmark_' in itens for itens in arquivos):
    mensagem = 'Já existe uma planilha de Benchmark_ no diretório. Favor verificar se não é a versão final'
    print(mensagem)
    return mensagem

  else:
    for idx, workbook in enumerate(arquivos):
      print("Inserindo novos dados na base... Atualmente coletando dados do arquivo {}: '{}''.".format(idx+1, workbook))

      df_m_geral = xlsx_table(workbook, sheetname='GERAL', table='GERAL')
      df_m_ocupacao = xlsx_table(workbook, sheetname='OCUPAÇÃO', table='OCUPAÇÃO')
      df_m_agua = xlsx_table(workbook, sheetname='ÁGUA', table='ÁGUA')
      df_m_energia = xlsx_table(workbook, sheetname='ENERGIA', table='ENERGIA')
      df_m_residuos = xlsx_table(workbook, sheetname='RESÍDUOS', table='RESÍDUOS')
      df_m_ar = xlsx_table(workbook, sheetname='QUALIDADE DO AR', table='QUALIDADEDOAR') 

      #Idealmente o concat deveria sozinho concaternar todas as iterações mas, por algum motivo, está iterando apenas a última. Pos isso usei o append pra iterar... Vou descobrir o porquê disso e utilizar apenas o concat
      d = d.append([df_m_geral, df_m_ocupacao,df_m_agua, df_m_energia, df_m_residuos, df_m_ar])

     
    df_benchmark_final = pd.concat([df_base, d], axis=0).drop_duplicates().reset_index(drop=True)
    print('Concluído.')
  return df_benchmark_final
  
def preencher_nulos(benchmark):

  benchmark[['Cidade', 'UF', 'FTE', 'Tipologia', 'Certificação', 'Nível', 'Área construída [m²]',
              'HVAC', 'Torre de resfriamento', 'Pavimento', 'Torre']] = benchmark[['Cidade', 'UF', 'FTE','Tipologia', 'Certificação', 'Nível', 'Área construída [m²]',
                                                                                   'HVAC', 'Torre de resfriamento', 'Pavimento', 'Torre']].fillna(method='ffill')
  

  
  return benchmark

def calcular_indice_por_ocupacao(benchmark):
    #benchmark['Litros_por_ocupante'] = (benchmark['Consumo [m³]']*1000)/benchmark['FTE']
    #benchmark['kWh_por_ocupante'] = (benchmark['Consumo [kWh]'])/benchmark['FTE']
    #print(benchmark['Classificação'].value_counts())
    benchmark['Kg_Nao_Reciclavel'] = (benchmark["Geração [kg]"]).where(benchmark['Classificação'] == 'Não Reciclável')
    benchmark['Kg_Reciclavel'] = (benchmark['Geração [kg]']).where(benchmark['Classificação'] == 'Reciclável')
        #benchmark['Kg_Nao_Reciclavel_por_ocupante'] = np.where(benchmark['Classificação'] == 'Não Reciclável', (benchmark['Geração [kg]']/benchmark['FTE']), np.nan)
    #benchmark['Geração [kg]']/benchmark['FTE'] if benchmark.query("Classificação == 'Não Reciclável'") == True else  np.nan
    #benchmark['Kg_Reciclavel_por_ocupante'] = (benchmark['Geração [kg]'])/benchmark['FTE'] if (benchmark.query("Classificação == 'Reciclável'")) == True else np.nan
    return benchmark

def salvar_arquivo (dataframe):
  revisao = input("Insira mês e ano do benchmark, separados por um underline, exemplo: '10_22'")
  nome = '\Benchmark_{}.xlsx'.format(revisao)

  caminho = diretorio+nome

  dataframe.to_excel(caminho) 
  print('salvo em ' + caminho) 
     