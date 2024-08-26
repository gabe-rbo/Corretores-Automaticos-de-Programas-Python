import traceback
from pathlib import Path
import os
import importlib
import sys
import CAPP_L.config as config
from CAPP_L.ICA.funcoes_de_correcao import executa_scripts_1_teste_por_exercicio

base = Path(str(config.BASE).replace(r'/Gabarito', '').replace(r'/ICA', ''))

nomes_exercicios = config.NOMES_EXES
testes = config.TESTES_EXES
nomes_exercicios_input = config.NOMES_EXES_INPUT

gerar_gabarito = True
corrigir = True

if 'funcoes_gabarito.py' not in os.listdir(base / 'Gabarito'):
    print('\n>>>Não há funções_gabarito.py no diretório <Gabarito>, logo não há como o gabarito ser gerado...\n'
          'EXECUÇÃO ENCERRADA POR FALTA DE FUNÇÕES GABARITO')
    gerar_gabarito = False
    corrigir = False

if 'gabarito.py' in os.listdir(base / 'ICA'):
    gerar_gabarito = False

try:
    funcoes_gabarito = importlib.import_module('Gabarito.funcoes_gabarito')
except ImportError:
    print('\n>>>funcoes_gabarito.py não pode ser importado.\n'
          f'{sys.exc_info()[1]}\n'
          f'EXECUÇÃO ENCERRADA POR ERRO DE IMPORTAÇÃO DE FUNÇÕES GABARITO')
    gerar_gabarito = False
    corrigir = False


def tupladora(lista: list) -> list:
    """
    Pega uma lista e transforma quaisquer listas dentro dela em tuplas.
    Caso haja listas dentro da lista, elas também se tornarão listas.
    Essa função é necessária para garantir que não haverão listas nos testes, afinal, listas não podem ser chaves de
    dicionários.

    :param lista: Lista que se deseja confirmar que seus elementos não são listas
    :return: Lista transformada
    """

    for i, elemento in enumerate(lista):
        if type(elemento) is list:
            tupladora(elemento)
            lista[i] = tuple(lista[i])

        elif type(elemento) is tuple:
            elemento = list(elemento)
            elemento = tupladora(elemento)
            elemento = tuple(elemento)
            lista[i] = elemento

    return lista


def arq_gabarito(gabarito) -> None:
    """
    Função que cria o arquivo gabarito.py contendo o dicionário de exercícios com dicionários dos testes e resultados
    esperados, associados.
    Cria na pasta CAPP_I_testes pois é onde gabarito será importado.


    :param gabarito: Dicionário do gabarito.
    :return:
    """

    arq = open(base / 'ICA' / 'gabarito.py', 'w', encoding='utf-8')
    arq.write(f'gabarito = {gabarito}')
    arq.close()
    print('GABARITO GERADO...')

    return None


def gera_gabarito() -> dict[str: dict[tuple: tuple]]:
    """
    Essa função funciona de maneira análoga ao corretor. No entanto, aqui geramos o gabarito, que é uma das peças
    fundamentais da correção. Nele, tratamos os argumentos inseridos e preparamos tudo para que o gabarito seja usado
    como chave do processo de correção.

    Precisamos que, na pasta Gabarito, exista o arquivo funcoes_gabarito.py contendo as funções (funcionando
    corretamente) que retornarão os valores corretos esperados de cada exercício.

    Após criar o <dicionário> (variável), ela também cria o arquivo dicionario.py.
    :return: O dicionário gerado.
    """

    gabarito: dict[str: dict[tuple: tuple]] = {}
    if gerar_gabarito:
        try:
            for i, exercicio in enumerate(nomes_exercicios_input):

                gabarito[exercicio]: dict[tuple: tuple] = {}

                testes_ex = getattr(funcoes_gabarito, exercicio.replace('exercicio', 'teste'))

                # Não precisamos tirar as listas aqui, pois inputs deve ser uma lista.

                for teste in testes_ex:  # nos exerícios com input, teste é uma tupla com um iterável de argumentos e
                    # outro iterável de input
                    if type(teste[0]) is not tuple:
                        teste[0] = (teste[0],)  # o argumento deve sempre ser um iterável.
                    resultado = executa_scripts_1_teste_por_exercicio('Gabarito.funcoes_gabarito', exercicio, teste[0],
                                                                      teste[1])
                    gabarito[exercicio][(teste[0], tuple(teste[1]))] = resultado

            for j, exercicio in enumerate([exercicio_sem_input
                                           for exercicio_sem_input in nomes_exercicios if
                                           exercicio_sem_input not in nomes_exercicios_input]):

                gabarito[exercicio]: dict[tuple: tuple] = {}
                testes_ex = getattr(funcoes_gabarito, exercicio.replace('exercicio', 'teste'))

                testes_ex = tupladora(testes_ex)  # removemos as nested-lists

                # garantimos que os argumentos são iteráveis, caso haja alguma str, int, float, etc.
                for teste in testes_ex:
                    if type(teste) is not tuple:
                        teste = ((teste,),)
                    elif type(teste) is tuple and len(teste) == 0:  # tupla vazia
                        teste = (teste,)
                    elif type(teste) is tuple and type(teste[0]) is not tuple:
                        teste = (teste,)
                    elif type(teste) is tuple and len(teste) == 2 and type(teste[1]) is not list:
                        teste = (teste[0], list(teste[1]))

                    resultado = executa_scripts_1_teste_por_exercicio('Gabarito.funcoes_gabarito', exercicio,
                                                                      teste[0])
                    gabarito[exercicio][teste] = resultado
            print(gabarito)
            arq_gabarito(gabarito)

        except AttributeError:
            print('\n\nHá um erro fatal em gera_gabarito: \n', sys.exc_info())
            print(traceback.format_exc())

        except Exception:
            print('\n\nHá um erro fatal em gera_gabarito: \n', sys.exc_info())
            print(traceback.format_exc())
            print('argumento do erro: ', teste)

    else:
        print('Não é possível gerar um gabarito.')

    return gabarito


if not gerar_gabarito:
    print('Já existe um Gabarito. ')
