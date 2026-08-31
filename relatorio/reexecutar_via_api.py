"""Roda as 4 ordenacoes (bubble/insertion/selection/shell) para os 6 tamanhos
e 3 tipos de dataset, chamando a mesma API HTTP que a interface web chama
(POST /api/ordenar + polling /api/status) — sem GPU, so CPU via a rotina NASM
de cada algoritmo, como se um usuario clicasse "Ordenar" na pagina pra cada
combinacao. Escreve tudo num markdown novo em resultados/.
"""

import json
import time
import urllib.request
from datetime import datetime

BASE_URL = "http://localhost:8000"
ALGOS = ["bubble", "insertion", "selection", "shell"]
TIPOS = ["ordenado", "invertido", "randomico"]
TAMANHOS = [700_000, 750_000, 800_000, 850_000, 900_000, 1_000_000]

OUT_MD = "/home/beuren/Documentos/pesquisa_ordenacao/resultados/resultados_execucao_api.md"


def post(path, payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BASE_URL + path, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode("utf-8"))


def get(path):
    with urllib.request.urlopen(BASE_URL + path) as r:
        return json.loads(r.read().decode("utf-8"))


def ordenar(algoritmo, arquivo):
    resp = post("/api/ordenar", {"algoritmo": algoritmo, "arquivo": arquivo})
    job_id = resp["job_id"]
    while True:
        status = get(f"/api/status?job_id={job_id}")
        if status["status"] == "done":
            return status["tempo"]
        if status["status"] == "error":
            raise RuntimeError(status.get("erro"))
        time.sleep(2)


def _ja_feitos():
    """Le o md existente (se houver) e devolve o set de (algo,tipo,tamanho) ja gravados."""
    feitos = set()
    try:
        with open(OUT_MD) as f:
            for linha in f:
                if not linha.startswith("| ") or linha.startswith("| Algoritmo"):
                    continue
                campos = [c.strip() for c in linha.strip().strip("|").split("|")]
                if len(campos) != 6:
                    continue
                algo, tipo, tam, *_ = campos
                feitos.add((algo, tipo, int(tam.replace(".", ""))))
    except FileNotFoundError:
        pass
    return feitos


def main():
    feitos = _ja_feitos()
    if feitos:
        with open(OUT_MD) as f:
            linhas = f.read().rstrip("\n").split("\n")
        print(f"retomando: {len(feitos)} combinacoes ja gravadas em {OUT_MD}", flush=True)
    else:
        linhas = []
        linhas.append("# Resultados de execucao via API (reexecucao)\n")
        linhas.append(f"\nGerado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, "
                       "chamando /api/ordenar da mesma forma que a interface web "
                       "chamaria (sem GPU, CPU via rotina NASM de cada algoritmo).\n")
        linhas.append("\n| Algoritmo | Tipo | Tamanho | Tempo (s) | Tempo (min) | Quando |")
        linhas.append("|---|---|---|---|---|---|")

    total = len(ALGOS) * len(TIPOS) * len(TAMANHOS)
    i = len(feitos)
    for algo in ALGOS:
        for tipo in TIPOS:
            for tamanho in TAMANHOS:
                if (algo, tipo, tamanho) in feitos:
                    continue
                i += 1
                arquivo = f"{tipo}_{tamanho}.txt"
                t0 = time.time()
                tempo = ordenar(algo, arquivo)
                quando = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                linha = (f"| {algo} | {tipo} | {tamanho:,} | {tempo:.6f} | "
                         f"{tempo / 60:.4f} | {quando} |").replace(",", ".")
                linhas.append(linha)
                print(f"[{i}/{total}] {algo} {tipo} {tamanho} -> {tempo:.3f}s "
                      f"(levou {time.time() - t0:.1f}s de parede)", flush=True)
                with open(OUT_MD, "w") as f:
                    f.write("\n".join(linhas) + "\n")

    print("Concluido:", OUT_MD)


if __name__ == "__main__":
    main()
