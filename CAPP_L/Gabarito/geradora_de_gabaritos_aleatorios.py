# CONFIGURE ============================================================================================================
n_gab_aleatorios: int = 5  # defina aqui quantos gabaritos aleatórios você deseja gerar.
 manual = {}  # coloque o manual deas gerações. Veja o manual do CAPP-L para entender como deve ser seu formato.
# ======================================================================================================================

import sys
import os
from pathlib import Path
import importlib
from unittest.mock import patch
from CAPP_L.Geradoras.Geradora_Aleatoria_de_Strings.GAS import gas
from CAPP_L.Geradoras.Geradora_de_Faixas_Aleatorias.GIA import gia, isr
from CAPP_L.Geradoras.Geradora_de_Nomes.gera_nomes import gera_nomes
from CAPP_L.ICA.funcoes_de_correcao import executa_scripts_1_teste_por_exercicio
import CAPP_L.config as config
import datetime
import random

nomes_exes = config.NOMES_EXES
nomes_exes_input = config.NOMES_EXES_INPUT
testes_exes = config.TESTES_EXES

base = Path(str(config.BASE).replace(r'/Gabarito', '').replace(r'/CAPP_I_testes', ''))
gerar_gabarito = True
corrigir = True
if 'funcoes_gabarito.py' not in os.listdir(base / 'Gabarito'):
    print('\n>>>Não há funções_gabarito.py no diretório <Gabarito>, logo não há como o gabarito ser gerado...\n'
          'EXECUÇÃO ENCERRADA POR FALTA DE FUNÇÕES GABARITO')
    gerar_gabarito = False
    corrigir = False

if 'gabarito.py' in os.listdir(base / 'CAPP_I_testes'):
    gerar_gabarito = False
    print('GBA diz >>> Já existe um ou mais gabarito(s) aleatório(s).')

try:
    funcoes_gabarito = importlib.import_module('Gabarito.funcoes_gabarito')
except:
    print('\n>>>funcoes_gabarito.py não pode ser importado.\n'
          f'{sys.exc_info()[1]}\n'
          f'EXECUÇÃO ENCERRADA POR ERRO DE IMPORTAÇÃO DE FUNÇÕES GABARITO')
    gerar_gabarito = False
    corrigir = False

sementes = []


def geradora_de_gabaritos_aleatorios():
    gabaritos = {}
    str_gabaritos = ''''''

    if gerar_gabarito:
        for i in range(n_gab_aleatorios):

            semente = ''
            for i in str(datetime.datetime.now()):
                if i.isdigit():
                    semente += i
            semente = eval(semente)
            sementes.append(semente)

            random.seed(semente)

            argumentos_aleatorizados = {}

            for teste in manual:

                geracoes = []
                if manual[teste][0] != 'n':

                    n_testes, args_p_teste, s, instrucoes = (manual[teste][0], manual[teste][1], manual[teste][2],
                                                             manual[teste][3])

                    for i in range(n_testes):

                        args = ()
                        for j in range(args_p_teste):
                            args += (gas(*instrucoes, semente + i),)

                        if len(manual[teste]) == 5:
                            geracao = (args, manual[teste][4],)
                        else:
                            geracao = (args,)
                        geracoes.append(geracao)

                elif 'n' in manual[teste][0]:

                    n_testes = manual[teste][1]
                    instrucoes = manual[teste][2]
                    geracoes = []
                    ja_gerados = []
                    for i in range(n_testes):
                        args = tuple(gia(instrucoes, semente + i)[0])
                        if args not in ja_gerados:
                            ja_gerados.append(args)
                        else:
                            rep = 1
                            while args in ja_gerados:
                                args = tuple(gia(instrucoes, semente + i + rep)[0])
                                rep += 1
                                if n_testes * instrucoes[0] > instrucoes[1][1] - instrucoes[1][0]:
                                    print(f'{n_testes}, {instrucoes} --- IMPOSSÍVEL GERAR ARGUMENTOS NÃO REPETIDOS.')
                                    break
                            ja_gerados.append(args)

                        if len(manual[teste]) == 4:

                            geracoes.append((args, manual[teste][3]))

                        else:
                            geracoes.append((args,))

                argumentos_aleatorizados[teste] = geracoes

            # agora que criamos os testes, vamos fazer o gabarito
            gabarito: dict[dict[tuple: tuple]] = {}
            for i, exercicio in enumerate(nomes_exes_input):

                gabarito[exercicio]: dict[tuple: tuple] = {}

                for teste in argumentos_aleatorizados[exercicio.replace('exercicio', 'teste')]:
                    resultado = executa_scripts_1_teste_por_exercicio('Gabarito.funcoes_gabarito', exercicio, teste[0],
                                                                      inputs=teste[1])
                    gabarito[exercicio][(teste[0], tuple(teste[1]))] = resultado

            for j, exercicio in enumerate([exercicio_sem_input
                                           for exercicio_sem_input in nomes_exes if
                                           exercicio_sem_input not in nomes_exes_input]):

                gabarito[exercicio]: dict[tuple: tuple] = {}

                for teste in argumentos_aleatorizados[exercicio.replace('exercicio', 'teste')]:
                    resultado = executa_scripts_1_teste_por_exercicio('Gabarito.funcoes_gabarito', exercicio, teste[0])
                    gabarito[exercicio][teste] = resultado

            gabaritos[f'{semente}'] = gabarito
            str_gabaritos += f'''gabarito_{semente} = {gabarito}\n'''
            print('Gerando gabarito de semente:', semente)

        arq = open(file=base / 'CAPP_I_testes' / 'gabarito.py', mode='w', encoding='utf-8')
        arq.writelines(str_gabaritos)
        arq.close()

    return gabaritos
