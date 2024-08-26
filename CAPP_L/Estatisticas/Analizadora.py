import os
import statistics
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
import numpy as np
from pathlib import Path
import pandas as pd
import datetime
from typing import Any


def cria_csv_por_colunas(dicionario: dict[str: dict[str: Any]]) -> str:
    """
    Função que cria tabelas CSV por meio de dicionários que representam os elementos da coluna. Por exemplo:
    dicionário = {'nome_aluno': {'aula1': 1, 'aula2': 2, ... }, ...}

    Na linha <nome_aluno> e coluna <aula1> queremos que a tabela tenha valor 1, para a coluna <aula2> queremos que
    tenha valor 2.

    :param dicionario: Dicionário de dicionários.
    :return: Retorna a string da tabela CSV.
    """

    nome_colunas = ['Nome dos Alunos']
    for aluno in dicionario:
        for colunas_aluno in dicionario[aluno]:

            if colunas_aluno not in nome_colunas:
                nome_colunas.append(colunas_aluno)

    nome_colunas = [nome_colunas[0]] + sorted(nome_colunas[1:])

    csv_lines = [nome_colunas]
    for aluno in dicionario:
        linha_aluno = [aluno]
        for nome_coluna in nome_colunas[1:]:

            if nome_coluna in dicionario[aluno].keys():
                linha_aluno.append(dicionario[aluno][nome_coluna])
            else:
                linha_aluno.append(0)
        csv_lines.append(linha_aluno)

    csv_string = ''
    for line in csv_lines:
        for i, element in enumerate(line):

            if i == len(line) - 1:
                csv_string += f'{element}\n'
            else:
                csv_string += f'{element};'

    return csv_string


def cria_csv_2linhas(dicionario: dict[str: Any]) -> str:
    """
    Recebe um dicionário onde as chaves são os nomes das colunas e cada coluna possui apenas um elemento.
    Ou seja, produz uma tabela csv de dimensões N-colunas e 2 linhas.

    :param dicionario: Dicionário que se quer transformar em csv
    :return:
    """

    csv = ''
    header = ''
    itens = ''
    for i, key in enumerate(dicionario.keys()):
        if i == len(dicionario.keys()) - 1:
            header += f'{key}\n'
            itens += f'{dicionario[key]}'
        else:
            header += f'{key};'
            itens += f'{dicionario[key]};'
    csv = header + itens

    return csv


base = Path(os.getcwd())

turmas = [turma for turma in os.listdir(base) if turma != 'Analizadora.py']

for turma in turmas:
    print(f'''>>>PREPARANDO BASE DE DADOS DE {turma}<<<''')
    correcoes = sorted(os.listdir(base / turma / 'CSVs'))

    os.makedirs(base / turma / f'Dados_da_Turma_{turma}', exist_ok=True)
    os.makedirs(base / turma / 'Alunos', exist_ok=True)
    os.makedirs(base / turma / 'Graficos_das_Aulas', exist_ok=True)

    alunos_aulas_notas: dict[str: dict[str: float]] = {}
    dados_turma = {}
    for correcao in correcoes:
        csv_correcao = pd.read_csv(base / turma / f'CSVs/{correcao}', sep=';')

        nota_media = statistics.mean(csv_correcao['Nota'])

        print(f'''
        >>>GERANDO GRÁFICO DE {correcao}''')
        plt.figure(figsize=(20, 12))
        plt.title(f'Gráfico de {correcao}. Gerado em {datetime.date.today()}')
        plt.ylim((0, 100))
        plt.yticks([i for i in range(0, 110, 10)] + [nota_media],
                   [j for j in range(0, 110, 10)] + [round(nota_media, 2)])  # isso mostra o valor da linha da média

        nomes_alunos_p_grafico = []  # para os nomes dos alunos não se sobreporem
        for nome in csv_correcao['Nome']:
            lista = nome.split('_')
            novo_nome = ''
            for pedaco in lista:
                novo_nome += f'{pedaco}\n'
            nomes_alunos_p_grafico.append(novo_nome)

        plt.bar(nomes_alunos_p_grafico, csv_correcao['Nota'])
        plt.axhline(y=nota_media, color='r')
        plt.savefig(base / turma / 'Graficos_das_Aulas' / f'{correcao[:-4]}_{datetime.date.today()}.png')
        plt.close()

        s_nota_turma: float = 0
        for i, aluno in enumerate(csv_correcao['Nome']):

            if aluno not in alunos_aulas_notas.keys():
                alunos_aulas_notas[aluno] = {}

            alunos_aulas_notas[aluno][correcao[:-4]] = csv_correcao['Nota'][i]

            # Para análise da turma
            s_nota_turma += csv_correcao['Nota'][i]
        dados_turma[correcao[:-4]] = s_nota_turma / len(csv_correcao['Nome'])

    # geramos a tabela das notas
    str_csv_geral = cria_csv_por_colunas(alunos_aulas_notas)
    arq_notas_turma = open(base / turma / f'Dados_da_Turma_{turma}' / 'Tabela_de_Notas.txt', 'w', encoding='utf-8')
    arq_notas_turma.write(str_csv_geral)
    arq_notas_turma.close()

    print(f'''
    >>>GERANDO GRÁFICOS DOS ALUNOS DE {turma}<<<
    ''')
    medias_finais = {}
    for aluno in alunos_aulas_notas:
        dict_aulas_notas = alunos_aulas_notas[aluno]
        aulas, notas = dict_aulas_notas.keys(), [dict_aulas_notas[i] for i in dict_aulas_notas.keys()]
        media_nota = statistics.mean(notas)
        medias_finais[aluno] = media_nota

        csv_aluno = cria_csv_2linhas(dict_aulas_notas)

        os.makedirs(base / turma / 'Alunos' / f'Dados_de_{aluno}', exist_ok=True)
        arq_aluno = open(base / turma / 'Alunos' / f'Dados_de_{aluno}' / f'{aluno}.txt', 'w', encoding='utf-8')
        arq_aluno.write(csv_aluno)
        arq_aluno.close()

        plt.figure(figsize=(10, 6))
        plt.title(f'Gráfico de {aluno}. Gerado em {datetime.date.today()}')
        plt.ylim((0, 100))
        plt.yticks([i for i in range(0, 110, 10)] + [media_nota],
                   [j for j in range(0, 110, 10)] + [round(media_nota, 2)])  # isso mostra o valor da linha da média
        plt.bar(aulas, notas)
        plt.axhline(y=media_nota, color='r')
        plt.savefig(base / turma / 'Alunos' / f'Dados_de_{aluno}' / f'Grafico_{aluno}_{datetime.date.today()}.png')
        plt.close()

    csv_turma = cria_csv_2linhas(dados_turma)
    arq_turma = open(base / turma / f'Dados_da_Turma_{turma}' / f'{turma}.txt', 'w', encoding='utf-8')
    arq_turma.write(csv_turma)
    arq_turma.close()

    aulas, medias = dados_turma.keys(), [dados_turma[i] for i in dados_turma.keys()]
    media_medias = statistics.mean(medias)

    plt.figure(figsize=(10, 6))
    plt.ylim((0, 100))
    plt.yticks([i for i in range(0, 110, 10)] + [media_medias],
               [j for j in range(0, 110, 10)] + [round(media_medias, 2)])  # isso mostra o valor da linha da média
    plt.title(f'Gráfico da turma {turma}. Gerado em {datetime.date.today()}')
    plt.bar(aulas, medias)
    plt.axhline(y=media_medias, color='r')
    plt.savefig(base / turma / f'Dados_da_Turma_{turma}' / f'Medias.png')
    plt.close()

    print(f'''
    +++GERANDO RELATÓRIO DE {turma}+++
    ''')

    relatorio_final = (f'RELATÓRIO DE {turma} === {datetime.date.today()} ==========================================='
                       f'=========================\n')
    # começaremos o relatório gerando alguns dados estatísticos básicos da turma.
    relatorio_final += f'''
    MÉDIAS FINAIS ------------------------------------------------------------------------------------------------------
    {'Nome': <50}{'Média Final': <20}'''
    passaram = 0
    for aluno in medias_finais:
        if medias_finais[aluno] >= 60:
            passaram += 1
            relatorio_final += f'''
    {aluno: <50}{medias_finais[aluno]: <20} | PASSOU'''
        else:
            relatorio_final += f'''
    {aluno: <50}{medias_finais[aluno]: <20}'''
    relatorio_final += f'''
    ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    DADOS ESTATÍSTICOS: 
    >>> A média de nota por aula é: {media_medias}.
    >>> {passaram} alunos já passaram no curso. ({(passaram/len(medias_finais.keys())).__round__(2)}%)
    '''

    # vamos achar a aula com maior e menor rendimento.
    for i, aula in enumerate(dados_turma):
        if i == 0:
            maior = menor = dados_turma[aula]
            aula_m = aula_M = aula
        elif dados_turma[aula] > maior:
            maior = dados_turma[aula]
            aula_M = aula
        elif dados_turma[aula] < menor:
            menor = dados_turma[aula]
            aula_m = aula

    relatorio_final += f'''
    >>> A aula com MAIOR rendimento foi {aula_M} | Rendimento: {maior} 
    >>> A aula com MENOR rendimento foi {aula_m} | Rendimento: {menor}
    '''

    arq_relatorio_turma = open(base / turma / f'Dados_da_Turma_{turma}' / f'Relatorio_Turma_{turma}.txt', 'w',
                               encoding='utf-8')
    arq_relatorio_turma.write(relatorio_final)
    arq_relatorio_turma.close()

print('>>>ANÁLISES GERADAS<<<')
