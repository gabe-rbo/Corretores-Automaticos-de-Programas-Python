import random


def gas(n: int, modo: str, palindromo: bool = False, semente: int = 0) -> str:
    """
    Geradora Aleatória de Strings (GAS):
        Essa geradora é especializada em gerar strings de maneira aleatória.

    :param n: Número de caracteres aleatórios que se deseja gerar.
    :param modo: Modo de geração, é uma concatenação de Strings:
        1) ''     -> A string vazia configura a geração para misturar letras maiúsculas e minúsculas.
        2) 'm'    -> Apenas letras minúsculas na string gerada.
        3) 'M'    -> Apenas letras maiúsculas na string gerada.
        4) '+[]'  -> Todas as strings dentro de [] serão colocadas, em ordem aleatória, na string gerada.
        Exemplo: '+['abc', 'igh]' -> A string gerada possuirá letras maiúsculas e minúsculas, e conterá 'abc' e 'igh'.
    :param palindromo: Se for True, a string gerada será um palíndromo.
    :param semente: Opcional, se não for informado será 0.
    :return: Retorna a string gerada de modo aleatório.
    """

    random.seed(semente)

    minusculas = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                  'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

    maiusculas = [letra.upper() for letra in minusculas]

    maiusculas_e_minusculas = maiusculas + minusculas

    if palindromo:

        modos = modo.split('+')

        if n % 2 == 0:
            string_metade = gas(n // 2, modo=modo, palindromo=False, semente=semente)
            string = string_metade + string_metade[::-1]
        else:
            string_metade = gas(n=n // 2, modo=modo, palindromo=False, semente=semente)
            caracter_meio = gas(n=1, modo=modos[0], palindromo=False, semente=semente)

            string = string_metade + caracter_meio + string_metade[::-1]

    else:

        strings_obrigatorias = []
        if '+[' in modo:
            strings_obrigatorias = eval(modo[modo.find('['):modo.find(']') + 1])

        if 'm' in modo:
            caracteres = random.choices(minusculas, k=n)

        elif 'M' in modo:
            caracteres = random.choices(maiusculas, k=n)

        else:
            caracteres = random.choices(maiusculas_e_minusculas, k=n)

        posicoes = [i for i in range(0, n + len(strings_obrigatorias))]
        string_list = [i for i in range(0, n + len(strings_obrigatorias))]

        for i in range(0, len(strings_obrigatorias)):

            substituir = random.choice(posicoes)
            string_obrigatoria = random.choice(strings_obrigatorias)
            string_list[substituir] = string_obrigatoria

            strings_obrigatorias.remove(string_obrigatoria)
            posicoes.remove(substituir)

        for i in range(0, (n)):

            substituir = random.choice(posicoes)
            caracter = random.choice(caracteres)
            string_list[substituir] = caracter

            caracteres.remove(caracter)
            posicoes.remove(substituir)

        string = ''
        for p in string_list:
            string += f'{p}'

    return string
