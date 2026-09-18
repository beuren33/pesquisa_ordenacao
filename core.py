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

ALGORITMOS_ATIVIDADE2 = {"quick", "merge", "radix", "heap"}

TAMANHOS_DISPONIVEIS = [
    700_000, 750_000, 800_000, 850_000, 900_000, 1_000_000,
    1_150_000, 1_300_000, 1_350_000, 1_500_000, 2_000_000,
]
TIPOS_DISPONIVEIS = ["ordenado", "invertido", "randomico"]
VALOR_MIN, VALOR_MAX = 0, 1_000_000_000

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
    if not os.path.isdir(PASTA_ARQUIVOS):
        return []
    return sorted(f for f in os.listdir(PASTA_ARQUIVOS) if f.endswith(".txt"))

def gerar_arquivo(tamanho, tipo):
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
    caminho = os.path.join(PASTA_ARQUIVOS, nome_arquivo)
    with open(caminho) as f:
        return [int(linha) for linha in f if linha.strip()]

def salvar_resultado(numeros, nome_arquivo_original, algoritmo):
    os.makedirs(PASTA_RESULTADOS, exist_ok=True)
    base = os.path.splitext(nome_arquivo_original)[0]
    nome = f"{base}_{algoritmo}_ordenado.txt"
    caminho = os.path.join(PASTA_RESULTADOS, nome)
    with open(caminho, "w") as f:
        f.write("\n".join(str(n) for n in numeros))
        f.write("\n")
    return nome

def registrar_tempo(algoritmo, tipo, tamanho, tempo_segundos):
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
    return _ordenar(numeros, _lib.bubble_sort)

def insertion_sort(numeros):
    return _ordenar(numeros, _lib.insertion_sort)

def shell_sort(numeros):
    return _ordenar(numeros, _lib.shell_sort)

def selection_sort(numeros):
    return _ordenar(numeros, _lib.selection_sort)

def quick_sort(numeros):
    return _ordenar(numeros, _lib.quick_sort)

def merge_sort(numeros):
    return _ordenar(numeros, _lib.merge_sort)

def radix_sort(numeros):
    return _ordenar(numeros, _lib.radix_sort)

def heap_sort(numeros):
    return _ordenar(numeros, _lib.heap_sort)

def iniciar_ordenacao(numeros, algoritmo):
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
