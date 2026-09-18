DATA_FILE = "alunos.txt"

def carregar_alunos(caminho):
    with open(caminho, "r") as f:
        n = int(f.readline().strip())
        alunos = []
        for _ in range(n):
            nome, numero = f.readline().split()
            alunos.append((nome, int(numero)))
    return alunos

def busca_binaria(alunos, alvo):
    inicio, fim = 0, len(alunos) - 1

    if inicio > fim:
        return -1, None

    if alvo < alunos[inicio][1] or alvo > alunos[fim][1]:
        return -1, None

    while inicio <= fim:
        meio = inicio + (fim - inicio) // 2
        nome, numero = alunos[meio]

        if numero == alvo:
            return meio, (nome, numero)
        elif numero < alvo:
            inicio = meio + 1
        else:
            fim = meio - 1

    return -1, None

def ler_numero():
    while True:
        entrada = input("Digite o numero do aluno a buscar: ").strip()
        if entrada.isdigit():
            return int(entrada)
        print(f"'{entrada}' nao e um numero valido. Digite apenas o numero (ex: 999873).")

def main():
    alunos = carregar_alunos(DATA_FILE)
    alvo = ler_numero()

    indice, resultado = busca_binaria(alunos, alvo)
    if resultado is None:
        print("Aluno nao encontrado.")
    else:
        nome, numero = resultado
        print(f"Aluno encontrado: {nome} (numero {numero}, indice {indice})")

if __name__ == "__main__":
    main()
