import os
import pathlib
import fnmatch
import sys
import traceback
from nbconvert.exporters import PythonExporter
import re
from zipfile import ZipFile

base = pathlib.Path(os.getcwd().replace(r'\Arquivos', '').replace(r'\ICA', ''))  # cwd
print(base)
arquivos_da_base = os.listdir(base)
roteiro = {}  # {'T_': (conversão, correção), ...} Dicionário que dita o que fazer com cada turma


def cria_dirs(caminhos: str | list | pathlib.Path, sub_dir: str = None) -> None:
    """
    Parameters
    ----------
    caminhos: str | list, pode ser uma string contendo o caminho do novo diretório, ou uma lista contendo o caminho de
    vários que se deseja criar simultaneamente.
    sub_dir: str, nome do subdiretório que deseja se criar dentro do caminho. Usar apenas quando caminho é str.

    Returns
    -------
    """

    if caminhos is list:

        for caminho in caminhos:

            try:
                os.makedirs(caminho, exist_ok=False)
            except FileExistsError or OSError:
                print(f'O diretório {caminho} já existe!')

    else:

        try:
            os.makedirs(pathlib.Path(caminhos), exist_ok=False)

        except FileExistsError or OSError:
            print(f'O diretório {caminhos} já existe!')

    if sub_dir is not None:

        try:
            os.makedirs(pathlib.Path(caminhos) / sub_dir, exist_ok=False)

        except FileExistsError or OSError:
            print(f'O diretório {caminhos}/{sub_dir} já existe ou não pode ser criado!')

    return None


def diretorio_vazio(diretorio: str | pathlib.Path) -> bool:
    """

    Parameters
    ----------
    diretorio: str, caminho para o diretório.

    Returns
    -------
    True, se estiver vazio.
    False, se não estiver vazio.

    """

    if not os.listdir(pathlib.Path(diretorio)):
        vazio = True
    else:
        vazio = False

    return vazio


def conversora_nb2py(notebook: pathlib.Path) -> None:
    """
    Converte o Notebook.ipynb para Script.py
    Método de conversão descoberto por José de Siqueira.

    Parameters
    ----------
    notebook: caminho do notebook que se deseja converter.

    Returns
    -------

    """

    py = str(notebook).replace('.ipynb', '.py').replace('Notebooks', 'Scripts')

    try:
        PythonExporter.exclude_raw = True
        PythonExporter.exclude_markdown = True
        PythonExporter.exclude_unknown = True
        (source, meta) = PythonExporter().from_filename(str(notebook))
        with open(py, 'w', encoding='utf-8') as outfile:
            outfile.write(source)
        outfile.close()

    except:  # Modificar a exceção

        txt = pathlib.Path(str(notebook).replace('.ipynb', '.txt'))
        os.rename(notebook, txt)  # transformo o notebook em txt
        linhas_notebook = open(txt, 'r', encoding='utf-8').readlines()

        apagar = False
        for i, linha in enumerate(linhas_notebook):

            if '"cell_type": "raw"' in linha:  # encontro a célula raw
                apagar = True
                linhas_notebook[i - 1] = ''

            if apagar and linha == '  },\n':  # final da célula raw
                linhas_notebook[i] = ''
                apagar = False

            elif apagar:
                linhas_notebook[i] = ''  # vou apagando as linhas

        nome_notebook_sem_raw = pathlib.Path(
            str(notebook).replace(f'Notebooks', 'Outros').replace('.ipynb', 'SEM_RAW.ipynb'))
        with open(nome_notebook_sem_raw, 'w', encoding='utf-8') as novo_notebook:
            for linha in linhas_notebook:
                novo_notebook.write(linha)  # salvo o notebook sem raw na pasta OUTROS da mesma turma

        try:
            (source, meta) = PythonExporter().from_filename(str(nome_notebook_sem_raw))
            with open(py, 'w', encoding='utf-8') as outfile:
                outfile.write(source)

        except:
            print(f'Não foi possível converter o notebook: {nome_notebook_sem_raw}')
            print(f'Erro: {sys.exc_info()[0]}\n {sys.exc_info()[1]}\n')
            print(f'{traceback.format_exc()}\n')

            cria_dirs(base/'Alunos'/f'{turma}'/'Intercorrencias')
            arq = open(base/'Alunos'/f'{turma}'/'Intercorrencias/Erros_Conversao.txt', 'w', encoding='utf-8')
            arq.write(f'''
            Não foi possível converter o notebook: {nome_notebook_sem_raw}')
            print(f'Erro: {sys.exc_info()[0]}\n {sys.exc_info()[1]}\n')
            print(f'{traceback.format_exc()}\n'
            ''')
            arq.close()

        os.rename(txt, notebook)

    return None


def unzipadora_turma(lista_turmas: list[str]) -> None:
    """
    Dá unzip nas turmas listadas.
    Cria Notebooks, Scripts, Outros e as sub-pastas de turmas em Alunos.
    Adiciona no roteiro quais turmas devem ser corrigidas, convertidas ou nada a ser feito.
    Para utilizar isso, precisamos primeiro, unzipar o Script para a pasta Alunos, após isso, colocamos a lista de
    turmas unzipadas como argumento desta função, para que ela crie e modifique os arquivos.

    Parameters
    ----------
    lista_turmas: Lista de turmas que foram unzipadas para Alunos e devem ser devidamente tratadas

    Returns
    -------
    None

    """

    for turma in lista_turmas:

        notebooks_turma, scripts_turma, outros_arq_turma = [], [], []

        for pasta_submissao in os.listdir(base / 'Alunos' / turma):
            # vamos tirar os brancos dos nomes das pastas
            novo_nome = str(pasta_submissao).replace(' ', '_')
            os.rename(base / 'Alunos' / turma / pasta_submissao, base / 'Alunos' / turma / novo_nome)

            # Vemos os arquivos dentro da pasta de submissão
            arquivos_submetidos = os.listdir(base / 'Alunos' / turma / novo_nome)

            problema = False
            if len(arquivos_submetidos) == 1:  # aluno submeteu um arquivo, entramos a extensao
                nome_arquivo_submetido: str = arquivos_submetidos[0]
                indice_extensao = str(nome_arquivo_submetido[::-1]).find('.')
                extensao = '.' + nome_arquivo_submetido[(len(arquivos_submetidos) - indice_extensao - 1):]
                nome_arquivo = nome_arquivo_submetido[:(len(nome_arquivo_submetido) - indice_extensao) - 1]

            elif len(arquivos_submetidos) > 1:  # aluno submeteu mais de um arquivo, pegamos o mais recente.

                tempo_criacao = {}
                for arquivo in arquivos_submetidos:
                    tempo_criacao[base / 'Alunos' / turma / novo_nome / arquivo] = (
                        os.path.getctime(base / 'Alunos' / turma / novo_nome / arquivo))
                tempo_mais_recente = max(tempo_criacao.values())
                arquivo_mais_recente = list(filter(lambda x: tempo_criacao[x] == tempo_mais_recente, tempo_criacao))[0]
                # solução encontrada em https://www.geeksforgeeks.org/python-get-key-from-value-in-dictionary/

                # encontramos a extensao
                nome_arquivo_submetido = str(arquivo_mais_recente)
                indice_extensao = str(nome_arquivo_submetido[::-1]).find('.')
                extensao = '.' + nome_arquivo_submetido[(len(arquivos_submetidos) - indice_extensao - 1):]
                nome_arquivo = nome_arquivo_submetido[:(len(nome_arquivo_submetido) - indice_extensao - 1)]

            else:
                print(f'Não há arquivos submetidos em {base} / Alunos / {turma} / {novo_nome}')
                problema = True

            if not problema:
                # sabemos que o nome do aluno está escrito até o underscore antes do primeiro número, exemplo:
                # Nome_Aluno_348130_assignsubmission_file_ (pasta da submissao do aluno)
                posicao_primeiro_numero = re.search(r'\d', novo_nome)
                try:
                    nome_aluno = novo_nome[:posicao_primeiro_numero.start() - 1] + extensao  # -1 para não pegarmos o _
                except AttributeError:  # posicao_primeiro_numero é None
                    nome_aluno = novo_nome + extensao

                notebook_submetido = os.listdir(base / base / 'Alunos' / turma / novo_nome)[0]
                # só pode submeter um notebook

                # aproveitamos para já retirar esse notebook da pasta da submissão
                os.rename(base / base / 'Alunos' / turma / novo_nome / notebook_submetido,
                          base / base / 'Alunos' / turma / nome_aluno)

                # Pegamos quais arquivos são .ipynb, .py e outros

                if extensao == '.ipynb':
                    notebooks_turma += [(base / 'Alunos' / turma / nome_aluno,
                                         base / 'Alunos' / turma / 'Notebooks' / nome_aluno)]
                elif extensao == '.py':
                    scripts_turma += [(base / 'Alunos' / turma / nome_aluno,
                                       base / 'Alunos' / turma / 'Scripts' / nome_aluno)]
                else:
                    outros_arq_turma += [(base / 'Alunos' / turma / nome_aluno,
                                          base / 'Alunos' / turma / 'Outros' / nome_aluno)]

            # agora vamos apagar as pastas vazias
            for arquivo_nao_recente in os.listdir(base / 'Alunos' / turma / novo_nome):
                try:
                    os.remove(base / 'Alunos' / turma / novo_nome / arquivo_nao_recente)
                except FileNotFoundError:
                    pass
            os.rmdir(base / 'Alunos' / turma / novo_nome)  # vai estar vazia pois tiramos a unica submissao

        # agora que descompactamos os arquivos e modificamos seus nomes, criaremos as pastas Notebooks, Scripts e
        # Outros.
        for pastas in ['Notebooks', 'Scripts', 'Outros', 'Correção']:
            cria_dirs(base / 'Alunos' / turma / pastas)

        for arquivo in notebooks_turma:
            os.rename(arquivo[0], arquivo[1])
        for arquivo in scripts_turma:
            os.rename(arquivo[0], arquivo[1])
        for arquivo in outros_arq_turma:
            os.rename(arquivo[0], arquivo[1])

        if scripts_turma:  # a turma possui scripts
            roteiro[turma] = (False, True)  # False para conversão, True para correção
            print(f'>>>AVISO: {turma} possui Scripts. Não será feita a conversão para essa turma.')

        elif notebooks_turma:  # turma não possui Scripts, mas possui notebooks
            roteiro[turma] = (True, False)  # True para a conversão, True para correção
            print(f'>>>AVISO: {turma} não possui Scripts. Convertendo Notebooks...')

        else:
            print(f'Não é possível corrigir nem converter notebooks ou scripts para a turma {turma}')

    return None


# verificando se há arquivo zip:
arquivos_zip = [pathlib.Path(str(arquivo)) for arquivo in arquivos_da_base if fnmatch.fnmatch(arquivo, '*.zip')]
if arquivos_zip:  # há arquivo(s) zip
    turmas = []  # pega as turmas em zip
    for i, arquivo_zip in enumerate(arquivos_zip):
        indice_T = str(arquivo_zip).find('_T')
        indice_Aula = str(arquivo_zip)[indice_T:].find('-') + indice_T
        turmas += [str(arquivo_zip)[indice_T:indice_Aula].replace('_', '')]

        # muda o nome do arquivo zip para o nome da turma. Não é preciso, trás muitos problemas.
        # os.rename(base / arquivo_zip, pathlib.Path(str(base / turmas[i]) + '.zip'))
        # arquivos_zip[i] = pathlib.Path(str(base / turmas[i]) + '.zip')
print(arquivos_zip)

# Caso 1 - Há alunos, mas não há arquivo zip.
if 'Alunos' in os.listdir(base) and pathlib.Path.is_dir(base / 'Alunos') and not arquivos_zip:
    print('Alunosarquivos_BETA  existe! Buscando turmas...')

    turmas_alunos = [turma for turma in os.listdir(base / 'Alunos') if turma[0] == 'T']
    print(f'Foram encontradas as seguintes turmas: {turmas_alunos}')

    for turma in turmas_alunos:

        sub_dirs_turma = os.listdir(base / 'Alunos' / f'{turma}')  # lista que terá ou Notebooks ou Scripts.

        if 'Scripts' in sub_dirs_turma and not diretorio_vazio(base / 'Alunos' / f'{turma}' / 'Scripts'):
            # Se há Scripts, a correção é obrigatória e não haverá conversão de notebooks para a turma.
            roteiro[base / 'Alunos' / f'{turma}'] = (False, True)

        elif ('Notebooks' in sub_dirs_turma and not diretorio_vazio(base / 'Alunos' / f'{turma}' / 'Notebooks') and
              diretorio_vazio(base / 'Alunos' / f'{turma}' / 'Scripts')):
            print(f'Há Notebooks, mas não há Scripts. Os Notebooks da turma {turma} serão corrigidos. ')
            roteiro[base / 'Alunos' / f'{turma}'] = (False, True)

    # isso verifica quais turmas deve ocorrer conversão e correção.

# Caso 2 - Há arquivo zip, mas não há alunos
elif 'Alunos' not in os.listdir(base) and arquivos_zip:

    for turma in turmas:  # turma não é referenciada antes da designação, neste caso estamos assumindo que turmas existe
        cria_dirs(base / 'Alunos' / turma)

    # Neste caso, a conversão e correção é executada para todas as turmas.

    # Primeiro vamos unzipar os arquivos zip
    for i, arquivo_zip in enumerate(arquivos_zip):
        zip = ZipFile(arquivo_zip, 'r')
        zip.extractall(path=base / 'Alunos' / turmas[i])

    unzipadora_turma(turmas)

# Caso 3 - Há alunos e há arquivo zip
elif 'Alunos' in os.listdir(base) and arquivos_zip:

    # Como há ambos, iremos converter apenas as turmas que não existem em Alunos.
    turmas_alunos = [turma for turma in os.listdir(base / 'Alunos')]
    turmas_zip = turmas

    turmas_para_unzipar = []
    for turma_zip in turmas_zip:
        if turma_zip not in turmas_alunos:
            print('Turma Zipada Incondizente: ', turma_zip)
            turmas_para_unzipar.append(turma_zip)
    print('Turmas ZIP', turmas_zip, 'Turmas Alunos', turmas_alunos)

    if not turmas_para_unzipar:
        print('Todas as turmas zipadas condizem com as em alunos.')
    else:
        print('Turmas para Unzipar: ', turmas_para_unzipar)
        for turma in turmas_para_unzipar:
            cria_dirs(base / 'Alunos' / turma)

            for arquivo_zip in arquivos_zip:
                if turma in str(arquivo_zip):  # pegamos o arquivo zip que condiz com a turma não unzipada
                    zip = ZipFile(arquivo_zip, 'r')
                    zip.extractall(path=base / 'Alunos' / turma)

        unzipadora_turma(turmas_para_unzipar)

    # Precisamos verificar quais Turmas tem Notebook e Scripts.

    for turma in os.listdir(base / 'Alunos'):

        if os.listdir(base / 'Alunos' / turma / 'Scripts'):  # Há Scripts
            roteiro[turma] = (False, True)
        elif os.listdir(base / 'Alunos' / turma / 'Notebooks'):  # Há notebooks e não há scripts
            roteiro[turma] = (True, True)
        else:
            print(f'Não há nem notebooks nem scripts para {turma}')


# Caso 4 - Não há alunos nem zip
else:
    print('Não há Alunos nem arquivo Zip. Terminando execução...')

print(roteiro)

'''
Conversão de Notebooks para Scripts das Turmas cujo roteiro admite correção.
Como aqui o tratamento da pasta Alunos acabou, podemos percorrer ela para acessar o roteiro de cada turma.
'''

if roteiro != {}:  # roteiro não é um dicionário vazio

    for turma in os.listdir(base / 'Alunos'):
        if roteiro[turma][0]:  # Converter é True.
            print(f'''>>>CONVERTENDO NOTEBOOKS DE {turma}<<<''')
            for notebook in os.listdir(base / 'Alunos' / turma / 'Notebooks'):
                # print(base / 'Alunos' / turma / 'Scripts' / notebook)
                conversora_nb2py(base / 'Alunos' / turma / 'Notebooks' / notebook)

            if not os.listdir(base / 'Alunos' / turma / 'Scripts'):
                print(f'Não foi possível converter nenhum Notebook da turma {turma}.\n'
                      'Não será possível corrigir nenhum arquivo da turma.')
                roteiro[turma] = (False, False)
            else:
                roteiro[turma] = (False, True)

        print('''>>>PREPARANDO ESTATÍSTICAS<<<''')
        if roteiro[turma][1]:  # Corrigir é True. Afinal, só podemos gerar estatísticas de turmas corrigidas.
            cria_dirs(base / 'Estatisticas' / turma / 'CSVs')

    print('''>>>NOTEBOOKS CONVERTIDOS <<<''')


print(roteiro)

exec()