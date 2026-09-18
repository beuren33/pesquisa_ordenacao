import core

estado = {"nome": None, "numeros": None}

def ler_arquivo():
    arquivos = core.listar_arquivos()
    if not arquivos:
        print("\nNenhum arquivo encontrado em 'datasets/'. Rode gerador.py primeiro.")
        return

    print("\nArquivos disponiveis:")
    for i, nome in enumerate(arquivos, start=1):
        print(f"  {i}) {nome}")

    escolha = input("Escolha o arquivo: ").strip()
    if not escolha.isdigit() or not (1 <= int(escolha) <= len(arquivos)):
        print("Opcao invalida.")
        return

    nome = arquivos[int(escolha) - 1]
    print(f"Lendo {nome}...")
    t0 = core.time.perf_counter()
    numeros = core.ler_arquivo(nome)
    t1 = core.time.perf_counter()

    estado["nome"] = nome
    estado["numeros"] = numeros
    print(f"{len(numeros):,} numeros lidos em {t1 - t0:.3f}s".replace(",", "."))

def _executar_ordenacao(func, nome_algoritmo):
    if estado["numeros"] is None:
        print("\nNenhum arquivo carregado. Use a opcao 1 primeiro.")
        return

    n = len(estado["numeros"])
    quadratico = nome_algoritmo in ("Bubble Sort", "Insertion Sort", "Selection Sort")
    if quadratico and n >= 700_000:
        confirmar = input(
            f"\nAviso: {nome_algoritmo} e O(n^2). Com {n:,} numeros isso pode "
            "demorar muito (minutos a horas). Continuar? (s/N): ".replace(",", ".")
        ).strip().lower()
        if confirmar != "s":
            print("Cancelado.")
            return

    print(f"Ordenando com {nome_algoritmo}...")
    resultado, tempo = func(estado["numeros"])
    estado["numeros"] = resultado
    print(f"Concluido em {tempo:.3f}s")
    print(f"Primeiros 10: {resultado[:10]}")
    print(f"Ultimos 10:   {resultado[-10:]}")

def executar_bubble_sort():
    _executar_ordenacao(core.bubble_sort, "Bubble Sort")

def executar_insertion_sort():
    _executar_ordenacao(core.insertion_sort, "Insertion Sort")

def executar_shell_sort():
    _executar_ordenacao(core.shell_sort, "Shell Sort")

def executar_selection_sort():
    _executar_ordenacao(core.selection_sort, "Selection Sort")

def executar_quick_sort():
    _executar_ordenacao(core.quick_sort, "Quick Sort")

def executar_merge_sort():
    _executar_ordenacao(core.merge_sort, "Merge Sort")

def executar_radix_sort():
    _executar_ordenacao(core.radix_sort, "Radix Sort")

def executar_heap_sort():
    _executar_ordenacao(core.heap_sort, "Heap Sort")

def menu():
    while True:
        print("\n=== Menu Principal ===")
        arquivo_atual = estado["nome"] or "(nenhum)"
        print(f"Arquivo carregado: {arquivo_atual}")
        print("1) Ler arquivo")
        print("2) Ordenar com Bubble Sort")
        print("3) Ordenar com Insertion Sort")
        print("4) Ordenar com Shell Sort")
        print("5) Ordenar com Selection Sort")
        print("6) Ordenar com Quick Sort")
        print("7) Ordenar com Merge Sort")
        print("8) Ordenar com Radix Sort")
        print("9) Ordenar com Heap Sort")
        print("10) Sair")

        opcao = input("Escolha uma opcao: ").strip()
        if opcao == "1":
            ler_arquivo()
        elif opcao == "2":
            executar_bubble_sort()
        elif opcao == "3":
            executar_insertion_sort()
        elif opcao == "4":
            executar_shell_sort()
        elif opcao == "5":
            executar_selection_sort()
        elif opcao == "6":
            executar_quick_sort()
        elif opcao == "7":
            executar_merge_sort()
        elif opcao == "8":
            executar_radix_sort()
        elif opcao == "9":
            executar_heap_sort()
        elif opcao == "10":
            print("Ate mais.")
            break
        else:
            print("Opcao invalida.")

if __name__ == "__main__":
    menu()
