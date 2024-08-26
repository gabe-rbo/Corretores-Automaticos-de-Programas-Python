# -*- coding: utf-8 -*-
"""
Created on Fri Jun 25 11:30:35 2021

@author: José de Siqueira

Versão 1.9.2 de gera_nomes_com_subniveis a partir da lista de exercícios,que nomesolve o pro-
blema de geração de nomes para qualquer número de subnveis e nomesolve outros
problemas.
Estado: 25/6/2021: funcionando

ex: [1, [2], [3], [4], 5, 6, 7, [1], [1], [1], 9, [5, 6], 10]
coleta_subniveis: [(['1'], [[2], [3], [4]]), (['5', '6', '7'], [[1], [1], [1]]),
                   (['9'], [[5, 6]]), (['10'], [])]
gera_nomes_com_subniveis:
['1_1_1_1', '1_1_1_2', '1_1_1_3', '1_1_1_4', '1_1_2_1', '1_1_2_2', '1_1_2_3',
 '1_1_2_4', '1_1_3_1', '1_1_3_2', '1_1_3_3', '1_1_3_4', '1_2_1_1', '1_2_1_2',
 '1_2_1_3', '1_2_1_4', '1_2_2_1', '1_2_2_2', '1_2_2_3', '1_2_2_4', '1_2_3_1',
 '1_2_3_2', '1_2_3_3', '1_2_3_4', '5', '6', '7_1_1_1', '9_5', '9_6', '10']
"""


def coleta_nomes_e_subniveis(exercicios: list[int, list]) -> list[tuple[[list[str], list[int]]]]:
    """
    Coleta todos os nomes na lista de exercícios, coleta todas as listas de
    subniveis seguidas aos nomes.

    Parameters
    ----------
    exercicios: [int,[int]] 
    Lista de exercícios e seus subníveis
    
    Returns
    -------
    [([str],[int])]: nomes de exercícios sem subníveis (1) e os subníveis (2)
    para cada nome.

    """
    i = 0
    res = []

    # original:

    '''
    while i < len(exercicios):
        nomes = []
        subniveis = []
        while i < len(exercicios) and type(exercicios[i]) is int:
            # coleta todos os inteiros até encontrar uma lista
            nomes += [str(exercicios[i])]
            i += 1
        # i indica a posição da primeira lista de subníveis
        while i < len(exercicios) and type(exercicios[i]) is list:
            # coleta todos as listas até encontrar um int ou terminar exercicios
            subniveis += [exercicios[i]]
            i += 1
        res += [(nomes,subniveis)]
    '''


    # Outra maneira por Gabriel Ribeiro
    nomes = []
    subniveis = []
    for i in range(len(exercicios)):

        if type(exercicios[i]) is int:
            # coleta os inteiros
            nomes += [str(exercicios[i])]

        elif type(exercicios[i]) is list:
            # coleta as listas
            subniveis += [exercicios[i]]

        if i == len(exercicios) - 1:
            # para o final da lista, colocando aqui evitamos 1 comparação a mais na próxima cláusula elif.
            res += [(nomes, subniveis)]
            nomes, subniveis = [], []

        elif type(exercicios[i]) is list and type(exercicios[i+1]) is int:
            # lista seguida de inteiro
            res += [(nomes, subniveis)]
            nomes, subniveis = [], []

    return res

# ex = [1, [2], [3], [4], 5, 6, 'a', 7, [1],[1],[1], 9,[5,6],10]
# print(f'ex: {ex} coleta_subniveis: {coleta_nomes_e_subniveis(ex)}')
# ex: [1, [2], [3], [4], 5, 6, 7, [1], [1], [1], 9, [5, 6], 10] coleta_subniveis: [(['1'], [[2], [3], [4]]), (['5', '6', '7'], [[1], [1], [1]]), (['9'], [[5, 6]]), (['10'], [])]


def gera_nomes_com_subniveis(nomes_e_subniveis):
    """
    A partir da lista de nomes e subníveis, gera os nomes com todos os subní-
    veis e retorna uma lista só com os nomes de todos exercícios segundo os
    nomes e subníveis passados.

    Parameters
    ----------
    nomes_e_subniveis : [(str,[[int]])]
        Dada a lista de exercícios [1, [2], [3], [4], 5, 6, 7, [8], 10], gera
        a correspondente lista de nomes e sublistas, que é esse parâmetro:
        [(['1'], [[2], [3], [4]]), (['5', '6', '7'], [[8]]), (['10'], [])]
        Observe que o nome de um exercício com subníveis é sempre o último
        elemento da lista de nomes.

    Returns
    -------
    [str] com todos os nomes de exercícios gerados a partir da lista de
    noems e subníveis.

    """

    def gera_todos_nomes(nome, subniveis):
        """
        Dado um nome e uma lista de subniveis ([int]), gera todos os nomes a
        partir do nome com todos os subniveis passados.
    
        Parameters
        ----------
        nome : str
            Nome do exercício para o qual se quer gerar os subniveis.
        subniveis : [[int]]
            Lista de [int] ou [int,int], indicando quantos subniveis o nome 
            deve ter ([int]) ou o início e o fim ([int,int]) dos subníveis que
            o nome deve ter.
    
        Returns
        -------
        [str]
        """
        def gera_nome(nomes,nivel):
            """
            Gera uma lista de strings com os nomes formados a partir da lista
            com os nomes nome passada como argumento e para todo o nivel
            indicado.
    
            Parameters
            ----------
            nome : [str]
                prefixo dos exercicios com os subníveis.
            nivel : [int]
                Subnível.
            Returns
            -------
            [str]
            """

            res = []
            ini = 0
            fim = 0

            for nome in nomes:
                nome_ = nome+'_'
                if len(nivel) == 0:
                    return [nome]
                elif len(nivel) == 1:
                    ini = 1
                    fim = nivel[0]
                elif len(nivel) == 2:
                    ini = nivel[0]
                    fim = nivel[1]
                for i in range(ini,fim+1):
                    res += [nome_+f'{i}']

            return res  # gera_nome

        if not subniveis:  # subníveis é uma lista vazia
            nn = gera_nome([nome], subniveis)

        else:
            nn = gera_nome([nome], subniveis[0])

            for nivel in subniveis[1:]:
                nn = gera_nome(nn, nivel)

        return nn  # gera_todos_nomes
    
    res = []
    for (nomes, subniveis) in nomes_e_subniveis:
        nome = nomes[-1]
        res += nomes[:-1]
        res += gera_todos_nomes(nome,subniveis)
    
    return res  # gera_nomes_com_subniveis
    
    
#ex = [1,[2], [3], [4]]
#ex = [1, [2], [3], [4], 5, 6, 7, [1],[1],[1], 9,[5,6],10]
#ex = [10]
#ex = [5,[2],5,[4,5]]
#print(gera_nomes_com_subniveis(coleta_nomes_e_subniveis(ex)))

def gera_nomes(nome,exercicios):
    """
    Essa é o wrapper das funções que coletam nomes e subniveis dos exercicios
    para passar como argumento de gera_nomes_com_subniveis.
    
    Parameters
    ----------
    exercicios : [int,[int]]
        .

    Returns
    -------
    [str]

    """
    res = []
    nomes = gera_nomes_com_subniveis(coleta_nomes_e_subniveis(exercicios))
    for n in nomes:
        res += [nome+n]
    return res

# ex = [1, [2], [3], [4], 5, 6, 7, [1],[1],[1],[1],[1], 9,[5,6],10]
# ex = [10]
# ex = [1,[2],2,4,[9],[2],4,[10,10],4,[11,12],[2]]
# ex = [1, [2, 3], [4]]
# print(gera_nomes('teste_', ex))

