// Interface web (parte 3). So consome a API HTTP servida por server.py,
// que por sua vez chama core.py. Nenhuma logica de ordenacao mora aqui —
// a animacao de exemplo e so uma simulacao visual em JS pra ilustrar o
// algoritmo, os numeros de verdade sao sempre ordenados pelo backend NASM.

const ALGORITMOS = {
  bubble: {
    titulo: "Bubble Sort",
    descricaoExemplo:
      "Compara pares vizinhos e troca quando estao fora de ordem, " +
      "borbulhando o maior valor pro fim a cada passagem.",
  },
  insertion: {
    titulo: "Insertion Sort",
    descricaoExemplo:
      "Pega cada elemento e o insere na posicao correta entre os " +
      "elementos ja ordenados a esquerda.",
  },
};

const LIMITE_AVISO = 700_000;

async function apiGet(path) {
  const res = await fetch(path);
  const dados = await res.json();
  if (!res.ok) throw new Error(dados.erro || "erro na requisicao");
  return dados;
}

async function apiPost(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const dados = await res.json();
  if (!res.ok) throw new Error(dados.erro || "erro na requisicao");
  return dados;
}

function formatarNumero(n) {
  return n.toLocaleString("pt-BR");
}

function formatarMinutos(segundos) {
  const minutos = Math.floor(segundos / 60);
  const resto = segundos - minutos * 60;
  return `${String(minutos).padStart(2, "0")}:${resto.toFixed(3).padStart(6, "0")} min`;
}

// ---------- animacao de exemplo (loop, 5 numeros) ----------

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function novoArrayExemplo() {
  const n = 5;
  const valores = [];
  while (valores.length < n) {
    const v = 15 + Math.floor(Math.random() * 80);
    if (!valores.includes(v)) valores.push(v);
  }
  return valores;
}

function* passosBubble(arr) {
  const a = arr.slice();
  const n = a.length;
  for (let i = 0; i < n - 1; i++) {
    for (let j = 0; j < n - 1 - i; j++) {
      yield { tipo: "comparar", indices: [j, j + 1] };
      if (a[j] > a[j + 1]) {
        [a[j], a[j + 1]] = [a[j + 1], a[j]];
        yield { tipo: "trocar", indices: [j, j + 1], estado: a.slice() };
      }
    }
    yield { tipo: "fixar", indice: n - 1 - i };
  }
  yield { tipo: "fixar", indice: 0 };
}

function* passosInsertion(arr) {
  const a = arr.slice();
  const n = a.length;
  yield { tipo: "fixar", indice: 0 };
  for (let i = 1; i < n; i++) {
    let j = i;
    yield { tipo: "comparar", indices: [j - 1, j] };
    while (j > 0 && a[j - 1] > a[j]) {
      [a[j - 1], a[j]] = [a[j], a[j - 1]];
      yield { tipo: "trocar", indices: [j - 1, j], estado: a.slice() };
      j--;
      if (j > 0) yield { tipo: "comparar", indices: [j - 1, j] };
    }
    for (let k = 0; k <= i; k++) yield { tipo: "fixar", indice: k };
  }
}

class Animacao {
  constructor(container, algoritmo) {
    this.container = container;
    this.algoritmo = algoritmo;
    this.rodando = true;
  }

  destruir() {
    this.rodando = false;
  }

  renderBase(valores) {
    this.container.innerHTML = "";
    this.barras = valores.map((v, i) => {
      const el = document.createElement("div");
      el.className = "barra";
      el.style.left = `${i * 20}%`;
      el.style.height = `${20 + v}px`;
      el.textContent = v;
      this.container.appendChild(el);
      return el;
    });
  }

  setEstado(valores) {
    valores.forEach((v, i) => {
      this.barras[i].style.left = `${i * 20}%`;
    });
  }

  limparClasses() {
    this.barras.forEach((b) => b.classList.remove("comparando", "trocando"));
  }

  async loop() {
    while (this.rodando) {
      const valores = novoArrayExemplo();
      this.renderBase(valores);
      await sleep(500);

      const gerador =
        this.algoritmo === "bubble" ? passosBubble(valores) : passosInsertion(valores);

      for (const passo of gerador) {
        if (!this.rodando) return;
        this.limparClasses();

        if (passo.tipo === "comparar") {
          const [i, j] = passo.indices;
          this.barras[i].classList.add("comparando");
          this.barras[j].classList.add("comparando");
          await sleep(450);
        } else if (passo.tipo === "trocar") {
          const [i, j] = passo.indices;
          this.barras[i].classList.add("trocando");
          this.barras[j].classList.add("trocando");
          [this.barras[i], this.barras[j]] = [this.barras[j], this.barras[i]];
          this.setEstado(passo.estado);
          await sleep(450);
        } else if (passo.tipo === "fixar") {
          this.barras[passo.indice].classList.remove("comparando", "trocando");
          this.barras[passo.indice].classList.add("ordenada");
        }
      }

      await sleep(1200);
    }
  }
}

// ---------- painel de cada aba ----------

class Painel {
  constructor(algoritmoKey, secaoEl) {
    this.key = algoritmoKey;
    this.el = secaoEl;
    this.jobId = null;
    this.cronometroInterval = null;

    this.selectTamanho = this.el.querySelector(".select-tamanho");
    this.selectTipo = this.el.querySelector(".select-tipo");
    this.btnGerar = this.el.querySelector(".btn-gerar");
    this.statusGerar = this.el.querySelector(".status-gerar");
    this.selectArquivo = this.el.querySelector(".select-arquivo");
    this.btnAtualizar = this.el.querySelector(".btn-atualizar");
    this.btnOrdenar = this.el.querySelector(".btn-ordenar");
    this.cronometroValor = this.el.querySelector(".cronometro-valor");
    this.progressoPreenchimento = this.el.querySelector(".progresso-preenchimento");
    this.progressoValor = this.el.querySelector(".progresso-valor");
    this.resultado = this.el.querySelector(".resultado");
    this.descricaoExemplo = this.el.querySelector(".descricao-exemplo");

    this.descricaoExemplo.textContent = ALGORITMOS[algoritmoKey].descricaoExemplo;

    this.btnGerar.addEventListener("click", () => this.gerarDataset());
    this.btnAtualizar.addEventListener("click", () => this.atualizarArquivos());
    this.btnOrdenar.addEventListener("click", () => this.ordenar());

    const containerBarras = this.el.querySelector(".barras");
    this.animacao = new Animacao(containerBarras, algoritmoKey);
    this.animacao.loop();
  }

  async carregarConfig(config) {
    this.selectTamanho.innerHTML = config.tamanhos
      .map((t) => `<option value="${t}">${formatarNumero(t)}</option>`)
      .join("");
    this.selectTipo.innerHTML = config.tipos
      .map((t) => `<option value="${t}">${t}</option>`)
      .join("");
    await this.atualizarArquivos();
  }

  async atualizarArquivos() {
    const { arquivos } = await apiGet("/api/arquivos");
    if (arquivos.length === 0) {
      this.selectArquivo.innerHTML = `<option value="">(nenhum dataset gerado)</option>`;
      this.btnOrdenar.disabled = true;
      return;
    }
    this.selectArquivo.innerHTML = arquivos
      .map((a) => `<option value="${a.nome}">${a.nome}</option>`)
      .join("");
    this.btnOrdenar.disabled = false;
  }

  async gerarDataset() {
    this.btnGerar.disabled = true;
    this.statusGerar.textContent = "Gerando...";
    try {
      const tamanho = parseInt(this.selectTamanho.value, 10);
      const tipo = this.selectTipo.value;
      const { nome } = await apiPost("/api/gerar", { tamanho, tipo });
      this.statusGerar.textContent = `Gerado: ${nome}`;
      await this.atualizarArquivos();
      this.selectArquivo.value = nome;
    } catch (err) {
      this.statusGerar.textContent = `Erro: ${err.message}`;
    } finally {
      this.btnGerar.disabled = false;
    }
  }

  pararCronometro() {
    if (this.cronometroInterval) {
      clearInterval(this.cronometroInterval);
      this.cronometroInterval = null;
    }
  }

  iniciarCronometro() {
    this.pararCronometro();
    const inicio = performance.now();
    this.cronometroValor.classList.add("rodando");
    this.cronometroInterval = setInterval(() => {
      const decorrido = (performance.now() - inicio) / 1000;
      this.cronometroValor.textContent = formatarMinutos(decorrido);
    }, 47);
  }

  setProgresso(percent) {
    this.progressoPreenchimento.style.width = `${percent}%`;
    this.progressoValor.textContent = `${percent.toFixed(0)}%`;
  }

  async ordenar() {
    const arquivo = this.selectArquivo.value;
    if (!arquivo) return;

    const opcao = this.selectArquivo.selectedOptions[0];
    const match = arquivo.match(/_(\d+)\.txt$/);
    const tamanho = match ? parseInt(match[1], 10) : 0;
    if (tamanho >= LIMITE_AVISO) {
      const nomeAlgo = ALGORITMOS[this.key].titulo;
      const ok = confirm(
        `Aviso: ${nomeAlgo} e O(n^2). Com ${formatarNumero(tamanho)} numeros isso ` +
          `pode demorar bastante (minutos a horas). Continuar?`
      );
      if (!ok) return;
    }

    this.btnOrdenar.disabled = true;
    this.resultado.textContent = "";
    this.setProgresso(0);
    this.iniciarCronometro();

    try {
      const { job_id, n } = await apiPost("/api/ordenar", {
        arquivo,
        algoritmo: this.key,
      });
      this.jobId = job_id;
      this.resultado.textContent = `Ordenando ${formatarNumero(n)} numeros...`;
      await this.acompanharJob(job_id);
    } catch (err) {
      this.pararCronometro();
      this.cronometroValor.classList.remove("rodando");
      this.resultado.innerHTML = `<span class="aviso">Erro: ${err.message}</span>`;
      this.btnOrdenar.disabled = false;
    }
  }

  async acompanharJob(jobId) {
    while (true) {
      const status = await apiGet(`/api/status?job_id=${jobId}`);
      if (status.status === "running") {
        this.setProgresso(status.percent ?? 0);
        await sleep(300);
        continue;
      }
      this.pararCronometro();
      this.cronometroValor.classList.remove("rodando");

      if (status.status === "error") {
        this.resultado.innerHTML = `<span class="aviso">Erro: ${status.erro}</span>`;
      } else {
        this.setProgresso(100);
        this.cronometroValor.textContent = formatarMinutos(status.tempo);
        const href = `/api/resultado?arquivo=${encodeURIComponent(status.arquivo_saida)}`;
        this.resultado.innerHTML =
          `Concluido em ${formatarMinutos(status.tempo)}<br>` +
          `Resultado salvo em <code>resultados/${status.arquivo_saida}</code> — ` +
          `<a href="${href}" download>baixar</a>`;
      }
      this.btnOrdenar.disabled = false;
      return;
    }
  }
}

// ---------- montagem da pagina ----------

async function main() {
  const template = document.getElementById("template-painel");
  const conteudo = document.getElementById("conteudo");
  const config = await apiGet("/api/config");

  const paineis = {};
  for (const key of Object.keys(ALGORITMOS)) {
    const fragmento = template.content.cloneNode(true);
    const secao = fragmento.querySelector(".painel");
    secao.dataset.aba = key;
    conteudo.appendChild(fragmento);
    const secaoEl = conteudo.querySelector(`.painel[data-aba="${key}"]`);
    const painel = new Painel(key, secaoEl);
    await painel.carregarConfig(config);
    paineis[key] = painel;
  }

  document.querySelector(`.painel[data-aba="bubble"]`).classList.add("ativa");

  document.querySelectorAll(".aba-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".aba-btn").forEach((b) => b.classList.remove("ativa"));
      document.querySelectorAll(".painel").forEach((p) => p.classList.remove("ativa"));
      btn.classList.add("ativa");
      document.querySelector(`.painel[data-aba="${btn.dataset.aba}"]`).classList.add("ativa");
    });
  });
}

main().catch((err) => {
  document.getElementById("conteudo").innerHTML =
    `<p style="color:#ff8a65">Erro ao iniciar: ${err.message}</p>`;
});
