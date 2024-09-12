import os
import json
import pandas as pd
from collections import defaultdict
from datetime import datetime
from tkinter import Tk
from tkinter.filedialog import askdirectory
import dateparser

# Função para converter a string da data para um objeto datetime usando dateparser
def converter_data(data_str):
    return dateparser.parse(data_str)

# Função para calcular o tempo ativo por mês e número de mensagens
def calcular_tempo_ativo_e_mensagens_por_mes(mensagens, meu_identificador):
    # Dicionário para armazenar o tempo ativo por mês
    tempo_ativo_por_mes = defaultdict(int)
    # Dicionário para armazenar o número de mensagens por mês
    mensagens_por_mes = defaultdict(int)

    # Filtrar as mensagens enviadas por você
    minhas_mensagens = [msg for msg in mensagens if msg.get('creator', {}).get('email') == meu_identificador]

    # Agrupar as mensagens por dia
    mensagens_por_dia = defaultdict(list)
    for mensagem in minhas_mensagens:
        # Obter a data da mensagem
        data_mensagem = converter_data(mensagem['created_date'])
        # Agrupar as mensagens pelo dia (ano-mês-dia)
        if data_mensagem:
            mensagens_por_dia[data_mensagem.date()].append(data_mensagem)

    # Para cada dia, calcular o tempo ativo e número de mensagens
    for dia, timestamps in mensagens_por_dia.items():
        # Ordenar as timestamps do dia (caso estejam fora de ordem)
        timestamps.sort()
        # Calcular o tempo ativo como diferença entre a primeira e a última mensagem do dia
        inicio_dia = timestamps[0]
        fim_dia = timestamps[-1]
        tempo_ativo = fim_dia - inicio_dia
        # Agrupar o tempo e o número de mensagens por mês (ano-mês)
        chave_mes = f"{inicio_dia.year}-{inicio_dia.month:02d}"
        tempo_ativo_por_mes[chave_mes] += tempo_ativo.total_seconds()  # Somar o tempo em segundos
        mensagens_por_mes[chave_mes] += len(timestamps)  # Contar o número de mensagens no mês

    return tempo_ativo_por_mes, mensagens_por_mes

# Função para obter o nome do outro participante em uma DM
def obter_nome_outro_participante(membros, meu_email):
    for membro in membros:
        if membro['email'] != meu_email:
            return membro['name']
    return 'Desconhecido'

# Ocultar a janela principal do tkinter
root = Tk()
root.withdraw()

# Abrir janela para selecionar a pasta
pasta_groups = askdirectory(title="Selecione a pasta Groups com os arquivos JSON")

# Verificar se a pasta foi selecionada
if not pasta_groups:
    print("Nenhuma pasta foi selecionada. O programa será encerrado.")
else:
    meu_identificador = ''  # Seu email ou identificador
    dados_resultantes = []

    # Iterar sobre todas as pastas dentro da pasta "groups"
    for pasta in os.listdir(pasta_groups):
        caminho_pasta = os.path.join(pasta_groups, pasta)
        if os.path.isdir(caminho_pasta):
            print(f"Verificando pasta: {pasta}")

            # Caminhos para os arquivos group_info e messages
            caminho_group_info = os.path.join(caminho_pasta, 'group_info.json')
            caminho_messages = os.path.join(caminho_pasta, 'messages.json')

            # Ler o arquivo group_info para obter o nome do grupo ou contato
            if os.path.exists(caminho_group_info):
                with open(caminho_group_info, 'r', encoding='utf-8') as f:
                    group_info = json.load(f)
                    membros = group_info.get('members', [])
                    if len(membros) == 2:  # Se for uma DM
                        nome_grupo = obter_nome_outro_participante(membros, meu_identificador)
                    else:
                        nome_grupo = group_info.get('name', 'Desconhecido')
            else:
                nome_grupo = 'Desconhecido'

            # Ler o arquivo messages para processar as mensagens
            if os.path.exists(caminho_messages):
                with open(caminho_messages, 'r', encoding='utf-8') as f:
                    mensagens = json.load(f).get('messages', [])

                    if not mensagens:
                        print(f"Arquivo messages está vazio na pasta {pasta}")
                    else:
                        print(f"{len(mensagens)} mensagens encontradas na pasta {pasta}")

                    # Calcular o tempo ativo e número de mensagens por mês
                    tempo_ativo_por_mes, mensagens_por_mes = calcular_tempo_ativo_e_mensagens_por_mes(mensagens, meu_identificador)

                    # Formatar os dados para exibição
                    tempo_ativo_formatado = ', '.join([f"{mes}: {int(tempo // 3600)} horas e {int((tempo % 3600) // 60)} minutos"
                                                       for mes, tempo in tempo_ativo_por_mes.items()])

                    mensagens_formatado = ', '.join([f"{mes}: {quantidade} mensagens" for mes, quantidade in mensagens_por_mes.items()])

                    # Adicionar os dados ao relatório
                    dados_resultantes.append({
                        'Grupo/Contato': nome_grupo,
                        'Mensagens Enviadas': mensagens_formatado if mensagens_formatado else '0',
                        'Tempo Gasto (h:m:s)': tempo_ativo_formatado if tempo_ativo_formatado else '0 horas e 0 minutos'
                    })
            else:
                print(f"Arquivo messages não encontrado na pasta {pasta}")

    # Verificar se algum dado foi processado
    if not dados_resultantes:
        print("Nenhum dado foi encontrado ou processado.")
    else:
        # Criar um DataFrame com os dados resultantes
        df = pd.DataFrame(dados_resultantes)

        # Salvar o DataFrame em um arquivo Excel
        caminho_arquivo_excel = 'relatorio_chat.xlsx'
        df.to_excel(caminho_arquivo_excel, index=False)
        print(f"Relatório salvo em: {caminho_arquivo_excel}")
