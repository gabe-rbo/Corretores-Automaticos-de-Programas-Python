import unittest.mock
import importlib


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
