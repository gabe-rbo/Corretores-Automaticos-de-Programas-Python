from ICA.funcoes_de_correcao import compara_respostas, executa_scripts_1_teste_por_exercicio
from multiprocessing import cpu_count, Process, Pool, Pipe, TimeoutError
from Arquivos.Arquivos import roteiro, cria_dirs
import os
from pathlib import Path
import config
import random
import time

# GERAÇÃO GABARITO =====================================================================================================
tipo_geracao_gab: str = 'n'  # 'n', para geração normal, 'a' para geração aleatória. Por omissão, é 'n'
# ======================================================================================================================

base = Path(config.BASE)

if __name__ == '__main__':
    """
    É aqui onde o a correção em Lotes acontece. 
    Utilizamos da biblioteca Multiprocessing para corrigir vários scripts ao mesmo tempo usando pool e apply_async.
    Caso os scripts apresentarem Loop, paramos a Thread usando ThreadingEvent().set()
    """

    p = Pool(min(cpu_count(), 61))

    if 'gabarito.py' not in os.listdir(base / 'CAPP_I'):
        print('O CAPP-L não encontrou um gabarito. Um será criado.')

        if tipo_geracao_gab == 'a':
            from Gabarito.geradora_de_gabaritos_aleatorios import geradora_de_gabaritos_aleatorios, sementes, corrigir
            gabaritos_aleatorios = geradora_de_gabaritos_aleatorios()
        else:
            from Gabarito.gera_gabarito import gera_gabarito, corrigir
            gabarito = gera_gabarito()
    else:
        if tipo_geracao_gab == 'a':
            from Gabarito.geradora_de_gabaritos_aleatorios import corrigir
            arq_gab_aleatorios = open(base / 'CAPP_I' / 'gabarito.py')
            linhas = arq_gab_aleatorios.readlines()
            gabaritos_aleatorios = {}
            sementes = []
            for linha in linhas:
                semente = linha[linha.find('_')+1:linha.find(' =')]  # achamos as sementes nos arquivos
                gabarito_aleatorio = eval(linha[linha.find(' =') + 3:])  # pegamos o gabarito
                gabaritos_aleatorios[semente] = gabarito_aleatorio
                sementes.append(semente)
        else:
            from Gabarito.gera_gabarito import corrigir  # para ver se foi possível criar gabarito.
            from ICA.gabarito import gabarito
            print(gabarito)

    if corrigir:

        scripts_todas_turmas = []
        for turma in roteiro:  # roteiro nos dá quais turmas devem ser corrigidas.

            if turma[1]:
                # vamos corrigir

                # começamos tratando os argumentos para importação.
                alunos_scripts: list[tuple] = []
                scripts_aluno_turma = []
                for script in os.listdir(Path(fr'{base}/Alunos/{turma}/Scripts')):
                    if '__pycache__' not in script:
                        scripts_aluno_turma += [
                            (fr'Alunos.{turma}.Scripts.' + script.replace('.py', ''),
                             script.replace('.py', ''), turma)]

                roteiro[turma] = (False, False)  # Pois a turma já foi/será corrigida.

                scripts_todas_turmas += [scripts_aluno_turma]
                print(scripts_todas_turmas)

        print(f'''
            >>> INICIANDO CORREÇÃO EM LOTES... <<<
            ''')
        t_inicial_correcao = time.time()

        alunos_notas_acertos: list[tuple] = []  # para juntarmos os alunos, notas e acertos em um único arquivo.
        for script_turma in scripts_todas_turmas:

            # um processo por teste
            alunos_notas_acertos: list[tuple[str, str, str]] = []  # tupla da forma (nome_aluno, nota, acertos)

            for script_aluno in script_turma:

                respostas_aluno = {}

                if tipo_geracao_gab == 'a':
                    semente_escolhida = random.choice(sementes)
                    gabarito = gabaritos_aleatorios[str(semente_escolhida)]  # pegamos um dos gabaritos gerados

                for exercicio in gabarito:

                    respostas_aluno[exercicio] = {}

                    for teste in gabarito[exercicio]:
                        if len(teste) == 2:  # tem input
                            processo = p.apply_async(executa_scripts_1_teste_por_exercicio,
                                                     args=(script_aluno[0], exercicio, teste[0],
                                                           list(teste[1])))
                        else:  # não tem input
                            processo = p.apply_async(executa_scripts_1_teste_por_exercicio,
                                                     args=(script_aluno[0], exercicio,
                                                           teste[0], []))

                        try:
                            resultado = processo.get(timeout=0.5)
                        except TimeoutError as e:  # entrou em loop para determinado teste.
                            print('Um script entrou em Loop para: ', teste, '\nTempo de execução: ',
                                  time.time() - t_inicial_correcao)
                            resultado = (e, [])
                            event = processo.__getstate__()['_event']
                            event.set()  # isso para a thread que entrar em Loop.
                        respostas_aluno[exercicio][teste] = resultado

                alunos_notas_acertos += (compara_respostas(gabarito, respostas_aluno, script_aluno[2], script_aluno[1]),)

            turma = script_turma[0][2]

            # Arquivo para o professor saber as notas dos alunos mais facilmente
            arq_prof = open(base / 'Alunos' / f'{turma}' / 'Notas_dos_Alunos.txt', 'w', encoding='utf-8')
            arq_prof.write(f'Correção dos Alunos da Turma {turma}\n')
            arq_prof.write(f"{'Nome': <50}{'Nota': ^20}{'Acertos': ^8}\n")

            # Arquivo da tabela CSV da turma apra determinada aula
            arq_estatistica = open(base / 'Estatisticas' / f'{turma}' / 'CSVs' / f'{config.NUM_AULA}.txt', 'w',
                                   encoding='utf-8')
            arq_estatistica.write('Nome;Nota;Acertos\n')

            for nome_nota_acertos in alunos_notas_acertos:
                arq_prof.write(f"{nome_nota_acertos[0]: <50}{nome_nota_acertos[1]: ^20}{nome_nota_acertos[2]: ^8}\n")
                arq_estatistica.write(f"{nome_nota_acertos[0]};{nome_nota_acertos[1]};{nome_nota_acertos[2]}\n")

        print('\n\n>>>>>>>> TEMPO DE DURAÇÃO DA CORREÇÃO: ', time.time() - t_inicial_correcao)

    else:
        print('NÃO HÁ COMO CORRIGIR POR AUSÊNCIA DE GABARITO...')

    p.close()

    print(f'''
        >>> CORREÇÃO EM LOTES FINALIZADA <<<
        ''')
