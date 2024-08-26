def gia(entrada: list, semente: int) -> list:
    """
    Gerador de Intervalos Aleatórios (GIA):
        Função que gera números dentro de intervalos uma vez.
        Recebe uma lista contendo números e intervalos, na forma [total1, [inicio1, final1, step1], ...].
        Total representa a quantidade total de números que serão gerados, o intervalo representa àquele que eles
        pertencem.
        Se algo do intervalo for omitido, serão utilizadas variáveis padrões.
        No final, ela retorna uma lista, a qual contem listas de todos os números gerados nos respectivos intervalos.

    :param semente: Semente para randomização.
    :param entrada: Lista de entrada que a função recebe, contendo total e os intervalos.
    :return: Retorna um conjunto com os números todos aleatorizados.
    """

    import random

    # Semente para mesma randomização entre máquinas, a semente vem de uma função a qual envelopa a GIA
    random.seed(semente)
    lista_final = []

    # Configuração do intervalo padrão para quando for dado apenas a quantidade de números a qual se quer gerar
    inicio_padrao, final_padrao, step_padrao = 1, 101, 1

    for item in range(0, len(entrada)):
        gerar = False
        total, inicio, final, step = 0, inicio_padrao, final_padrao, step_padrao

        # Aqui inicia o parsing da entrada
        if item < len(entrada) - 1 and isinstance(entrada[item], int):
            if isinstance(entrada[item + 1], list):
                total = entrada[item]
                gerar = True
                # agora que há variáveis padrão, não é preciso checar para lista vazia.
                if len(entrada[item + 1]) == 1:
                    final = entrada[item + 1][0]
                    step += final + 1
                elif len(entrada[item + 1]) == 2:
                    inicio = entrada[item + 1][0]
                    final = entrada[item + 1][1]
                elif len(entrada[item + 1]) == 3:
                    inicio = entrada[item + 1][0]
                    final = entrada[item + 1][1]
                    step = entrada[item + 1][2]
                else:
                    print(f'A(s) entrada(s) {entrada[item]}, {entrada[item + 1]} geraram erro.')
                    gerar = False

            elif isinstance((entrada[item + 1]), int):
                total = entrada[item]
                gerar = True

        elif item == len(entrada) - 1 and isinstance((entrada[item]), int):
            total = entrada[item]
            gerar = True

        # aqui inicia o gerador
        lista_gerada = []

        if gerar:
            # limitador para os valores não passarem além de <final>
            limitador = inicio

            if step > len(range(inicio, final)):
                # Como o passo é maior, serão gerados <total> números
                # aleatórios no intervalo
                lista_gerada += random.sample(range(inicio, final), total)

            elif total > (final - inicio) // step:
                # Randomizador para valores normais
                numeros_por_intervalo = total // (final // step)

                for contador in range(0, (final - inicio) // step):
                    inicio_subintervalo = random.randrange(limitador, limitador + step, step)
                    limitador += step
                    lista_gerada += random.sample(range(inicio_subintervalo + 1, inicio_subintervalo + step),
                                                  numeros_por_intervalo)

            else:
                # O número total é menor que o número de intervalos.
                # Então, geramos normalmente para um número por intervalo,
                # mas escolhemos <total> números da lista no final.
                pre_lista = []

                for contador in range(0, (final - inicio) // step):
                    inicio_subintervalo = random.randrange(limitador, limitador + step, step)
                    limitador += step
                    n_aleatorio_sub = random.randint(inicio_subintervalo + 1, inicio_subintervalo + step)
                    # + 1, pois, em alguns casos, os intervalos se sobrepunham no elemento mínimo
                    pre_lista.append(n_aleatorio_sub)

                for i in range(0, total):
                    escolha = random.choice(pre_lista)
                    pre_lista.remove(escolha)
                    lista_gerada.append(escolha)

            lista_final.append(lista_gerada)

    return lista_final


def isr(geradora: list, rep: int = 0) -> list:
    """
    Inicializadora para Sequências com Repetição (ISR):
        Recebe uma lista do tipo rep*[n1, [inicio1, final1, step1], ...], sendo rep o número de vezes
        que se quer gerar números nos intervalos inseridos.
        Dada a lista, ela chama a função GIA (Geradora de Intervalos Aleatórios), r vezes.

        A função possui 2 funcionamentos:

        1) Caso a variável opcional <rep> tenha sido dada, ela repete a função gia com a lista geradora dada <rep>
        vezes, sem a necessidade do operador *.

        2) Caso a variável opcional <rep> não tenha sido dada, isso significa que estamos usando o operador * antes da
        lista. O operador * funciona antes da operação da função. Então, ela possui um parsing que funciona da
        seguinte maneira:
        Ela lê os primeiros dois elementos da entrada. Caso eles repitam sequencialmente, ela identifica que ali há
        uma repetição e identifica qual lista geradora está sendo repetida. Assim, ele termina de ler toda a sequência,
        contabilizando as repetições, para, depois, ativar a GIA quantas vezes o intervalo foi repetido.

    :param rep: Parâmetro opcional para repetição da geradora.
    :param geradora:  Lista a ser lida para a geração de números aleatórios. A lista pode conter intervalos da forma
        n, [inicio, final, step] e/ou n, [inicio, final] e/ou n, [final] e/ou n.
    :return: Retorna uma lista que possui listas, as quais representam os números gerados em cada repetição para os
        parâmetros repetidos.
    """

    from datetime import datetime
    import random

    # geramos uma semente para a GIA pegando apenas os números do instante dado por datetime.now
    agora = str(datetime.now())
    semente = int(agora.split('.')[-1])
    random.seed(semente)

    lista_final = []

    if rep != 0:
        for i in range(rep):
            lista_final.append(gia(geradora, semente))

    if rep == 0:
        rep = 1
        lista_geradora = []
        for i in range(2, len(geradora) - 1):

            if geradora[i] == geradora[0] and geradora[i + 1] == geradora[1] and rep == 1:
                # detectou uma repetição e ela é a primeira, então determina qual a é a lista que repete
                lista_geradora = geradora[0:i]
                rep += 1

            elif geradora[i] == geradora[0] and geradora[i + 1] == geradora[1] and rep > 1:
                rep += 1

        # agora que temos a lista e as repetições, podemos chamar a GIA e gerar o que queremos.
        for i in range(rep):
            lista_final.append(gia(lista_geradora, semente))

    return lista_final

'''
teste_a = 3*[10, [0, 100, 10], 5, [200, 400], 2, [30], 5, 6, [3, 4, 5, 6], 6]
teste_rep = [10, [0, 100, 10], 5, [200, 400], 2, [30], 5, 6, [3, 4, 5, 6], 6]

lista_a = isr(teste_a)
lista_rep = isr(teste_rep, 3)
print('-'*40, 'ISR', '-'*40,
      '\n--Com rep especificada, sem *:', lista_rep,
      '\n--Sem rep, com *:             ', lista_a,
      '\nElas têm o mesmo tamanho? ', len(lista_a) == len(lista_rep),
      '\nEstá funcionando normalmente.')
'''