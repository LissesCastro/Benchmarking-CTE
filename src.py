import pandas as pd
import numpy as np
from janitor import xlsx_table
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows

import glob
import os
import regex
import benchmarking_functions as bf

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd 
from tkinter.messagebox import showinfo

#root = tk.Tk()
#root.title('Alimentador de Benchmarking')
#root.resizable(False, False)
#root.geometry('500x500')
#filename = fd.askopenfilename()

def alimentar_base(arquivos, df_base):
    
  global df_benchmark_final
  '''df_m_geral = pd.DataFrame()
  df_m_ocupacao = pd.DataFrame()
  df_m_agua = pd.DataFrame()
  df_m_energia = pd.DataFrame()
  df_m_residuos = pd.DataFrame()
  df_m_ar = pd.DataFrame()'''
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

def selecionar_arquivo ():
    global df_base
    dir_bi_base = fd.askopenfilename(title= 'Escolha o arquivo de excel')
    showinfo(title='Arquivo selecionado', message=dir_bi_base)
    wb = load_workbook(dir_bi_base)
    print(wb.worksheets)
    ws = wb['Benchmark']
    df_base = xlsx_table(dir_bi_base, sheetname = 'Benchmark', table='BENCHMARK')
    print(df_base.columns)
    return ws, df_base

def selecionar_diretorio():
    global arquivos_lista
    global diretorio
    diretorio = fd.askdirectory(title='Insira o diretório com os arquivos de monitoramento')    
    showinfo(title='Diretorio selecionado', message=diretorio)
    diretorio = diretorio.replace("/", "\\")
    arquivos_lista = glob.glob(diretorio+'\*')
    print(df_base.columns)
    return arquivos_lista, diretorio

def executa_alimentar_base():
    alimentar_base(arquivos_lista, df_base)
    ttk.tkinter.messagebox.showinfo(title="Concluído", message="Processo concluído, execute o próximo passo")

def executa_preencher_nulos():
    preencher_nulos(df_benchmark_final)
    ttk.tkinter.messagebox.showinfo(title="Concluído", message="Processo concluído, realize o próximo passo")

def executa_calcular_indices():
    calcular_indice_por_ocupacao(df_benchmark_final)
    ttk.tkinter.messagebox.showinfo(title="Concluído", message="Processo concluído, realize o próximo passo")

def executa_salvar_arquivo():
    salvar_arquivo(df_benchmark_final)
    ttk.tkinter.messagebox.showinfo(title="Concluído", message="Salvo. Verifique o arquivo.")
    

root = tk.Tk()
open_button = ttk.Button(root, text='1. Selecione o Benchmark antigo', command=selecionar_arquivo)
open_button_2 = ttk.Button(root, text='2. Selecioone o diretório de monitoramento', command=selecionar_diretorio)
function_button_1 = ttk.Button(root, text='3. Atualizar Benchmark', command=executa_alimentar_base)
function_button_2 = ttk.Button(root, text='4. Preencher inputs nulos', command=executa_preencher_nulos)
function_button_2b = ttk.Button(root, text='4b. gerar_indices', command=executa_calcular_indices)
function_button_3 = ttk.Button(root, text='5. Salvar a nova planilha', command=executa_salvar_arquivo)
open_button.pack(expand=True)
open_button_2.pack(expand=True)
function_button_1.pack(expand=True)
function_button_2.pack(expand=True)
function_button_2b.pack(expand=True)
function_button_3.pack(expand=True)
root.mainloop()
