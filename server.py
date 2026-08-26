#!/usr/bin/env python3
"""Servidor web da interface (parte 3). So expoe core.py via HTTP.

Nao usa nenhuma dependencia externa (sem Flask/etc disponivel no ambiente) —
so a biblioteca padrao do Python (http.server + threading), para servir a
pagina estatica em web/ e uma API JSON simples que chama core.py.

Ordenacoes rodam em threads separadas (background jobs) porque bubble/
insertion sort sao O(n^2) e podem demorar muito com datasets grandes — o
cliente cria o job e faz polling do status.
"""

import json
import os
import re
import threading
import urllib.parse
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import core

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
}

NOME_RE = re.compile(r"^(ordenado|invertido|randomico)_(\d+)\.txt$")
LINHA_TEMPOS_RE = re.compile(
    r"^\|\s*(\w+)\s*\|\s*(\w+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*(.+?)\s*\|$"
)


def _ler_tempos():
    """Le resultados/tempos.md e devolve os registros como lista de dicts."""
    registros = []
    if not os.path.isfile(core.TEMPOS_MD):
        return registros
    with open(core.TEMPOS_MD) as f:
        for linha in f:
            m = LINHA_TEMPOS_RE.match(linha.strip())
            if not m:
                continue
            algoritmo, tipo, tamanho, tempo_s, tempo_min, quando = m.groups()
            if algoritmo == "Algoritmo":
                continue  # linha de cabecalho
            registros.append(
                {
                    "algoritmo": algoritmo,
                    "tipo": tipo,
                    "tamanho": int(tamanho.replace(".", "")),
                    "tempo_s": float(tempo_s),
                    "tempo_min": float(tempo_min),
                    "quando": quando,
                }
            )
    return registros

jobs = {}
jobs_lock = threading.Lock()


def _run_job(job_id, numeros, algoritmo, arquivo_original):
    try:
        # A ordenacao roda numa thread propria (dentro de iniciar_ordenacao) —
        # o buffer ctypes que ela muta ao vivo fica guardado no job pra quem
        # chamar /api/status poder observar o progresso real enquanto roda.
        thread, buffer, resultado = core.iniciar_ordenacao(numeros, algoritmo)
        with jobs_lock:
            jobs[job_id]["_buffer"] = buffer
        thread.join()

        resultado_lista = list(buffer)
        arquivo_saida = core.salvar_resultado(resultado_lista, arquivo_original, algoritmo)

        m = NOME_RE.match(arquivo_original)
        tipo = m.group(1) if m else "desconhecido"
        core.registrar_tempo(algoritmo, tipo, len(numeros), resultado["tempo"])

        with jobs_lock:
            jobs[job_id].pop("_buffer", None)
            jobs[job_id].update(
                status="done",
                tempo=resultado["tempo"],
                percent=100,
                arquivo_saida=arquivo_saida,
            )
    except Exception as exc:  # devolve erro pro cliente em vez de matar a thread
        with jobs_lock:
            jobs[job_id].pop("_buffer", None)
            jobs[job_id].update(status="error", erro=str(exc))


class Handler(BaseHTTPRequestHandler):
    server_version = "OrdenacaoWeb/1.0"

    def log_message(self, fmt, *args):
        pass  # silencia o log padrao no stderr

    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error_json(self, msg, status=400):
        self._send_json({"erro": msg}, status)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def _serve_static(self, path):
        if path == "/":
            path = "/index.html"
        caminho = os.path.normpath(os.path.join(WEB_DIR, path.lstrip("/")))
        if not caminho.startswith(WEB_DIR) or not os.path.isfile(caminho):
            self._send_error_json("nao encontrado", 404)
            return
        ext = os.path.splitext(caminho)[1]
        content_type = CONTENT_TYPES.get(ext, "application/octet-stream")
        with open(caminho, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/config":
            self._send_json(
                {
                    "tamanhos": core.TAMANHOS_DISPONIVEIS,
                    "tipos": core.TIPOS_DISPONIVEIS,
                }
            )
            return

        if self.path == "/api/arquivos":
            arquivos = []
            for nome in core.listar_arquivos():
                m = NOME_RE.match(nome)
                if m:
                    arquivos.append(
                        {"nome": nome, "tipo": m.group(1), "tamanho": int(m.group(2))}
                    )
                else:
                    arquivos.append({"nome": nome, "tipo": None, "tamanho": None})
            self._send_json({"arquivos": arquivos})
            return

        if self.path == "/api/tempos":
            self._send_json({"registros": _ler_tempos()})
            return

        if self.path.startswith("/api/status"):
            qs = self.path.split("?", 1)[1] if "?" in self.path else ""
            params = dict(p.split("=", 1) for p in qs.split("&") if "=" in p)
            job_id = params.get("job_id")
            with jobs_lock:
                job = jobs.get(job_id)
                buffer = job.get("_buffer") if job is not None else None
                resposta = (
                    {k: v for k, v in job.items() if k != "_buffer"}
                    if job is not None
                    else None
                )
            if resposta is None:
                self._send_error_json("job nao encontrado", 404)
                return

            if resposta.get("status") == "running":
                percent = core.progresso_ordenacao(buffer, resposta["algoritmo"]) if buffer else 0.0
                resposta["percent"] = round(percent, 1)

            self._send_json(resposta)
            return

        if self.path.startswith("/api/resultado"):
            qs = self.path.split("?", 1)[1] if "?" in self.path else ""
            params = dict(p.split("=", 1) for p in qs.split("&") if "=" in p)
            nome = urllib.parse.unquote(params.get("arquivo", ""))
            pasta = os.path.normpath(core.PASTA_RESULTADOS)
            caminho = os.path.normpath(os.path.join(pasta, nome))
            if not caminho.startswith(pasta) or not os.path.isfile(caminho):
                self._send_error_json("resultado nao encontrado", 404)
                return
            with open(caminho, "rb") as f:
                body = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Disposition", f'attachment; filename="{nome}"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self._serve_static(self.path)

    def do_POST(self):
        try:
            body = self._read_json_body()
        except json.JSONDecodeError:
            self._send_error_json("JSON invalido")
            return

        if self.path == "/api/gerar":
            try:
                tamanho = int(body.get("tamanho"))
                tipo = body.get("tipo")
                nome = core.gerar_arquivo(tamanho, tipo)
            except (ValueError, TypeError) as exc:
                self._send_error_json(str(exc))
                return
            self._send_json({"nome": nome})
            return

        if self.path == "/api/ordenar":
            arquivo = body.get("arquivo")
            algoritmo = body.get("algoritmo")
            if algoritmo not in ("bubble", "insertion", "shell", "selection", "quick", "merge"):
                self._send_error_json("algoritmo invalido")
                return
            try:
                numeros = core.ler_arquivo(arquivo)
            except OSError:
                self._send_error_json("arquivo nao encontrado", 404)
                return

            job_id = uuid.uuid4().hex
            with jobs_lock:
                jobs[job_id] = {
                    "status": "running",
                    "n": len(numeros),
                    "algoritmo": algoritmo,
                    "arquivo": arquivo,
                }
            thread = threading.Thread(
                target=_run_job, args=(job_id, numeros, algoritmo, arquivo), daemon=True
            )
            thread.start()
            self._send_json({"job_id": job_id, "n": len(numeros)})
            return

        self._send_error_json("rota nao encontrada", 404)


def main():
    porta = int(os.environ.get("PORT", 8000))
    servidor = ThreadingHTTPServer(("0.0.0.0", porta), Handler)
    print(f"Servindo em http://localhost:{porta}")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
