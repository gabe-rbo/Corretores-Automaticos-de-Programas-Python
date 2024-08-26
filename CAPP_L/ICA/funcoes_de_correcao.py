import CAPP_L.config as config
import importlib
import sys
from pathlib import Path
import unittest.mock

base = Path(str(config.BASE).replace(r'/CAPP_I_testes', ''))


def compara_respostas(gabarito: dict, respostas_script: dict, turma: str, nome_aluno: str) -> tuple:
    """
    Essa função compara as respostas obtidas pelos scripts dos alunos com o Gabarito.
    O resultado do script do aluno é transformado em um dicionário de chaves cujos nomes são os exercícios. Cada chave
    possui um dicionário associado, sendo cada uma delas os testes aplicados, assimiladas ao resultado retornado.
    Gabarito é de mesma estrutura.
    A chave da comparação está no gabarito, afinal é nele que está a iteração.

    Conforme compara as respostas, gera uma string característica contendo a correção daquele script.
    Depois, cria o arquivo de correção e o manipula de maneira devida vide os outros argumentos.

    :param gabarito: Gabarito.
    :param respostas_script: Dicionário de respostas do aluno para cada exercício
    :param turma: Opcional, turma pela qual o aluno pertence.
    :param nome_aluno: Opcional, nome do aluno.
    :return: Tupla, contendo nome, nota e acertos do script.
    """

    trials = 0
    for exercicio in gabarito:
        trials += len(gabarito[exercicio])
    nota_per_trial = round(100 / trials, 4)

    correcao = f'''   
    Aula: {config.NUM_AULA}.
    Correção de {nome_aluno}
    '''
    acertos = 0
    nota = 0.0

    tabela_acertos: dict[str: tuple] = {}  # dicionário contendo exercício associado ao número de testes e acertos

    for exercicio in gabarito:  # gabarito é a base de toda a iteração

        trials_ex = len(gabarito[exercicio])
        acertos_ex = 0

        for arg in gabarito[exercicio]:

            if len(arg) == 2:  # tem input

                if ((respostas_script[exercicio][arg])[0] == (gabarito[exercicio][arg])[0] and
                        (respostas_script[exercicio][arg])[1] == (gabarito[exercicio][arg])[
                            1]):  # compara os inputs e os prints

                    correcao += f'''
                    =====================================================================
                    >> {exercicio}
                    Argumentos       : {arg[0]}
                    Inputs           : {arg[1]}
                    ---------------------------------------------------------------------
                    Output Esperado  : {gabarito[exercicio][arg][0]} | {type(gabarito[exercicio][arg][0])}
                    Output Obtido    : {respostas_script[exercicio][arg][0]} | {type(respostas_script[exercicio][arg][0])}
                    +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    Prints Esperados : {gabarito[exercicio][arg][1]}
                    Prints Obtidos   : {respostas_script[exercicio][arg][1]}
                    ---------------------------------------------------------------------
                    Nota obtida      : {nota_per_trial}
                    '''

                    nota += nota_per_trial
                    acertos_ex += 1

                else:
                    correcao += f'''
                    =====================================================================
                    >> {exercicio}
                    Argumentos       : {arg[0]}
                    Inputs           : {arg[1]}
                    ---------------------------------------------------------------------
                    Output Esperado  : {gabarito[exercicio][arg][0]} | {type(gabarito[exercicio][arg][0])}
                    Output Obtido    : {respostas_script[exercicio][arg][0]} | {type(respostas_script[exercicio][arg][0])}
                    +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    Prints Esperados : {gabarito[exercicio][arg][1]}
                    Prints Obtidos   : {respostas_script[exercicio][arg][1]}
                    ---------------------------------------------------------------------
                    Nota obtida      : 0
                    '''

            else:  # não há input

                if respostas_script[exercicio][arg][0] == gabarito[exercicio][arg][0]:

                    correcao += f'''
                    =====================================================================
                    >> {exercicio}
                    Argumentos       : {arg}
                    ---------------------------------------------------------------------
                    Output Esperado  : {gabarito[exercicio][arg][0]} | {type(gabarito[exercicio][arg][0])}
                    Output Obtido    : {respostas_script[exercicio][arg][0]} | {type(respostas_script[exercicio][arg][0])}
                    +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    Prints           : {respostas_script[exercicio][arg][1]}
                    ---------------------------------------------------------------------
                    Nota obtida      : {nota_per_trial}
                    '''

                    nota += nota_per_trial
                    acertos_ex += 1

                else:
                    correcao += f'''
                    =====================================================================
                    >> {exercicio}
                    Argumentos       : {arg}
                    ---------------------------------------------------------------------
                    Output Esperado  : {gabarito[exercicio][arg][0]} | {type(gabarito[exercicio][arg][0])}
                    Output Obtido    : {respostas_script[exercicio][arg][0]} | {type(respostas_script[exercicio][arg][0])}
                    +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    Prints           : {respostas_script[exercicio][arg][1]}
                    ---------------------------------------------------------------------
                    Nota obtida      : 0
                    '''

        acertos += acertos_ex
        tabela_acertos[exercicio] = (trials_ex, acertos_ex, f'{round((acertos_ex / trials_ex), 4) * 100}%')

    correcao += f'''
    =====================================================================
    >>> ACERTOS     : {acertos} / {trials}
    >>> NOTA FINAL  : {round(nota, 4)}
    
'''

    correcao += f"{'Exercício': <20}{'Testes' : <10}{'Acertos': <10}{'Porcentagem': <20}\n"
    correcao += "+++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
    for exercicio in tabela_acertos:  # Criamos a tabela do final da correção
        correcao += f"{exercicio : <20}{tabela_acertos[exercicio][0] : <10}{tabela_acertos[exercicio][1] : <10}{tabela_acertos[exercicio][2] : <20}\n"

    try:  # Criamos o arquivo de correção com base no que foi dado nos argumentos da função
        arq = open(Path(fr'{base}/Alunos/{turma}/Correção/{nome_aluno}.txt'), 'w', encoding='utf-8')
        arq.write(correcao)
        arq.close()
    except OSError:
        print(fr'Não foi possível criar o arquivo: {base}\Alunos\{turma}\{nome_aluno}.txt\n'
              f'DESCRIÇÃO DO ERRO: {sys.exc_info()}')

    return nome_aluno, f'{round(nota, 4)}', f'{acertos}/{trials}'


def executa_scripts_1_teste_por_exercicio(script: str, nome_funcao: str, teste, inputs=None) -> tuple:
    """
    Essa função é utilizada pelo CAPP_L para obter os resultados das funções dos alunos, capturando retornos ou erros,
    juntamente ao que é printado durante a execução.

    1) Dado o caminho para o Script, importamos-o usando importlib.
    2) Dado o nome da função, obtemos ela enquanto atributo do script.
    3) O iterável <teste>, passado como argumento, é utilizado como argumento da função do aluno.
    4) O iterável <inputs>, caso haja, será aplicados na função.
    5) A função retorna o que foi obtido dessa triagem, em forma de Tupla.

    :param script: É o caminho para importarmos o arquivo .py do aluno, sem a extensão do arquivo. Ex: Alunos.TX.Scripts.nome_do_aluno
    :param nome_funcao: Nome da função que desejamos importar para testá-la.
    :param teste: Deve ser um iterável de algum tipo.
    :param inputs: Opcional, deve ser um iterável de algum tipo. Utilizar apenas caso a função tenha inputs.
    :return: Retorna uma tupla contendo retorno da função do aluno para dado teste ou o erro obtido, juntamente ao que
             foi printado durante a execução
    """

    prints = []
    erro = ''
    try:
        py_code = importlib.import_module(script)
        funcao = getattr(py_code, nome_funcao)

        if inputs:

            with unittest.mock.patch(target='builtins.input', side_effect=inputs):
                with unittest.mock.patch(target='builtins.print', side_effect=lambda s: prints.append(s)):
                    resultado = funcao(*teste)

        else:
            with unittest.mock.patch(target='builtins.print', side_effect=lambda s: prints.append(s)):
                resultado = funcao(*teste)

    except Exception as e:
        erro = e

    if erro:
        retorno = (erro, prints)
    else:
        retorno = (resultado, prints)

    return retorno
