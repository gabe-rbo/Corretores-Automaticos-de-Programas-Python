from FCA.funcoes_de_correcao import executa_scripts_1_teste_por_exercicio
import multiprocessing
import os
from typing import Any, Iterable
import importlib
from pathlib import Path


# CONFIGURE ============================================================================================================
config: dict[str: Iterable[Any]] = {}
'''
Sobre dúvidas em como configurar o corretor individual: consulte o Manual de Uso dos Corretores Automáticos de Programas
Python. 
'''
# ======================================================================================================================

base: Path = Path(os.getcwd())
itens_cwd: list[str] = os.listdir(base)
itens_cwd.remove('CAPP_I.py')
itens_cwd.remove('FCA')
if 'Resultados.txt' in itens_cwd:
    itens_cwd.remove('Resultados.txt')
corrigir = False

if not itens_cwd:
    print('Não há arquivo python para ser corrigido. Encerrando execução...')
elif not config:
    print('O Corretor não foi configurado. Encerrando execução...')
else:
    nome_script: str = itens_cwd[0]

    if '.py' not in nome_script[-3:]:
        print(f'{nome_script} não é um arquivo .py. Encerrando execução...')
    else:
        try:
            script = importlib.import_module(f'{nome_script.replace('.py', '')}')
            corrigir = True
            print(f'Script encontrado: {nome_script}')
        except ImportError or ModuleNotFoundError as e:
            print('Não foi possível importar o arquivo.py.')
            print('Erro: ', e)
            corrigir = False

if corrigir:

    print('''
    >>> INICIANDO EXECUÇÃO <<<
    ''')

    resultados: str = ''
    pool = multiprocessing.Pool(processes=2)

    for nome_funcao in config:

        for teste in config[nome_funcao]:

            if len(teste) == 2:
                processo = pool.apply_async(executa_scripts_1_teste_por_exercicio,
                                            args=(nome_script.replace('.py', 'algo'), nome_funcao
                                                  , teste[0], list(teste[1])))
                inputs = f'Inputs: {list(teste[1])}'

            else:
                processo = pool.apply_async(executa_scripts_1_teste_por_exercicio,
                                            args=(nome_script.replace('.py', ''), nome_funcao,
                                                  teste[0], []))
                inputs = ''

            try:
                resultado = processo.get(timeout=1)
            except TimeoutError as e:  # entrou em loop para determinado teste.
                print(f'A função {nome_funcao} entrou em Loop para o teste: {teste}')
                resultado = (e, [])
                event = processo.__getstate__()['_event']
                event.set()

            resultados += f'''
            ============================================================================================================
            Função     : {nome_funcao}
            Argumentos : {teste[0]}
            ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            {inputs}
            Output : {resultado[0]}  |-> {type(resultado[0])}
            Prints : {resultado[1]}  |-> {type(resultado[1])}
            ............................................................................................................
            '''

    arq = open(base / 'Resultados.txt', 'w', encoding='utf-8')
    arq.write(resultados)
    arq.close()

print('''
    >>> EXECUÇÃO ENCERRADA <<<
''')
