import pandas as pd
from datetime import datetime
import cfscrape
import os
import openpyxl
import numpy as np


#============================SALVAR DADOS===========================

def salvar_arquivo(df, nome_arquivo):
	path = os.getcwd()
	mes = datetime.today().strftime('%m')
	dia = datetime.today().strftime('%d')

	path_arquivos = f'{path}/arquivos/esoccer/{mes}/{dia}'
	if not os.path.exists(path_arquivos):
		os.makedirs(path_arquivos)

	# dir_mes = f'{path_arquivos}/{mes}'
	# if not os.path.exists(dir_mes):
	# 	os.makedirs(dir_mes)
		
	# dir_dia = f'{path_arquivos}/{mes}/{dia}'
	# if not os.path.exists(dir_dia):
	# 	os.makedirs(dir_dia)

	caminho_arquivo_xlsx = f'{path_arquivos}/{nome_arquivo}.xlsx'
	caminho_arquivo_csv = f'{path_arquivos}/{nome_arquivo}.csv'
		
	# today = datetime.today().strftime('%d_%m_%H_%M')

	if os.path.exists(path_arquivos):
		# if os.path.exists(caminho_arquivo_xlsx) or os.path.exists(caminho_arquivo_csv):
		# 	print('Já existe arquivo com mesmo nome, deseja sobrescrever o atual?')
		try:
			df.to_excel(caminho_arquivo_xlsx, index=False)
			df.to_csv(caminho_arquivo_csv, index=False)			
			
			os.system(f'start EXCEL.EXE "{caminho_arquivo_xlsx}"')
			
			print(f'Planilha "{nome_arquivo}" salva com sucesso!')
			# input('Pressione enter para finalizar...')

		except:
			print('Erro ao tentar gravar os dados.\nVerifique se há algum arquivo com mesmo nome aberto. Feche-o!!')
			input('Aperte enter para continuar...')
			
			df.to_excel(f'{nome_arquivo}.xlsx', index=False)
			df.to_csv(f'{nome_arquivo}.csv', index=False)				
			

			os.system(f'start EXCEL.EXE "{caminho_arquivo_xlsx}"')

			print(f'Planilha "{nome_arquivo}" salva com sucesso!')
			# input('Pressione enter para finalizar...')
	
	return caminho_arquivo_xlsx

#============================JOGOS DO DIA===========================

def coletar_dados():
	try:
		url = "https://d.flashscore.com.br/x/feed/t_36_12390_fJseY2UI_-3_pt-br_1"

		payload = ""
		headers = {
			"authority": "d.flashscore.com.br",
			"accept": "*/*",
			"accept-language": "pt-BR,pt-PT;q=0.9,pt;q=0.8,en-US;q=0.7,en;q=0.6",
			"dnt": "1",
			"origin": "https://www.flashscore.com.br",
			"referer": "https://www.flashscore.com.br/",
			"sec-ch-ua": '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
			"sec-ch-ua-mobile": "?0",
			"sec-ch-ua-platform": '"Windows"',
			"sec-fetch-dest": "empty",
			"sec-fetch-mode": "cors",
			"sec-fetch-site": "same-site",
			"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
			"x-fsign": "SW9D1eZo",
			"x-geoip": "1"
		}

		scraper = cfscrape.create_scraper()
		
		response = scraper.request("GET", url, data=payload, headers=headers)

		print('Dados coletados com sucesso!')
		# input('Pressione enter para finalizar...')
		return response.text
	
	except:
		print('Erro ao tentar coletar os dados!')
		input('Pressione enter para finalizar...')
		return 'Erro'

def gerar_dataframe(texto, tipo='com-hora'):

	try:
		lst_texto = texto.split('¬')

		lst_selecao = []

		for cod in lst_texto:
			if cod[:4] == '~AA÷' or cod[:3] == 'AE÷' or cod[:3] == 'AG÷' or cod[:3] == 'AF÷' or cod[:3] == 'AH÷' or cod[:4] == 'ADE÷':
				lst_selecao.append(cod)

		lst_texto = []

		texto = ''
		for i in lst_selecao:
			item = i.replace(':','#').replace('~AA÷','¬Id_Jogo:').replace('AE÷','|Player1:').replace('AG÷','|Gols_P1:').replace('AF÷','|Player2:').replace('AH÷','|Gols_P2:').replace('ADE÷','|Horario:')
			texto += item

		lst_jogos = texto.split('¬')
		lst_jogos = list(filter(None, lst_jogos))

		dados = []
		for item in lst_jogos:
			info = item.split('|')
			dict_info = {}
			for i in info:
				chave, valor = i.split(':')
				dict_info[chave] = valor
			dados.append(dict_info)

		df = pd.DataFrame(dados)
		df['Gols_P1'] = df['Gols_P1'].fillna(0)
		df['Gols_P2'] = df['Gols_P2'].fillna(0)
		df['Gols_P1'] = df['Gols_P1'].astype(int) 
		df['Gols_P2'] = df['Gols_P2'].astype(int) 
		df['Horario'] = df['Horario'].apply(lambda x: datetime.fromtimestamp(int(x)).strftime('%d-%m-%Y %H:%M:%S'))

		df = df.reindex(columns=['Id_Jogo','Horario', 'Player1', 'Gols_P1', 'Gols_P2', 'Player2', 'Analisar'])
		
		# hora_agora = (pd.to_datetime(hora_agora)).strftime('%d/%m/%Y %H:%M:%S')

		if tipo == 'com-hora':
			hora_agora = datetime.today().strftime('%d-%m-%Y %H:%M:%S')

			df = df.loc[df['Horario'] >= hora_agora]

		print('Dataframe gerado com sucesso!')
		
		# input('Pressione enter para finalizar...')
		return df

	except:

		df = pd.DataFrame(columns=['Id_Jogo', 'Horario', 'Player1', 'Gols_P1', 'Gols_P2', 'Player2', 'Analisar'])
		print('Erro ao gerar o dataframe!')
		input('Pressione enter para finalizar...')
		return df

#====================================DADOS H2H========================

def buscar_dados_jogos(path):
	dados = {}
		
	df = pd.read_excel(path, sheet_name='Sheet1', usecols=['Id_Jogo', 'Horario', 'Player1', 'Gols_P1', 'Gols_P2', 'Player2', 'Analisar'])
		
	for indice, item in df.iterrows():
		if str(item.Analisar) == 'X' or str(item.Analisar) == 'x':			
			dados[item.Id_Jogo] = [item.Id_Jogo, item.Player1, item.Player2, item.Horario]
 
	return dados

def coletar_dados_h2h(cod_jogo):

	url = f"https://d.flashscore.com.br/x/feed/df_hh_1_{cod_jogo}"

	payload = ""
	headers = {
		"authority": "d.flashscore.com.br",
		"accept": "*/*",
		"accept-language": "pt-BR,pt-PT;q=0.9,pt;q=0.8,en-US;q=0.7,en;q=0.6",
		"dnt": "1",
		"origin": "https://www.flashscore.com.br",
		"referer": "https://www.flashscore.com.br/",
		"sec-ch-ua": '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
		"sec-ch-ua-mobile": "?0",
		"sec-ch-ua-platform": '"Windows"',
		"sec-fetch-dest": "empty",
		"sec-fetch-mode": "cors",
		"sec-fetch-site": "same-site",
		"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
		"x-fsign": "SW9D1eZo"
	}

	scraper = cfscrape.create_scraper()
	response = scraper.request("GET", url, data=payload, headers=headers)

	return response.text

def gerar_dataframe_h2h(texto):

	lst_texto = texto.split('¬')

	lst_selecao = []
	for cod in lst_texto:
		if cod[:4] == '~KB÷' or cod[:3] == 'KF÷' or cod[:3] == 'KJ÷' or cod[:3] == 'KK÷' or cod[:3] == 'KU÷' or cod[:3] == 'KT÷' or cod[:4] == '~KC÷':

			lst_selecao.append(cod)

	lst_texto = []
	texto = ''
	for i in lst_selecao:
		item = i.replace(':','').replace('*','').replace('~KB÷','¬Tipo:').replace('KF÷','|Campeonato:').replace('KJ÷','|Casa:').replace('KK÷','|Fora:').replace('KU÷','|Gol_Casa:').replace('KT÷','|Gol_Fora:').replace('~KC÷','=|Data:')
		
		texto += item

	lst_tipo = texto.split('¬')

	lst_data = []

	for tipo in lst_tipo:
		lst_data.append(tipo.split('='))

	for i in lst_data:
		if i != '' and i != None:
			for index in range(1, len(i)):
				i[index] = i[0] + i[index]
			del i[0]

	dados = []
		
	for lista in lst_data:
		for item in lista:
			info = item.split('|')
			dict_info = {}
			for i in info:
				chave, valor = i.split(':')
				dict_info[chave] = valor
			dados.append(dict_info)

	df = pd.DataFrame(dados)

	df = df.reindex(columns=['Tipo', 'Data', 'Campeonato', 'Casa',	'Gol_Casa', 'Gol_Fora', 'Fora'])
	df['Gol_Casa'] = df['Gol_Casa'].astype(int) 
	df['Gol_Fora'] = df['Gol_Fora'].astype(int) 
	df['Data'] = df['Data'].apply(lambda x: datetime.fromtimestamp(int(x)).strftime('%d-%m-%Y %H:%M:%S'))

	df = df.drop_duplicates(subset=['Tipo', 'Data', 'Campeonato'])

	return df


def formar_colunas_media_gol_total(df, player1, player2):

	filtro1 = (df['Tipo'] == f'Últimos jogos {player1}')
	filtro2 = (df['Tipo'] == f'Últimos jogos {player2}')
	
	total_sum = df.loc[filtro1, 'Gol_Casa'].head(20).sum() + df.loc[filtro1, 'Gol_Fora'].head(20).sum()
	MedGol_Total_T1_20 = total_sum/20
	
	total_sum = df.loc[filtro2, 'Gol_Casa'].head(20).sum() + df.loc[filtro2, 'Gol_Fora'].head(20).sum()
	MedGol_Total_T2_20 = total_sum/20

	# MedGol_Total_T1_20 = ((df.loc[filtro1, 'Gol_Casa'].iloc[:20].mean()) + (df.loc[filtro1, ['Gol_Fora', 'Gol_Casa']].iloc[:20].mean()))

	# MedGol_Total_T2_20 = ((df.loc[filtro2, 'Gol_Casa'].iloc[:20].mean()) + (df.loc[filtro2, ['Gol_Fora', 'Gol_Casa']].iloc[:20].mean()))

	return round(MedGol_Total_T1_20, 2), round(MedGol_Total_T2_20, 2)

def formar_colunas_media_gol_time(df, player1, player2):
	filtro3 = (df['Fora'] == f'{player1}') & (df['Tipo'] == f'Últimos jogos {player1}')
	filtro5 = (df['Fora'] == f'{player2}') & (df['Tipo'] == f'Últimos jogos {player2}')
	
	filtro4 = (df['Casa'] == f'{player1}') & (df['Tipo'] == f'Últimos jogos {player1}')
	filtro6 = (df['Casa'] == f'{player2}') & (df['Tipo'] == f'Últimos jogos {player2}')

	MedGol_T1_20 = ((df.loc[filtro3, 'Gol_Fora'].iloc[:10].mean()) + (df.loc[filtro4, 'Gol_Casa'].iloc[:10].mean()))/2

	MedGol_T2_20 = ((df.loc[filtro5, 'Gol_Fora'].iloc[:10].mean()) + (df.loc[filtro6, 'Gol_Casa'].iloc[:10].mean()))/2

	return MedGol_T1_20.round(2), MedGol_T2_20.round(2)

def formar_colunas_over_45(df, player1, player2):
	df_filtrado = df.loc[(df['Tipo'] == f'Últimos jogos {player1}'), ['Gol_Casa', 'Gol_Fora']].iloc[:20]
	soma = df_filtrado.sum(axis=1)
	over_45_T1_20 = (soma > 4.5).sum()
	
	df_filtrado = df.loc[(df['Tipo'] == f'Últimos jogos {player1}'), ['Gol_Casa', 'Gol_Fora']].iloc[:5]
	soma = df_filtrado.sum(axis=1)
	over_45_T1_5 = (soma > 4.5).sum()

	df_filtrado = df.loc[(df['Tipo'] == f'Últimos jogos {player2}'), ['Gol_Casa', 'Gol_Fora']].iloc[:20]
	soma = df_filtrado.sum(axis=1)
	over_45_T2_20 = (soma > 4.5).sum()
	
	df_filtrado = df.loc[(df['Tipo'] == f'Últimos jogos {player2}'), ['Gol_Casa', 'Gol_Fora']].iloc[:5]
	soma = df_filtrado.sum(axis=1)
	over_45_T2_5 = (soma > 4.5).sum()

	return str((over_45_T1_20/20*100).round(2))+'%', str((over_45_T1_5/5*100).round(2))+'%', str((over_45_T2_20/20*100).round(2))+'%', str((over_45_T2_5/5*100).round(2))+'%'

def formar_colunas_over_55(df, player1, player2):
	df_filtrado = df.loc[(df['Tipo'] == f'Últimos jogos {player1}'), ['Gol_Casa', 'Gol_Fora']].iloc[:20]
	soma = df_filtrado.sum(axis=1)
	over_55_T1_20 = (soma > 5.5).sum()
	
	df_filtrado = df.loc[(df['Tipo'] == f'Últimos jogos {player1}'), ['Gol_Casa', 'Gol_Fora']].iloc[:5]
	soma = df_filtrado.sum(axis=1)
	over_55_T1_5 = (soma > 5.5).sum()

	df_filtrado = df.loc[(df['Tipo'] == f'Últimos jogos {player2}'), ['Gol_Casa', 'Gol_Fora']].iloc[:20]
	soma = df_filtrado.sum(axis=1)
	over_55_T2_20 = (soma > 5.5).sum()
	
	df_filtrado = df.loc[(df['Tipo'] == f'Últimos jogos {player2}'), ['Gol_Casa', 'Gol_Fora']].iloc[:5]
	soma = df_filtrado.sum(axis=1)
	over_55_T2_5 = (soma > 5.5).sum()

	return str((over_55_T1_20/20*100).round(2))+'%', str((over_55_T1_5/5*100).round(2))+'%', str((over_55_T2_20/20*100).round(2))+'%', str((over_55_T2_5/5*100).round(2))+'%'

def formar_colunas_v_e_d(df, player1, player2):
	filtro = (df['Tipo'] == f'Últimos jogos {player1}') & (df['Casa'] == f'{player1}')
	df_filtrado = df.loc[filtro][:10]
	resultados = np.where(df_filtrado['Gol_Casa'] > df_filtrado['Gol_Fora'], 'ganhou', np.where(df_filtrado['Gol_Casa'] == df_filtrado['Gol_Fora'], 'empatou', 'perdeu'))
	contagem_resultados_casa = pd.Series(resultados).value_counts()

	filtro = (df['Tipo'] == f'Últimos jogos {player1}') & (df['Fora'] == f'{player1}')
	df_filtrado = df.loc[filtro][:10]
	resultados = np.where(df_filtrado['Gol_Casa'] < df_filtrado['Gol_Fora'], 'ganhou', np.where(df_filtrado['Gol_Casa'] == df_filtrado['Gol_Fora'], 'empatou', 'perdeu'))
	contagem_resultados_fora = pd.Series(resultados).value_counts()

	try: ganhou_casa = contagem_resultados_casa['ganhou']
	except:	ganhou_casa = 0
	try: empatou_casa = contagem_resultados_casa['empatou'] 
	except: empatou_casa = 0
	try: perdeu_casa = contagem_resultados_casa['perdeu']
	except: perdeu_casa = 0
	try: ganhou_fora = contagem_resultados_fora['ganhou']
	except: ganhou_fora = 0
	try: empatou_fora = contagem_resultados_fora['empatou']
	except: empatou_fora = 0
	try: perdeu_fora = contagem_resultados_fora['perdeu']
	except: perdeu_fora = 0

	Vit_T1 = ganhou_casa + ganhou_fora
	Emp_T1 = empatou_casa + empatou_fora
	Der_T1 = perdeu_casa + perdeu_fora

	filtro = (df['Tipo'] == f'Últimos jogos {player2}') & (df['Casa'] == f'{player2}')
	df_filtrado = df.loc[filtro][:10]
	resultados = np.where(df_filtrado['Gol_Casa'] > df_filtrado['Gol_Fora'], 'ganhou', np.where(df_filtrado['Gol_Casa'] == df_filtrado['Gol_Fora'], 'empatou', 'perdeu'))
	contagem_resultados_casa = pd.Series(resultados).value_counts()

	filtro = (df['Tipo'] == f'Últimos jogos {player2}') & (df['Fora'] == f'{player2}')
	df_filtrado = df.loc[filtro][:10]
	resultados = np.where(df_filtrado['Gol_Casa'] < df_filtrado['Gol_Fora'], 'ganhou', np.where(df_filtrado['Gol_Casa'] == df_filtrado['Gol_Fora'], 'empatou', 'perdeu'))
	contagem_resultados_fora = pd.Series(resultados).value_counts()

	try: ganhou_casa = contagem_resultados_casa['ganhou']
	except:	ganhou_casa = 0
	try: empatou_casa = contagem_resultados_casa['empatou'] 
	except: empatou_casa = 0
	try: perdeu_casa = contagem_resultados_casa['perdeu']
	except: perdeu_casa = 0
	try: ganhou_fora = contagem_resultados_fora['ganhou']
	except: ganhou_fora = 0
	try: empatou_fora = contagem_resultados_fora['empatou']
	except: empatou_fora = 0
	try: perdeu_fora = contagem_resultados_fora['perdeu']
	except: perdeu_fora = 0

	Vit_T2 = ganhou_casa + ganhou_fora
	Emp_T2 = empatou_casa + empatou_fora
	Der_T2 = perdeu_casa + perdeu_fora

	return str((Vit_T1/20*100).round(2))+'%', str((Emp_T1/20*100).round(2))+'%', str((Der_T1/20*100).round(2))+'%', str((Vit_T2/20*100).round(2))+'%', str((Emp_T2/20*100).round(2))+'%', str((Der_T2/20*100).round(2))+'%'

def formar_colunas_confronto_direto_v_e_d(df, player1):
	filtro = (df['Tipo'] == 'Confrontos diretos') & (df['Casa'] == f'{player1}')
	df_filtrado = df.loc[filtro][:5]
	resultados = np.where(df_filtrado['Gol_Casa'] > df_filtrado['Gol_Fora'], 'ganhou', np.where(df_filtrado['Gol_Casa'] == df_filtrado['Gol_Fora'], 'empatou', 'perdeu'))
	contagem_resultados_casa = pd.Series(resultados).value_counts()

	filtro = (df['Tipo'] == 'Confrontos diretos') & (df['Fora'] == f'{player1}')
	df_filtrado = df.loc[filtro][:5]
	resultados = np.where(df_filtrado['Gol_Casa'] < df_filtrado['Gol_Fora'], 'ganhou', np.where(df_filtrado['Gol_Casa'] == df_filtrado['Gol_Fora'], 'empatou', 'perdeu'))
	contagem_resultados_fora = pd.Series(resultados).value_counts()

	try: ganhou_casa = contagem_resultados_casa['ganhou']
	except:	ganhou_casa = 0
	try: empatou_casa = contagem_resultados_casa['empatou'] 
	except: empatou_casa = 0
	try: perdeu_casa = contagem_resultados_casa['perdeu']
	except: perdeu_casa = 0
	try: ganhou_fora = contagem_resultados_fora['ganhou']
	except: ganhou_fora = 0
	try: empatou_fora = contagem_resultados_fora['empatou']
	except: empatou_fora = 0
	try: perdeu_fora = contagem_resultados_fora['perdeu']
	except: perdeu_fora = 0

	Vit_cd_T1 = ganhou_casa + ganhou_fora
	Emp_cd_T1 = empatou_casa + empatou_fora
	Der_cd_T1 = perdeu_casa + perdeu_fora

	Vit_cd_T2 = Der_cd_T1
	Emp_cd_T2 = Emp_cd_T1
	Der_cd_T2 = Vit_cd_T1

	return str(round(Vit_cd_T1/10*100, 2))+'%', str(round(Emp_cd_T1/10*100,2))+'%', str(round(Der_cd_T1/10*100, 2))+'%', str(round(Vit_cd_T2/10*100, 2))+'%', str(round(Emp_cd_T2/10*100, 2))+'%', str(round(Der_cd_T2/10*100, 2))+'%'

def formar_colunas_confronto_direto_over_45(df):
	df_filtrado = df.loc[(df['Tipo'] == 'Confrontos diretos'), ['Gol_Casa', 'Gol_Fora']].iloc[:20]
	soma = df_filtrado.sum(axis=1)
	over_45_T1_20 = (soma > 4.5).sum()
	
	df_filtrado = df.loc[(df['Tipo'] == 'Confrontos diretos'), ['Gol_Casa', 'Gol_Fora']].iloc[:5]
	soma = df_filtrado.sum(axis=1)
	over_45_T1_5 = (soma > 4.5).sum()

	over_45_T2_20 = over_45_T1_20
	over_45_T2_5 = over_45_T1_5

	return str((over_45_T1_20/20*100).round(2))+'%', str((over_45_T1_5/5*100).round(2))+'%', str((over_45_T2_20/20*100).round(2))+'%', str((over_45_T2_5/5*100).round(2))+'%'

def formar_colunas_confronto_direto_over_55(df):
	df_filtrado = df.loc[(df['Tipo'] == 'Confrontos diretos'), ['Gol_Casa', 'Gol_Fora']].iloc[:20]
	soma = df_filtrado.sum(axis=1)
	over_55_cd_T1_20 = (soma > 5.5).sum()
	
	df_filtrado = df.loc[(df['Tipo'] == 'Confrontos diretos'), ['Gol_Casa', 'Gol_Fora']].iloc[:5]
	soma = df_filtrado.sum(axis=1)
	over_55_cd_T1_5 = (soma > 5.5).sum()

	over_55_T2_cd_20 = over_55_cd_T1_20
	over_55_cd_T2_5 = over_55_cd_T1_5

	return str((over_55_cd_T1_20/20*100).round(2))+'%', str((over_55_cd_T1_5/5*100).round(2))+'%', str((over_55_T2_cd_20/20*100).round(2))+'%', str((over_55_cd_T2_5/5*100).round(2))+'%'

def formar_colunas_over_05(df, player1, player2):

	filtro1 = ((df['Tipo'] == f'Últimos jogos {player1}') & (df['Casa'] == f'{player1}')) 
	filtro2 = ((df['Tipo'] == f'Últimos jogos {player1}') & (df['Fora'] == f'{player1}'))

	df_filtrado = df.loc[filtro1, ['Gol_Casa']].iloc[:10]
	soma = df_filtrado.sum(axis=1)
	over_05_T1_casa = (soma > 0.5).sum()
	
	df_filtrado = df.loc[filtro2, ['Gol_Fora']].iloc[:10]
	soma = df_filtrado.sum(axis=1)
	over_05_T1_fora = (soma > 0.5).sum()
	
	over_05_T1 = over_05_T1_fora + over_05_T1_casa

	filtro1 = ((df['Tipo'] == f'Últimos jogos {player2}') & (df['Casa'] == f'{player2}')) 
	filtro2 = ((df['Tipo'] == f'Últimos jogos {player2}') & (df['Fora'] == f'{player2}'))

	df_filtrado = df.loc[filtro1, ['Gol_Casa']].iloc[:10]
	soma = df_filtrado.sum(axis=1)
	over_05_T2_casa = (soma > 0.5).sum()
	
	df_filtrado = df.loc[filtro2, ['Gol_Fora']].iloc[:10]
	soma = df_filtrado.sum(axis=1)
	over_05_T2_fora = (soma > 0.5).sum()
	
	over_05_T2 = over_05_T2_casa + over_05_T2_fora

	return str((over_05_T1/20*100).round(2))+'%', str((over_05_T2/20*100).round(2))+'%'

def formar_colunas_cd_over_05(df, player1, player2):

	filtro1 = ((df['Tipo'] == 'Confrontos diretos') & (df['Casa'] == f'{player1}')) 
	filtro2 = ((df['Tipo'] == 'Confrontos diretos') & (df['Fora'] == f'{player1}'))

	df_filtrado = df.loc[filtro1, ['Gol_Casa']].iloc[:10]
	soma = df_filtrado.sum(axis=1)
	over_05_T1_casa = (soma > 0.5).sum()
	
	df_filtrado = df.loc[filtro2, ['Gol_Fora']].iloc[:10]
	soma = df_filtrado.sum(axis=1)
	over_05_T1_fora = (soma > 0.5).sum()
	
	over_05_cd_T1 = over_05_T1_fora + over_05_T1_casa

	filtro1 = ((df['Tipo'] == 'Confrontos diretos') & (df['Casa'] == f'{player2}')) 
	filtro2 = ((df['Tipo'] == 'Confrontos diretos') & (df['Fora'] == f'{player2}'))

	df_filtrado = df.loc[filtro1, ['Gol_Casa']].iloc[:10]
	soma = df_filtrado.sum(axis=1)
	over_05_T2_casa = (soma > 0.5).sum()
	
	df_filtrado = df.loc[filtro2, ['Gol_Fora']].iloc[:10]
	soma = df_filtrado.sum(axis=1)
	over_05_T2_fora = (soma > 0.5).sum()
	
	over_05_cd_T2 = over_05_T2_casa + over_05_T2_fora

	return str((over_05_cd_T1/20*100).round(2))+'%', str((over_05_cd_T2/20*100).round(2))+'%'


def realizar_analise(df, player1, player2):

	MedGol_Total_T1_20, MedGol_Total_T2_20 = formar_colunas_media_gol_total(df, player1, player2)
	MedGol_T1_20, MedGol_T2_20 = formar_colunas_media_gol_time(df, player1, player2)
	over_45_T1_20, over_45_T1_5, over_45_T2_20, over_45_T2_5 = formar_colunas_over_45(df, player1, player2)
	over_55_T1_20, over_55_T1_5, over_55_T2_20, over_55_T2_5 = formar_colunas_over_55(df, player1, player2)
	Vit_T1, Emp_T1, Der_T1, Vit_T2, Emp_T2, Der_T2 = formar_colunas_v_e_d(df, player1, player2)
	Vit_cd_T1, Emp_cd_T1, Der_cd_T1, Vit_cd_T2, Emp_cd_T2, Der_cd_T2 = formar_colunas_confronto_direto_v_e_d(df, player1)
	over_45_cd_T1_20, over_45_cd_T1_5, over_45_T2_cd_20, over_45_cd_T2_5 = formar_colunas_confronto_direto_over_45(df)
	over_55_cd_T1_20, over_55_cd_T1_5, over_55_T2_cd_20, over_55_cd_T2_5 = formar_colunas_confronto_direto_over_55(df)
	over_05_T1, over_05_T2 = formar_colunas_over_05(df, player1, player2)
	over_05_cd_T1, over_05_cd_T2 = formar_colunas_cd_over_05(df, player1, player2)

	dict_t1 = {'Player': f'{player1}', 'Vit(20)': Vit_T1,'Emp(20)': Emp_T1, 'Der(20)': Der_T1, 'Med_Tot(20)': MedGol_Total_T1_20, 'Med_Time(20)': MedGol_T1_20, '>0.5(20)': over_05_T1, '>4.5(20)': over_45_T1_20, '>4.5(5)': over_45_T1_5, '>5.5(20)': over_55_T1_20, '>5.5(5)': over_55_T1_5, 'Vit_CD(10)': Vit_cd_T1, 'Emp_CD(10)': Emp_cd_T1, 'Der_CD(10)': Der_cd_T1, '>0.5_cd(20)': over_05_cd_T1, '>4.5_cd(20)': over_45_cd_T1_20, '>4.5_cd(5)': over_45_cd_T1_5, '>5.5_cd(20)':over_55_cd_T1_20, '>5.5_cd(5)':over_55_cd_T1_5}

	dict_t2 = {'Player': f'{player2}', 'Vit(20)': Vit_T2, 'Emp(20)': Emp_T2, 'Der(20)': Der_T2,  'Med_Tot(20)': MedGol_Total_T2_20, 'Med_Time(20)': MedGol_T2_20, '>0.5(20)': over_05_T2, '>4.5(20)': over_45_T2_20, '>4.5(5)': over_45_T2_5, '>5.5(20)': over_55_T2_20, '>5.5(5)': over_55_T2_5, 'Vit_CD(10)': Vit_cd_T2, 'Emp_CD(10)': Emp_cd_T2, 'Der_CD(10)': Der_cd_T2, '>0.5_cd(20)': over_05_cd_T2, '>4.5_cd(20)': over_45_T2_cd_20, '>4.5_cd(5)': over_45_cd_T2_5, '>5.5_cd(20)':over_55_T2_cd_20, '>5.5_cd(5)':over_55_cd_T2_5}
	
	dict_t0 = {'Player': 'Valores', 'Vit(20)': 'Vit(20)', 'Emp(20)': 'Emp(20)', 'Der(20)': 'Der(20)',  'Med_Tot(20)': 'Med_Tot(20)', 'Med_Time(20)': 'Med_Time(20)', '>0.5(20)': '>0.5(20)', '>4.5(20)': '>4.5(20)', '>4.5(5)': '>4.5(5)', '>5.5(20)': '>5.5(20)', '>5.5(5)': '>5.5(5)', 'Vit_CD(10)': 'Vit_CD(10)', 'Emp_CD(10)': 'Emp_CD(10)', 'Der_CD(10)': 'Der_CD(10)', '>0.5_cd(20)': '>0.5_cd(20)', '>4.5_cd(20)': '>4.5_cd(20)', '>4.5_cd(5)': '>4.5_cd(5)', '>5.5_cd(20)':'>5.5_cd(20)', '>5.5_cd(5)':'>5.5_cd(5)'}
	
	df_t0 = pd.DataFrame.from_dict(dict_t0, orient='index', columns=['Valores'])
	df_t1 = pd.DataFrame.from_dict(dict_t1, orient='index', columns=[f'{player1}'])
	df_t2 = pd.DataFrame.from_dict(dict_t2, orient='index', columns=[f'{player2}'])
	
	df_final = pd.concat([df_t0, df_t1, df_t2], axis=1)

	# df_final.rename(index={'Player': 'Nome do Jogador'}, inplace=True)
	# df_final = pd.DataFrame([dict_t1, dict_t2])

	return df_final

#=========================================================================


def teste_valor_numerico():
    while True:
        user_input = input()
        menu_principal_opcoes()
        try:
            user_input = int(user_input)
            if user_input in [1,2,3,0]:
                break
            else:
                print("\nDigite uma opção válida:")
        except ValueError:
            print("\nDigite uma opção válida:")
    return user_input

def menu_principal_opcoes():
    
    os.system('cls') or None
 
    print('\nOPÇOES')
    print('-------------')
    print('1. Jogos do dia')
    print('2. Abrir planilha com jogos do dia')
    print('3. Realizar análises')
    print('-------------')
    print('0. SAIR')
    print('\nQual a opção desejada? ', end=" ")
    
def menu_principal():
    menu_principal_opcoes()
    opcao = teste_valor_numerico()
    
    while opcao != 0:
        if opcao == 1:
            tipo = 'jogos-do-dia'
            break
        elif opcao == 2:
            tipo = 'abrir-planilha'
            break
        elif opcao == 3:
            tipo = 'analises'
            break
        else:
            print('Escolha uma opção válida: ', end=' ')
            opcao = int(input())
    
    if opcao == 0:
        os.system('cls') or None
        exit()

    return tipo, opcao  


def buscar_local_arquivo():
	path = os.getcwd()
	mes = datetime.today().strftime('%m')
	dia = datetime.today().strftime('%d')

	path = f'{path}\\arquivos\\esoccer\\{mes}\\{dia}'
	path_arquivo = f'{path}\\esoccer-jogos-dia.xlsx'

	return path, path_arquivo


def main():

	os.system('cls') or None
	opcao = 999
	

	while opcao != 0:
		tipo, opcao = menu_principal()
		os.system('cls') or None

		if tipo == 'jogos-do-dia':			
			texto = coletar_dados()
			df = gerar_dataframe(texto)
			df_completo = gerar_dataframe(texto, tipo='sem-hora') #sem restrição de horario
			local_arquivo = salvar_arquivo(df_completo, 'esoccer-jogos-dia-completo')			
			local_arquivo = salvar_arquivo(df, 'esoccer-jogos-dia')			
		   
		elif tipo == 'abrir-planilha':
			path = os.getcwd()
			mes = datetime.today().strftime('%m')
			dia = datetime.today().strftime('%d')
			path_arquivos = f'{path}\\arquivos\\esoccer\\{mes}\\{dia}'

			if not os.path.exists(path_arquivos):
				# os.makedirs(path_arquivos)
				print('O arquivo com os jogos do dia ainda não foi gerado!!')
				main()
			else:
				try:
					caminho_arquivo_xlsx = buscar_local_arquivo()
					print(caminho_arquivo_xlsx)
					input()
					os.system(f'start EXCEL.EXE "{caminho_arquivo_xlsx}	"')
				except:
					print('Arquivo já se encontra aberto ou não foi gerado corretamente!!')
					input('\nPressione enter para finalizar...')
					main()

		elif tipo == 'analises':
			path, path_arquivo = buscar_local_arquivo()
			
			lst_dataframes = []

			if not os.path.exists(path_arquivo):
				print('O arquivo com os jogos do dia ainda não foi gerado / está aberto!!')
				main()
			else:	
				dict_dados = buscar_dados_jogos(path_arquivo)
				for c, v in dict_dados.items():
					id_jogo = v[0]
					player1 = v[1]
					player2 = v[2]
					horario = str(v[3]).replace(' ','_').replace(':', '-')
					print(id_jogo, player1, player2, horario)

					texto = coletar_dados_h2h(id_jogo)
					print('Dados coletados com sucesso!')

					df = gerar_dataframe_h2h(texto)
					print('Dataframe gerado com sucesso!')

					df_final = realizar_analise(df, player1, player2)
					print('Análise realizada com sucesso!')
					
					lst_dataframes.append(df_final)

				df_final = pd.concat(lst_dataframes, axis=1)

				arquivo = f'{path}\\esoccer_{player1}-{player2}-{horario}.xlsx'
				
				df_final.to_excel(arquivo, index=False)
				
				os.system(f'start EXCEL.EXE "{arquivo}"')
				print(f'Arquivo gerado com sucesso:\n {arquivo}')
				

			

	

if (__name__ == "__main__"):
	main()