import core

def escolher_tamanho():
    print("\nTamanhos disponiveis:")
    for i, t in enumerate(core.TAMANHOS_DISPONIVEIS, start=1):
        print(f"  {i}) {t:,}".replace(",", "."))
    while True:
        escolha = input("Escolha o tamanho: ").strip()
        if escolha.isdigit() and 1 <= int(escolha) <= len(core.TAMANHOS_DISPONIVEIS):
            return core.TAMANHOS_DISPONIVEIS[int(escolha) - 1]
        print("Opcao invalida.")

def escolher_tipo():
    print("\nTipos disponiveis:")
    for i, t in enumerate(core.TIPOS_DISPONIVEIS, start=1):
        print(f"  {i}) {t.capitalize()}")
    while True:
        escolha = input("Escolha o tipo: ").strip()
        if escolha.isdigit() and 1 <= int(escolha) <= len(core.TIPOS_DISPONIVEIS):
            return core.TIPOS_DISPONIVEIS[int(escolha) - 1]
        print("Opcao invalida.")

def main():
    print("=== Gerador de arquivos de numeros ===")
    tamanho = escolher_tamanho()
    tipo = escolher_tipo()
    print(f"\nGerando {tamanho:,} numeros ({tipo})...".replace(",", "."))
    nome = core.gerar_arquivo(tamanho, tipo)
    print(f"Arquivo salvo em: datasets/{nome}")

if __name__ == "__main__":
    main()
