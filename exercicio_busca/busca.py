import subprocess
import os
import time

ASM_FILE = "/home/beuren/Documentos/pesquisa_ordenacao/exercicio_busca/busca_binaria.asm"
OBJ_FILE = "busca_binaria.o"
EXE_FILE = "busca_binaria"
DATA_FILE = "/home/beuren/Documentos/pesquisa_ordenacao/exercicio_busca/alunos.txt"

def compilar_assembly():
    precisa_compilar = (
        not os.path.exists(EXE_FILE)
        or os.path.getmtime(ASM_FILE) > os.path.getmtime(EXE_FILE)
    )

    if not precisa_compilar:
        return

    print("Compilando assembly...")

    resultado = subprocess.run(
        ["nasm", "-f", "elf64", ASM_FILE, "-o", OBJ_FILE],
        capture_output=True, text=True,
    )
    if resultado.returncode != 0:
        raise RuntimeError(f"Erro no nasm:\n{resultado.stderr}")

    resultado = subprocess.run(
        ["gcc", OBJ_FILE, "-o", EXE_FILE, "-no-pie"],
        capture_output=True, text=True,
    )
    if resultado.returncode != 0:
        raise RuntimeError(f"Erro no gcc:\n{resultado.stderr}")

    print("Compilado com sucesso.")

def buscar_no_assembly(numero):
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"{DATA_FILE} nao encontrado no diretorio atual.")

    resultado = subprocess.run(
        [f"./{EXE_FILE}"],
        input=f"{numero}\n",
        capture_output=True,
        text=True,
    )

    if resultado.returncode != 0:
        detalhe = (
            f"codigo de saida: {resultado.returncode}\n"
            f"stdout: {resultado.stdout!r}\n"
            f"stderr: {resultado.stderr!r}"
        )
        if resultado.returncode < 0:
            detalhe += f"\n(codigo negativo = processo morto por sinal, provavel crash/segfault)"
        raise RuntimeError(f"Programa terminou com erro:\n{detalhe}")

    return resultado.stdout

def ler_numero():
    while True:
        entrada = input("Digite o numero do aluno a buscar: ").strip()
        if entrada.isdigit():
            return int(entrada)
        print(f"'{entrada}' nao e um numero valido. Digite apenas o numero (ex: 999873).")

def main():
    compilar_assembly()

    numero = ler_numero()

    inicio = time.perf_counter()
    saida = buscar_no_assembly(numero)
    fim = time.perf_counter()

    print(saida.strip())
    print(f"Tempo de busca: {(fim - inicio) * 1000:.3f} ms")

if __name__ == "__main__":
    main()
