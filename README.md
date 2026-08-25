# Backend de ordenacao (Assembly)

Bubble Sort e Insertion Sort implementados em NASM, expostos como uma
biblioteca Python (`core.py`) pronta para ser usada por qualquer interface
(web, CLI, etc). Quem for montar a UI so precisa importar `core.py` — nao
precisa mexer em Assembly nem em ctypes.

## Estrutura

```
asm/bubble_sort.asm      -> rotina NASM do bubble sort
asm/insertion_sort.asm   -> rotina NASM do insertion sort
Makefile                 -> compila os .asm e gera libsort.so
core.py                  -> API Python (importar isso na UI)
gerador.py               -> CLI de terminal para gerar arquivos (usa core.py)
menu.py                  -> CLI de terminal do menu (usa core.py)
server.py                -> servidor web (HTTP puro, sem dependencias) que expoe core.py
web/                      -> frontend (index.html, style.css, app.js) servido por server.py
datasets/                -> onde os .txt gerados/lidos ficam (dados da questao 1)
resultados/               -> saida ordenada de cada job, gerada por server.py
```

## Interface web

```bash
make               # se ainda nao gerou libsort.so
python3 server.py  # sobe em http://localhost:8000 (porta configuravel via PORT)
```

Abra `http://localhost:8000` no navegador. A pagina tem uma aba para cada
algoritmo (Bubble Sort / Insertion Sort), cada uma com:

- um exemplo visual animado (5 numeros, em loop continuo) ilustrando como o
  algoritmo funciona — e so uma simulacao em JS, nao usa o backend;
- geracao de dataset (chama `core.gerar_arquivo`) e selecao de um arquivo
  ja existente em `datasets/`;
- botao para ordenar o dataset escolhido rodando a rotina NASM de verdade
  (via `core.bubble_sort`/`core.insertion_sort`), com um cronometro ao vivo
  e o tempo final medido pelo backend.

Ordenacoes rodam em thread separada no servidor (job em background com
polling) para nao travar o servidor durante os minutos que um dataset
grande pode levar em um algoritmo O(n^2).

Ao terminar, o resultado ordenado e salvo em `resultados/<nome>_<algoritmo>_ordenado.txt`
(via `core.salvar_resultado`) e fica disponivel pra download direto na pagina
(rota `GET /api/resultado?arquivo=<nome>`).

Cada execucao tambem e registrada em `resultados/tempos.md` (via
`core.registrar_tempo`) — uma tabela com algoritmo, tipo de dataset, tamanho,
tempo em segundos/minutos e a data/hora, acumulando um historico entre
execucoes diferentes do servidor.

## Build

Requisitos: `nasm` e `gcc` (so para compilar; depois de gerado o
`libsort.so`, so precisa de Python 3 + as dependencias de `requirements.txt`
para rodar).

```bash
pip install -r requirements.txt
```

```bash
make            # gera libsort.so a partir dos .asm
make clean      # remove os artefatos de build
```

## API (`core.py`)

```python
import core

core.TAMANHOS_DISPONIVEIS   # [700_000, 750_000, 800_000, 850_000, 900_000, 1_000_000]
core.TIPOS_DISPONIVEIS      # ["ordenado", "invertido", "randomico"]

# Parte 1 — gerar arquivo de numeros
nome = core.gerar_arquivo(700_000, "randomico")   # -> "randomico_700000.txt"

# Listar arquivos ja gerados em datasets/
core.listar_arquivos()      # -> ["randomico_700000.txt", ...]

# Ler um arquivo pelo nome (retorna list[int])
numeros = core.ler_arquivo("randomico_700000.txt")

# Ordenar — cada funcao roda a rotina NASM e mede o tempo
resultado, tempo_segundos = core.bubble_sort(numeros)
resultado, tempo_segundos = core.insertion_sort(numeros)
```

Todas as funcoes sao puras/sincronas: recebem dados, devolvem dados. Nao ha
`input()`/`print()` em `core.py` — isso fica por conta da interface.

## Importante para quem for montar a UI web

- **Bubble Sort e Insertion Sort sao O(n^2).** Com os tamanhos pedidos
  (700k–1M), uma ordenacao pode levar minutos a dezenas de minutos. Isso e
  esperado (faz parte do exercicio comparar o custo desses algoritmos) —
  **nao rode isso direto na thread de uma requisicao HTTP**. Rode em
  background (fila de job, thread separada, websocket com progresso, etc.)
  e devolva o tempo/resultado quando terminar.
- `core.bubble_sort` / `core.insertion_sort` bloqueiam a thread Python que os
  chama enquanto rodam (o `.so` e codigo nativo, sem liberar o GIL — ctypes
  so libera o GIL automaticamente para chamadas que ele reconhece como
  seguras; nao contar com isso aqui). Se for expor via Flask/FastAPI, chame
  a partir de um worker/processo separado.
- Os numeros sao inteiros de 32 bits (`ctypes.c_int32`). O gerador so produz
  valores entre 0 e 1.000.000.000, entao nao ha risco de overflow.
- `core.ler_arquivo` espera um `.txt` com um inteiro por linha (formato que
  `core.gerar_arquivo` produz). Se a UI aceitar upload de arquivo, so
  garantir que caia nesse formato dentro de `datasets/`.

## Testando sem UI (CLI de referencia)

```bash
python3 gerador.py   # gera um arquivo de teste
python3 menu.py       # le, ordena, mostra tempo
```

Esses dois scripts sao so uma casca fina sobre `core.py` — servem de
referencia/teste, nao sao a interface final.
# pesquisa_ordenacao
