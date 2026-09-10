"""API do backend de ordenacao. Sem I/O interativo — so funcoes prontas para
serem chamadas por uma interface (CLI, web, o que for).

As ordenacoes rodam em NASM (asm/bubble_sort.asm e asm/insertion_sort.asm),
compiladas em libsort.so e carregadas aqui via ctypes.
"""

import ctypes
import os
import threading
import time
from datetime import datetime

import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_ARQUIVOS = os.path.join(BASE_DIR, "datasets")
PASTA_RESULTADOS = os.path.join(BASE_DIR, "resultados")
LIBSORT_PATH = os.path.join(BASE_DIR, "libsort.so")
TEMPOS_MD = os.path.join(PASTA_RESULTADOS, "tempos.md")
TEMPOS_MD_ATIVIDADE2 = os.path.join(PASTA_RESULTADOS, "resultados_atividade2.md")

_tempos_lock = threading.Lock()

# Atividade 1: Bubble/Insertion/Shell/Selection, 700k-1M -> tempos.md
# Atividade 2: Quick/Merge/Radix/Heap, 1M-2M -> resultados_atividade2.md
ALGORITMOS_ATIVIDADE2 = {"quick", "merge", "radix", "heap"}

TAMANHOS_DISPONIVEIS = [
    700_000, 750_000, 800_000, 850_000, 900_000, 1_000_000,
    1_150_000, 1_300_000, 1_350_000, 1_500_000, 2_000_000,
]
TIPOS_DISPONIVEIS = ["ordenado", "invertido", "randomico"]
VALOR_MIN, VALOR_MAX = 0, 1_000_000_000  # cabe em int32

_lib = ctypes.CDLL(LIBSORT_PATH)
_lib.bubble_sort.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.c_int64]
_lib.bubble_sort.restype = None
_lib.insertion_sort.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.c_int64]
_lib.insertion_sort.restype = None
_lib.shell_sort.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.c_int64]
_lib.shell_sort.restype = None
_lib.selection_sort.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.c_int64]
_lib.selection_sort.restype = None
_lib.quick_sort.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.c_int64]
_lib.quick_sort.restype = None
_lib.merge_sort.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.c_int64]
_lib.merge_sort.restype = None
_lib.radix_sort.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.c_int64]
_lib.radix_sort.restype = None
_lib.heap_sort.argtypes = [ctypes.POINTER(ctypes.c_int32), ctypes.c_int64]
_lib.heap_sort.restype = None


def listar_arquivos():
    """Nomes (.txt) disponiveis em datasets/, ordenados alfabeticamente."""
    if not os.path.isdir(PASTA_ARQUIVOS):
        return []
    return sorted(f for f in os.listdir(PASTA_ARQUIVOS) if f.endswith(".txt"))


def gerar_arquivo(tamanho, tipo):
    """Gera um arquivo de numeros em datasets/ e retorna o nome do arquivo.

    tamanho: um dos valores em TAMANHOS_DISPONIVEIS
    tipo: "ordenado" | "invertido" | "randomico"
    """
    if tamanho not in TAMANHOS_DISPONIVEIS:
        raise ValueError(f"tamanho invalido: {tamanho}")
    if tipo not in TIPOS_DISPONIVEIS:
        raise ValueError(f"tipo invalido: {tipo}")

    if tipo == "ordenado":
        numeros = np.arange(tamanho, dtype=np.int64)
    elif tipo == "invertido":
        numeros = np.arange(tamanho, 0, -1, dtype=np.int64)
    else:
        numeros = np.random.randint(VALOR_MIN, VALOR_MAX + 1, size=tamanho, dtype=np.int64)

    os.makedirs(PASTA_ARQUIVOS, exist_ok=True)
    nome = f"{tipo}_{tamanho}.txt"
    caminho = os.path.join(PASTA_ARQUIVOS, nome)
    np.savetxt(caminho, numeros, fmt="%d")
    return nome


def ler_arquivo(nome_arquivo):
    """Le um arquivo de datasets/ pelo nome e retorna a lista de inteiros."""
    caminho = os.path.join(PASTA_ARQUIVOS, nome_arquivo)
    with open(caminho) as f:
        return [int(linha) for linha in f if linha.strip()]


def salvar_resultado(numeros, nome_arquivo_original, algoritmo):
    """Salva a saida ordenada em resultados/ e retorna o nome do arquivo."""
    os.makedirs(PASTA_RESULTADOS, exist_ok=True)
    base = os.path.splitext(nome_arquivo_original)[0]
    nome = f"{base}_{algoritmo}_ordenado.txt"
    caminho = os.path.join(PASTA_RESULTADOS, nome)
    with open(caminho, "w") as f:
        f.write("\n".join(str(n) for n in numeros))
        f.write("\n")
    return nome


def registrar_tempo(algoritmo, tipo, tamanho, tempo_segundos):
    """Acrescenta uma linha na tabela markdown com o tempo de execucao de uma
    ordenacao (um historico entre execucoes). Algoritmos da atividade 1
    (Bubble/Insertion/Shell/Selection) vao pra resultados/tempos.md;
    algoritmos da atividade 2 (Quick/Merge/Radix/Heap) vao pra
    resultados/resultados_atividade2.md — arquivos separados."""
    os.makedirs(PASTA_RESULTADOS, exist_ok=True)
    destino = TEMPOS_MD_ATIVIDADE2 if algoritmo in ALGORITMOS_ATIVIDADE2 else TEMPOS_MD
    titulo = (
        "# Resultados de execucao (atividade 2)\n\n"
        if algoritmo in ALGORITMOS_ATIVIDADE2
        else "# Tempos de execucao\n\n"
    )
    quando = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = (
        f"| {algoritmo} | {tipo} | {tamanho:,} | {tempo_segundos:.6f} | "
        f"{tempo_segundos / 60:.4f} | {quando} |\n".replace(",", ".")
    )
    with _tempos_lock:
        novo = not os.path.isfile(destino)
        with open(destino, "a") as f:
            if novo:
                f.write(titulo)
                f.write("| Algoritmo | Tipo | Tamanho | Tempo (s) | Tempo (min) | Quando |\n")
                f.write("|---|---|---|---|---|---|\n")
            f.write(linha)


def _ordenar(numeros, func_asm):
    n = len(numeros)
    arr = (ctypes.c_int32 * n)(*numeros)
    t0 = time.perf_counter()
    func_asm(arr, n)
    t1 = time.perf_counter()
    return list(arr), t1 - t0


def bubble_sort(numeros):
    """Ordena (crescente) via NASM. Retorna (lista_ordenada, tempo_segundos)."""
    return _ordenar(numeros, _lib.bubble_sort)


def insertion_sort(numeros):
    """Ordena (crescente) via NASM. Retorna (lista_ordenada, tempo_segundos)."""
    return _ordenar(numeros, _lib.insertion_sort)


def shell_sort(numeros):
    """Ordena (crescente) via NASM. Retorna (lista_ordenada, tempo_segundos)."""
    return _ordenar(numeros, _lib.shell_sort)


def selection_sort(numeros):
    """Ordena (crescente) via NASM. Retorna (lista_ordenada, tempo_segundos)."""
    return _ordenar(numeros, _lib.selection_sort)


def quick_sort(numeros):
    """Ordena (crescente) via NASM. Retorna (lista_ordenada, tempo_segundos)."""
    return _ordenar(numeros, _lib.quick_sort)


def merge_sort(numeros):
    """Ordena (crescente) via NASM. Retorna (lista_ordenada, tempo_segundos)."""
    return _ordenar(numeros, _lib.merge_sort)


def radix_sort(numeros):
    """Ordena (crescente) via NASM. Retorna (lista_ordenada, tempo_segundos)."""
    return _ordenar(numeros, _lib.radix_sort)


def heap_sort(numeros):
    """Ordena (crescente) via NASM. Retorna (lista_ordenada, tempo_segundos)."""
    return _ordenar(numeros, _lib.heap_sort)


def iniciar_ordenacao(numeros, algoritmo):
    """Inicia bubble_sort/insertion_sort em background numa thread separada,
    sem esperar terminar. Retorna (thread, buffer, resultado):

    - buffer: o array ctypes que a rotina NASM muta in-place durante a
      ordenacao — pode ser lido de outra thread pra observar o progresso
      real em tempo real (a chamada ctypes libera o GIL enquanto roda).
    - resultado: dict vazio que ganha a chave "tempo" quando a thread termina.

    Nao muda em nada a logica de ordenacao (mesmo _lib.bubble_sort/
    insertion_sort de sempre) — so orquestra a chamada numa thread pra
    permitir observar o array enquanto ele ainda esta sendo ordenado.
    """
    func_asm = {
        "bubble": _lib.bubble_sort,
        "insertion": _lib.insertion_sort,
        "shell": _lib.shell_sort,
        "selection": _lib.selection_sort,
        "quick": _lib.quick_sort,
        "merge": _lib.merge_sort,
        "radix": _lib.radix_sort,
        "heap": _lib.heap_sort,
    }[algoritmo]
    n = len(numeros)
    buffer = (ctypes.c_int32 * n)(*numeros)
    resultado = {}

    def _alvo():
        t0 = time.perf_counter()
        func_asm(buffer, n)
        resultado["tempo"] = time.perf_counter() - t0

    thread = threading.Thread(target=_alvo, daemon=True)
    thread.start()
    return thread, buffer, resultado


def progresso_ordenacao(buffer, algoritmo):
    """Estima a % concluida de uma ordenacao em andamento observando o
    buffer que a rotina NASM esta mutando ao vivo — sem tocar no Assembly
    e sem estimar por tempo.

    Bubble sort empurra o maior elemento restante pro final a cada
    passagem completa, entao os ultimos elementos vao virando definitivos
    de tras pra frente: medimos o tamanho do sufixo ja ordenado.

    Insertion sort mantem o prefixo [0:i] sempre ordenado entre si, entao
    medimos o tamanho do prefixo ja ordenado.

    E uma estimativa (pode superestimar um pouco num instante de corrida
    com o array ainda mudando), mas reflete o estado real do array, nao
    uma projecao de tempo.
    """
    n = len(buffer)
    if n <= 1:
        return 100.0
    arr = np.ctypeslib.as_array(buffer)
    quebras = np.where(arr[:-1] > arr[1:])[0]
    if quebras.size == 0:
        return 100.0
    if algoritmo == "bubble":
        pronto = n - 1 - int(quebras[-1])
    else:
        pronto = int(quebras[0]) + 1
    return max(0.0, min(99.0, pronto / n * 100))
