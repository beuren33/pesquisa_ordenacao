const ALGORITMOS = {
  bubble: {
    titulo: "Bubble Sort",
    descricaoExemplo:
      "Compara pares vizinhos e troca quando estao fora de ordem, " +
      "levando o maior valor pro fim a cada passagem.",
  },
  insertion: {
    titulo: "Insertion Sort",
    descricaoExemplo:
      "Pega cada elemento e o insere na posicao correta entre os " +
      "elementos ja ordenados a esquerda.",
  },
  shell: {
    titulo: "Shell Sort",
    descricaoExemplo:
      "Como o Insertion Sort, mas compara elementos distantes " +
      "primeiro, reduzindo o espaço a cada passada ate chegar em 1.",
  },
  selection: {
    titulo: "Selection Sort",
    descricaoExemplo:
      "Encontra o menor elemento restante e o troca pra posicao atual, " +
      "avancando da esquerda pra direita.",
  },
  quick: {
    titulo: "Quick Sort",
    descricaoExemplo:
      "Escolhe um pivo, particiona o array em menores/maiores que ele " +
      "e repete recursivamente em cada metade.",
  },
  merge: {
    titulo: "Merge Sort",
    descricaoExemplo:
      "Divide o array ao meio recursivamente e depois intercala " +
      "(merge) as metades ja ordenadas de volta.",
  },
  radix: {
    titulo: "Radix Sort",
    descricaoExemplo:
      "Ordena por counting sort, digito a digito (do menos ao mais " +
      "significativo), sem comparar os numeros entre si diretamente.",
  },
  heap: {
    titulo: "Heap Sort",
    descricaoExemplo:
      "Monta um heap maximo com os numeros e vai tirando o maior " +
      "elemento do topo pra posicao final, um de cada vez.",
  },
};

const LIMITE_AVISO = 700_000;
const ALGORITMOS_QUADRATICOS = new Set(["bubble", "insertion", "selection"]);

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

function* passosShell(arr) {
  const a = arr.slice();
  const n = a.length;
  let gap = Math.floor(n / 2);
  while (gap > 0) {
    for (let i = gap; i < n; i++) {
      let j = i;
      yield { tipo: "comparar", indices: [j - gap, j] };
      while (j >= gap && a[j - gap] > a[j]) {
        [a[j - gap], a[j]] = [a[j], a[j - gap]];
        yield { tipo: "trocar", indices: [j - gap, j], estado: a.slice() };
        j -= gap;
        if (j >= gap) yield { tipo: "comparar", indices: [j - gap, j] };
      }
    }
    gap = Math.floor(gap / 2);
  }
  for (let k = 0; k < n; k++) yield { tipo: "fixar", indice: k };
}

function* passosSelection(arr) {
  const a = arr.slice();
  const n = a.length;
  for (let i = 0; i < n - 1; i++) {
    let minIdx = i;
    for (let j = i + 1; j < n; j++) {
      yield { tipo: "comparar", indices: [minIdx, j] };
      if (a[j] < a[minIdx]) minIdx = j;
    }
    if (minIdx !== i) {
      [a[i], a[minIdx]] = [a[minIdx], a[i]];
      yield { tipo: "trocar", indices: [i, minIdx], estado: a.slice() };
    }
    yield { tipo: "fixar", indice: i };
  }
  yield { tipo: "fixar", indice: n - 1 };
}

function* passosQuick(arr) {
  const a = arr.slice();

  function* particionar(lo, hi) {
    const pivot = a[hi];
    let i = lo - 1;
    for (let j = lo; j < hi; j++) {
      yield { tipo: "comparar", indices: [j, hi] };
      if (a[j] <= pivot) {
        i++;
        if (i !== j) {
          [a[i], a[j]] = [a[j], a[i]];
          yield { tipo: "trocar", indices: [i, j], estado: a.slice() };
        }
      }
    }
    if (i + 1 !== hi) {
      [a[i + 1], a[hi]] = [a[hi], a[i + 1]];
      yield { tipo: "trocar", indices: [i + 1, hi], estado: a.slice() };
    }
    return i + 1;
  }

  function* ordenar(lo, hi) {
    if (lo >= hi) {
      if (lo === hi) yield { tipo: "fixar", indice: lo };
      return;
    }
    const p = yield* particionar(lo, hi);
    yield { tipo: "fixar", indice: p };
    yield* ordenar(lo, p - 1);
    yield* ordenar(p + 1, hi);
  }

  yield* ordenar(0, a.length - 1);
  for (let k = 0; k < a.length; k++) yield { tipo: "fixar", indice: k };
}

function* passosMerge(arr) {
  const a = arr.slice();
  const n = a.length;
  const temp = new Array(n);

  function* mesclar(lo, mid, hi) {
    let i = lo;
    let j = mid + 1;
    let k = lo;
    while (i <= mid && j <= hi) {
      yield { tipo: "comparar", indices: [i, j] };
      if (a[i] <= a[j]) temp[k++] = a[i++];
      else temp[k++] = a[j++];
    }
    while (i <= mid) temp[k++] = a[i++];
    while (j <= hi) temp[k++] = a[j++];
    for (let x = lo; x <= hi; x++) a[x] = temp[x];
    const destaque = [];
    for (let x = lo; x <= hi; x++) destaque.push(x);
    yield { tipo: "definir", estado: a.slice(), destaque };
  }

  function* ordenar(lo, hi) {
    if (lo >= hi) return;
    const mid = lo + Math.floor((hi - lo) / 2);
    yield* ordenar(lo, mid);
    yield* ordenar(mid + 1, hi);
    yield* mesclar(lo, mid, hi);
  }

  yield* ordenar(0, n - 1);
  for (let k = 0; k < n; k++) yield { tipo: "fixar", indice: k };
}

function* passosRadix(arr) {
  const a = arr.slice();
  const n = a.length;
  const max = Math.max(...a);

  for (let exp = 1; Math.floor(max / exp) > 0; exp *= 10) {
    const baldes = Array.from({ length: 10 }, () => []);
    for (let i = 0; i < n; i++) {
      const digito = Math.floor(a[i] / exp) % 10;
      baldes[digito].push(a[i]);
    }
    let k = 0;
    for (let d = 0; d < 10; d++) {
      for (const v of baldes[d]) a[k++] = v;
    }
    yield { tipo: "definir", estado: a.slice(), destaque: a.map((_, i) => i) };
  }
  for (let k = 0; k < n; k++) yield { tipo: "fixar", indice: k };
}

function* passosHeap(arr) {
  const a = arr.slice();
  const n = a.length;

  function* siftDown(size, i) {
    while (true) {
      let largest = i;
      const l = 2 * i + 1;
      const r = 2 * i + 2;
      if (l < size) {
        yield { tipo: "comparar", indices: [l, largest] };
        if (a[l] > a[largest]) largest = l;
      }
      if (r < size) {
        yield { tipo: "comparar", indices: [r, largest] };
        if (a[r] > a[largest]) largest = r;
      }
      if (largest === i) return;
      [a[i], a[largest]] = [a[largest], a[i]];
      yield { tipo: "trocar", indices: [i, largest], estado: a.slice() };
      i = largest;
    }
  }

  for (let i = Math.floor(n / 2) - 1; i >= 0; i--) yield* siftDown(n, i);
  for (let i = n - 1; i > 0; i--) {
    [a[0], a[i]] = [a[i], a[0]];
    yield { tipo: "trocar", indices: [0, i], estado: a.slice() };
    yield { tipo: "fixar", indice: i };
    yield* siftDown(i, 0);
  }
  yield { tipo: "fixar", indice: 0 };
}

const GERADORES_PASSOS = {
  bubble: passosBubble,
  insertion: passosInsertion,
  shell: passosShell,
  selection: passosSelection,
  quick: passosQuick,
  merge: passosMerge,
  radix: passosRadix,
  heap: passosHeap,
};

class Animacao {
  constructor(container, algoritmo) {
    this.container = container;
    this.algoritmo = algoritmo;
    this.modo = algoritmo === "heap" ? "heap" : algoritmo === "merge" ? "merge" : "barras";

    this.multiplicadorAtraso = this.modo === "heap" || this.modo === "merge" ? 2 : 1;
    this.rodando = true;
  }

  espera(ms) {
    return sleep(ms * this.multiplicadorAtraso);
  }

  destruir() {
    this.rodando = false;
  }

  renderBase(valores) {
    this.container.innerHTML = "";
    if (this.modo === "heap") {
      this.renderArvoreBase(valores);
      return;
    }
    if (this.modo === "merge") {
      this.renderArvoreMergeBase(valores);
      return;
    }
    this.barras = valores.map((v, i) => {
      const el = document.createElement("div");
      el.className = "barra";
      el.style.left = `${i * 20}%`;
      el.style.height = `${20 + v * 3}px`;
      el.textContent = v;
      this.container.appendChild(el);
      return el;
    });
  }

  renderArvoreBase(valores) {
    const n = valores.length;
    const largura = 500;
    const altura = 300;
    const maxNivel = Math.floor(Math.log2(n));
    const alturaNivel = (altura - 60) / (maxNivel + 1 || 1);
    const raio = 22;

    const posicoes = valores.map((_, i) => {
      const nivel = Math.floor(Math.log2(i + 1));
      const inicioNivel = 2 ** nivel - 1;
      const posNoNivel = i - inicioNivel;
      const slots = 2 ** nivel;
      const x = ((posNoNivel + 1) / (slots + 1)) * largura;
      const y = 34 + nivel * alturaNivel;
      return { x, y };
    });

    const svg = criarSvg("svg", {
      class: "arvore-svg",
      viewBox: `0 0 ${largura} ${altura}`,
    });

    this.arvoreLinhas = new Map();
    for (let i = 1; i < n; i++) {
      const pai = Math.floor((i - 1) / 2);
      const linha = criarSvg("line", {
        class: "aresta",
        x1: posicoes[pai].x,
        y1: posicoes[pai].y,
        x2: posicoes[i].x,
        y2: posicoes[i].y,
      });
      svg.appendChild(linha);
      this.arvoreLinhas.set(i, linha);
    }

    this.noCirculos = [];
    this.noTextos = [];
    valores.forEach((v, i) => {
      const { x, y } = posicoes[i];
      const circulo = criarSvg("circle", { class: "no", cx: x, cy: y, r: raio });
      const texto = criarSvg("text", { class: "no-texto", x, y: y + 5, "text-anchor": "middle" });
      texto.textContent = v;
      svg.appendChild(circulo);
      svg.appendChild(texto);
      this.noCirculos.push(circulo);
      this.noTextos.push(texto);
    });

    this.container.appendChild(svg);
  }

  construirArvoreMerge(n) {
    const nos = [];
    let maxNivel = 0;

    const constroi = (lo, hi, nivel) => {
      maxNivel = Math.max(maxNivel, nivel);
      const no = { lo, hi, nivel, x: (lo + hi) / 2, filhos: [] };
      nos.push(no);
      if (lo === hi) return no;
      const mid = lo + Math.floor((hi - lo) / 2);
      no.filhos.push(constroi(lo, mid, nivel + 1));
      no.filhos.push(constroi(mid + 1, hi, nivel + 1));
      return no;
    };
    constroi(0, n - 1, 0);
    return { nos, maxNivel };
  }

  renderArvoreMergeBase(valores) {
    const n = valores.length;
    const largura = 700;
    const altura = 300;
    const alturaNo = 26;
    const { nos, maxNivel } = this.construirArvoreMerge(n);
    const alturaNivel = (altura - 50) / (maxNivel + 1 || 1);
    const larguraElemento = largura / n;

    const posPixel = (no) => ({
      x: (no.x + 0.5) * larguraElemento,
      y: 24 + no.nivel * alturaNivel,
    });

    const svg = criarSvg("svg", { class: "arvore-svg", viewBox: `0 0 ${largura} ${altura}` });

    const defs = criarSvg("defs", {});
    const marcador = criarSvg("marker", {
      id: "seta-merge",
      markerWidth: 8,
      markerHeight: 8,
      refX: 6,
      refY: 3,
      orient: "auto",
    });
    marcador.appendChild(criarSvg("path", { d: "M0,0 L6,3 L0,6 Z", class: "seta-merge-ponta" }));
    defs.appendChild(marcador);
    svg.appendChild(defs);

    this.mergeLinhas = new Map();
    this.mergeFilhos = new Map();
    nos.forEach((no) => {
      if (no.filhos.length === 0) return;
      const pPai = posPixel(no);
      const chaveFilhos = [];
      no.filhos.forEach((filho) => {
        const pFilho = posPixel(filho);

        const linha = criarSvg("line", {
          class: "aresta",
          x1: pFilho.x,
          y1: pFilho.y - alturaNo / 2,
          x2: pPai.x,
          y2: pPai.y + alturaNo / 2,
          "marker-end": "url(#seta-merge)",
        });
        svg.appendChild(linha);
        const chaveFilho = `${filho.lo}-${filho.hi}`;
        this.mergeLinhas.set(chaveFilho, linha);
        chaveFilhos.push(chaveFilho);
      });
      this.mergeFilhos.set(`${no.lo}-${no.hi}`, chaveFilhos);
    });

    this.mergeNos = new Map();
    nos.forEach((no) => {
      const { x, y } = posPixel(no);
      const largRetangulo = (no.hi - no.lo + 1) * larguraElemento - 4;
      const ehFolha = no.filhos.length === 0;
      const rect = criarSvg("rect", {
        class: "no-merge" + (ehFolha ? "" : " no-merge-pendente"),
        x: x - largRetangulo / 2,
        y: y - alturaNo / 2,
        width: largRetangulo,
        height: alturaNo,
        rx: 4,
      });
      const texto = criarSvg("text", {
        class: "no-merge-texto",
        x,
        y: y + 4,
        "text-anchor": "middle",
      });
      texto.textContent = ehFolha ? valores[no.lo] : "";
      svg.appendChild(rect);
      svg.appendChild(texto);
      this.mergeNos.set(`${no.lo}-${no.hi}`, { rect, texto });
    });

    this.container.appendChild(svg);
  }

  setEstado(valores) {
    valores.forEach((v, i) => {
      this.barras[i].style.left = `${i * 20}%`;
    });
  }

  setConteudo(valores) {
    valores.forEach((v, i) => {
      this.barras[i].textContent = v;
      this.barras[i].style.height = `${20 + v * 3}px`;
    });
  }

  limparClasses() {
    if (this.modo === "heap") {
      this.noCirculos.forEach((c) => c.classList.remove("comparando", "trocando"));
      return;
    }
    if (this.modo === "merge") return;
    this.barras.forEach((b) => b.classList.remove("comparando", "trocando"));
  }

  async loop() {
    while (this.rodando) {
      const valores = novoArrayExemplo();
      this.renderBase(valores);
      await this.espera(500);

      const gerador = GERADORES_PASSOS[this.algoritmo](valores);

      for (const passo of gerador) {
        if (!this.rodando) return;
        this.limparClasses();

        if (this.modo === "heap") {
          if (passo.tipo === "comparar") {
            const [i, j] = passo.indices;
            this.noCirculos[i].classList.add("comparando");
            this.noCirculos[j].classList.add("comparando");
            await this.espera(450);
          } else if (passo.tipo === "trocar") {
            const [i, j] = passo.indices;
            const filho = Math.max(i, j);
            const linha = this.arvoreLinhas.get(filho);

            this.noCirculos[i].classList.add("comparando");
            this.noCirculos[j].classList.add("comparando");
            if (linha) linha.classList.add("seta-ativa");
            await this.espera(500);

            this.noCirculos[i].classList.remove("comparando");
            this.noCirculos[j].classList.remove("comparando");
            if (linha) linha.classList.remove("seta-ativa");
            this.noCirculos[i].classList.add("trocando");
            this.noCirculos[j].classList.add("trocando");
            this.noTextos[i].textContent = passo.estado[i];
            this.noTextos[j].textContent = passo.estado[j];
            await this.espera(450);
          } else if (passo.tipo === "fixar") {
            this.noCirculos[passo.indice].classList.remove("comparando", "trocando");
            this.noCirculos[passo.indice].classList.add("ordenada");
          }
          continue;
        }

        if (this.modo === "merge") {

          if (passo.tipo === "definir") {
            const lo = passo.destaque[0];
            const hi = passo.destaque[passo.destaque.length - 1];
            const chave = `${lo}-${hi}`;
            const no = this.mergeNos.get(chave);
            if (no) {

              const chaveFilhos = this.mergeFilhos.get(chave) || [];
              chaveFilhos.forEach((chaveFilho) => {
                const filho = this.mergeNos.get(chaveFilho);
                const linha = this.mergeLinhas.get(chaveFilho);
                if (filho) filho.rect.classList.add("comparando");
                if (linha) linha.classList.add("seta-ativa");
              });
              await this.espera(700);

              chaveFilhos.forEach((chaveFilho) => {
                const filho = this.mergeNos.get(chaveFilho);
                const linha = this.mergeLinhas.get(chaveFilho);
                if (filho) {
                  filho.rect.classList.remove("comparando");
                  filho.rect.classList.add("no-merge-consumida");
                  filho.texto.classList.add("no-merge-consumida");
                }
                if (linha) linha.classList.remove("seta-ativa");
              });

              no.rect.classList.remove("no-merge-pendente");
              no.rect.classList.add("trocando");
              no.texto.textContent = passo.estado.slice(lo, hi + 1).join(" ");
              await this.espera(600);
              no.rect.classList.remove("trocando");
              if (lo === 0 && hi === valores.length - 1) {
                no.rect.classList.add("ordenada");
              }
            }
          }
          continue;
        }

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
        } else if (passo.tipo === "definir") {
          (passo.destaque || []).forEach((idx) => this.barras[idx].classList.add("trocando"));
          this.setConteudo(passo.estado);
          await sleep(450);
        } else if (passo.tipo === "fixar") {
          this.barras[passo.indice].classList.remove("comparando", "trocando");
          this.barras[passo.indice].classList.add("ordenada");
        }
      }

      await this.espera(1200);
    }
  }
}

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
    if (tamanho >= LIMITE_AVISO && ALGORITMOS_QUADRATICOS.has(this.key)) {
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
          `Resultado salvo em <code>resultados/${status.arquivo_saida}</code>, ` +
          `<a href="${href}" download>baixar</a>`;
      }
      this.btnOrdenar.disabled = false;
      return;
    }
  }
}

const CORES_ALGORITMO = {
  bubble: "#e53935",
  insertion: "#1e88e5",
  shell: "#43a047",
  selection: "#fdd835",
  quick: "#8e24aa",
  merge: "#fb8c00",
  radix: "#00acc1",
  heap: "#d81b60",
};

const NOMES_ALGORITMO = {
  bubble: "Bubble Sort",
  insertion: "Insertion Sort",
  shell: "Shell Sort",
  selection: "Selection Sort",
  quick: "Quick Sort",
  merge: "Merge Sort",
  radix: "Radix Sort",
  heap: "Heap Sort",
};

const ORDEM_ALGORITMOS = [
  "bubble", "insertion", "shell", "selection", "quick", "merge", "radix", "heap",
];

function criarSvg(tag, attrs) {
  const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  return el;
}

function criarTooltip(container) {
  const el = document.createElement("div");
  el.className = "grafico-tooltip";
  el.hidden = true;
  container.appendChild(el);

  function mostrar(ev, texto) {
    el.textContent = texto;
    el.hidden = false;
    mover(ev);
  }
  function mover(ev) {
    const rect = container.getBoundingClientRect();
    el.style.left = `${ev.clientX - rect.left + 14}px`;
    el.style.top = `${ev.clientY - rect.top + 14}px`;
  }
  function esconder() {
    el.hidden = true;
  }

  return { mostrar, mover, esconder };
}

function renderLegenda(algoritmos = ORDEM_ALGORITMOS) {
  const div = document.createElement("div");
  div.className = "legenda-comparativo";
  algoritmos.forEach((algoritmo) => {
    const item = document.createElement("span");
    item.className = "legenda-item";
    const cor = document.createElement("span");
    cor.className = "legenda-cor";
    cor.style.background = CORES_ALGORITMO[algoritmo];
    item.appendChild(cor);
    item.appendChild(document.createTextNode(NOMES_ALGORITMO[algoritmo]));
    div.appendChild(item);
  });
  return div;
}

function ultimoRegistroPorAlgoritmoTamanho(registros, tipo) {

  const mapa = new Map();
  for (const algoritmo of ORDEM_ALGORITMOS) mapa.set(algoritmo, new Map());
  for (const r of registros) {
    if (r.tipo !== tipo) continue;
    mapa.get(r.algoritmo)?.set(r.tamanho, r);
  }
  return mapa;
}

function formatarTempo(tempo) {
  if (tempo < 1) return `${(tempo * 1000).toFixed(1)}ms`;
  if (tempo >= 60) return `${tempo.toFixed(2)}s (${(tempo / 60).toFixed(2)} min)`;
  return `${tempo.toFixed(2)}s`;
}

function renderGraficoLinha(registros, tipo, { algoritmos = ORDEM_ALGORITMOS, escala = "log", titulo: tituloTxt } = {}) {
  const porAlgoritmo = ultimoRegistroPorAlgoritmoTamanho(registros, tipo);
  const tamanhos = [...new Set(registros.map((r) => r.tamanho))].sort((a, b) => a - b);

  const largura = 1400;
  const alturaGrafico = 520;
  const margemEsq = 150;
  const margemDir = 32;
  const margemBaixo = 52;
  const margemTopo = 24;
  const larguraUtil = largura - margemEsq - margemDir;

  const todosValores = algoritmos
    .flatMap((algoritmo) => [...(porAlgoritmo.get(algoritmo)?.values() ?? [])])
    .map((r) => r.tempo_s)
    .filter((v) => v > 0);
  const maxTempo = todosValores.length ? Math.max(...todosValores) : 1;
  const minTempo = todosValores.length ? Math.min(...todosValores) : 0.0001;

  const logMin = Math.log10(Math.max(minTempo, 0.0001));
  const logMax = Math.log10(Math.max(maxTempo, minTempo * 10));
  const linMax = maxTempo * 1.15;

  function x(tamanho) {
    if (tamanhos.length <= 1) return margemEsq + larguraUtil / 2;
    const idx = tamanhos.indexOf(tamanho);
    return margemEsq + (idx / (tamanhos.length - 1)) * larguraUtil;
  }
  function y(tempo) {
    if (escala === "linear") {
      const frac = linMax > 0 ? tempo / linMax : 0;
      return margemTopo + alturaGrafico - frac * alturaGrafico;
    }
    const t = Math.max(tempo, 0.0001);
    const frac = (Math.log10(t) - logMin) / (logMax - logMin || 1);
    return margemTopo + alturaGrafico - frac * alturaGrafico;
  }

  const container = document.createElement("div");
  container.className = "grafico-tamanho";
  const tooltip = criarTooltip(container);

  const svg = criarSvg("svg", {
    class: "grafico-svg",
    viewBox: `0 0 ${largura} ${alturaGrafico + margemBaixo + margemTopo}`,
  });

  const grade = criarSvg("g", { class: "grade" });
  const N_LINHAS_Y = 5;
  for (let i = 0; i <= N_LINHAS_Y; i++) {
    const yy = margemTopo + (alturaGrafico / N_LINHAS_Y) * i;
    grade.appendChild(criarSvg("line", { x1: margemEsq, x2: largura - margemDir, y1: yy, y2: yy }));
  }
  tamanhos.forEach((tamanho) => {
    const xx = x(tamanho);
    grade.appendChild(criarSvg("line", { x1: xx, x2: xx, y1: margemTopo, y2: margemTopo + alturaGrafico }));
  });
  svg.appendChild(grade);

  svg.appendChild(
    criarSvg("rect", {
      x: margemEsq,
      y: margemTopo,
      width: larguraUtil,
      height: alturaGrafico,
      fill: "none",
      class: "moldura",
    })
  );

  for (let i = 0; i <= N_LINHAS_Y; i++) {
    const frac = i / N_LINHAS_Y;
    let tempo;
    if (escala === "linear") {
      tempo = linMax * (1 - frac);
    } else {
      const logV = logMin + (1 - frac) * (logMax - logMin);
      tempo = Math.pow(10, logV);
    }
    const yy = margemTopo + (alturaGrafico / N_LINHAS_Y) * i;
    const label = criarSvg("text", { x: margemEsq - 10, y: yy + 4, "text-anchor": "end" });
    label.textContent = formatarTempo(tempo);
    svg.appendChild(label);
  }

  tamanhos.forEach((tamanho) => {
    const xx = x(tamanho);
    const label = criarSvg("text", {
      x: xx,
      y: margemTopo + alturaGrafico + 22,
      "text-anchor": "middle",
    });
    label.textContent = formatarNumero(tamanho);
    svg.appendChild(label);
  });

  algoritmos.forEach((algoritmo) => {
    const pontos = tamanhos
      .map((tamanho) => {
        const registro = porAlgoritmo.get(algoritmo)?.get(tamanho);
        return registro ? { tamanho, tempo: registro.tempo_s } : null;
      })
      .filter(Boolean);
    if (pontos.length === 0) return;

    const d = pontos
      .map((p, i) => `${i === 0 ? "M" : "L"} ${x(p.tamanho)} ${y(p.tempo)}`)
      .join(" ");
    svg.appendChild(
      criarSvg("path", {
        d,
        fill: "none",
        stroke: CORES_ALGORITMO[algoritmo],
        "stroke-width": 2.5,
      })
    );
    pontos.forEach((p) => {
      const ponto = criarSvg("circle", {
        cx: x(p.tamanho),
        cy: y(p.tempo),
        r: 4,
        fill: CORES_ALGORITMO[algoritmo],
        class: "ponto-grafico",
      });
      const texto = `${formatarNumero(p.tamanho)}: ${formatarTempo(p.tempo)}`;
      ponto.addEventListener("mouseenter", (ev) => tooltip.mostrar(ev, texto));
      ponto.addEventListener("mousemove", (ev) => tooltip.mover(ev));
      ponto.addEventListener("mouseleave", () => tooltip.esconder());
      svg.appendChild(ponto);
    });
  });

  const titulo = document.createElement("h3");
  titulo.textContent = tituloTxt ?? `Tempo x tamanho do dataset ${tipo}`;
  container.appendChild(titulo);
  container.appendChild(renderLegenda(algoritmos));
  container.appendChild(svg);
  return container;
}

function renderGraficoBarrasMaiorTamanho(registros, tipo) {
  const tamanhos = [...new Set(registros.map((r) => r.tamanho))].sort((a, b) => a - b);
  const maiorTamanho = tamanhos[tamanhos.length - 1];
  const porAlgoritmo = ultimoRegistroPorAlgoritmoTamanho(registros, tipo);

  const barras = ORDEM_ALGORITMOS.map((algoritmo) => {
    const registro = porAlgoritmo.get(algoritmo)?.get(maiorTamanho);
    return { algoritmo, tempo: registro ? registro.tempo_s : null };
  });

  const largura = 1400;
  const alturaGrafico = 460;
  const margemEsq = 150;
  const margemDir = 32;
  const margemBaixo = 48;
  const margemTopo = 24;
  const larguraUtil = largura - margemEsq - margemDir;

  const valores = barras.map((b) => b.tempo).filter((v) => v > 0);
  const maxTempo = valores.length ? Math.max(...valores) : 1;
  const minTempo = valores.length ? Math.min(...valores) : 0.0001;
  const logMin = Math.log10(Math.max(minTempo, 0.0001));
  const logMax = Math.log10(Math.max(maxTempo, minTempo * 10));

  function alturaBarra(tempo) {
    const t = Math.max(tempo, 0.0001);
    const frac = (Math.log10(t) - logMin) / (logMax - logMin || 1);
    return frac * alturaGrafico;
  }

  const larguraGrupo = larguraUtil / barras.length;
  const larguraBarra = larguraGrupo * 0.55;

  const svg = criarSvg("svg", {
    class: "grafico-svg",
    viewBox: `0 0 ${largura} ${alturaGrafico + margemBaixo + margemTopo}`,
  });

  const grade = criarSvg("g", { class: "grade" });
  const N_LINHAS_Y = 5;
  for (let i = 0; i <= N_LINHAS_Y; i++) {
    const yy = margemTopo + (alturaGrafico / N_LINHAS_Y) * i;
    grade.appendChild(criarSvg("line", { x1: margemEsq, x2: largura - margemDir, y1: yy, y2: yy }));
  }
  svg.appendChild(grade);
  svg.appendChild(
    criarSvg("rect", {
      x: margemEsq,
      y: margemTopo,
      width: larguraUtil,
      height: alturaGrafico,
      fill: "none",
      class: "moldura",
    })
  );

  for (let i = 0; i <= N_LINHAS_Y; i++) {
    const frac = i / N_LINHAS_Y;
    const logV = logMin + (1 - frac) * (logMax - logMin);
    const tempo = Math.pow(10, logV);
    const yy = margemTopo + (alturaGrafico / N_LINHAS_Y) * i;
    const label = criarSvg("text", { x: margemEsq - 10, y: yy + 4, "text-anchor": "end" });
    label.textContent = formatarTempo(tempo);
    svg.appendChild(label);
  }

  barras.forEach((b, i) => {
    const xGrupo = margemEsq + i * larguraGrupo + (larguraGrupo - larguraBarra) / 2;
    if (b.tempo == null) return;
    const h = Math.max(alturaBarra(b.tempo), 1);
    const yTopo = margemTopo + alturaGrafico - h;
    const rect = criarSvg("rect", {
      x: xGrupo,
      y: yTopo,
      width: larguraBarra,
      height: h,
      fill: CORES_ALGORITMO[b.algoritmo],
      rx: 0,
    });
    const tip = criarSvg("title", {});
    tip.textContent = `${NOMES_ALGORITMO[b.algoritmo]}, ${formatarTempo(b.tempo)}`;
    rect.appendChild(tip);
    svg.appendChild(rect);

    const valorTxt = criarSvg("text", {
      x: xGrupo + larguraBarra / 2,
      y: yTopo - 6,
      "text-anchor": "middle",
      class: "barra-valor",
    });
    valorTxt.textContent = formatarTempo(b.tempo);
    svg.appendChild(valorTxt);

    const rotulo = criarSvg("text", {
      x: xGrupo + larguraBarra / 2,
      y: margemTopo + alturaGrafico + 20,
      "text-anchor": "middle",
    });
    rotulo.textContent = NOMES_ALGORITMO[b.algoritmo];
    svg.appendChild(rotulo);
  });

  const container = document.createElement("div");
  container.className = "grafico-tamanho";
  const titulo = document.createElement("h3");
  titulo.textContent = `${formatarNumero(maiorTamanho)} dataset ${tipo}`;
  container.appendChild(titulo);
  container.appendChild(svg);
  return container;
}

let _registrosCache = null;

function algoritmosSelecionados() {
  const marcados = document.querySelectorAll(
    "#filtro-algoritmos-comparativo input[type=checkbox]:checked"
  );
  return ORDEM_ALGORITMOS.filter((a) =>
    [...marcados].some((el) => el.value === a)
  );
}

function renderGraficoBarrasAgrupadas(registros, tipo, algoritmos) {
  const porAlgoritmo = ultimoRegistroPorAlgoritmoTamanho(registros, tipo);
  const tamanhos = [...new Set(registros.map((r) => r.tamanho))].sort((a, b) => a - b);

  const largura = 1400;
  const alturaGrafico = 460;
  const margemEsq = 150;
  const margemDir = 32;
  const margemBaixo = 48;
  const margemTopo = 24;
  const larguraUtil = largura - margemEsq - margemDir;

  const valores = tamanhos
    .flatMap((tamanho) => algoritmos.map((a) => porAlgoritmo.get(a)?.get(tamanho)?.tempo_s))
    .filter((v) => v > 0);
  const maxTempo = valores.length ? Math.max(...valores) : 1;
  const minTempo = valores.length ? Math.min(...valores) : 0.0001;
  const logMin = Math.log10(Math.max(minTempo, 0.0001));
  const logMax = Math.log10(Math.max(maxTempo, minTempo * 10));

  function alturaBarra(tempo) {
    const t = Math.max(tempo, 0.0001);
    const frac = (Math.log10(t) - logMin) / (logMax - logMin || 1);
    return frac * alturaGrafico;
  }

  const espacoEntreGrupos = 0.35;
  const larguraGrupo = larguraUtil / (tamanhos.length + espacoEntreGrupos * (tamanhos.length - 1));
  const espacamento = larguraGrupo * espacoEntreGrupos;
  const larguraBarra = larguraGrupo / algoritmos.length;

  const svg = criarSvg("svg", {
    class: "grafico-svg",
    viewBox: `0 0 ${largura} ${alturaGrafico + margemBaixo + margemTopo}`,
  });

  const grade = criarSvg("g", { class: "grade" });
  const N_LINHAS_Y = 5;
  for (let i = 0; i <= N_LINHAS_Y; i++) {
    const yy = margemTopo + (alturaGrafico / N_LINHAS_Y) * i;
    grade.appendChild(criarSvg("line", { x1: margemEsq, x2: largura - margemDir, y1: yy, y2: yy }));
  }
  svg.appendChild(grade);
  svg.appendChild(
    criarSvg("rect", {
      x: margemEsq,
      y: margemTopo,
      width: larguraUtil,
      height: alturaGrafico,
      fill: "none",
      class: "moldura",
    })
  );

  for (let i = 0; i <= N_LINHAS_Y; i++) {
    const frac = i / N_LINHAS_Y;
    const logV = logMin + (1 - frac) * (logMax - logMin);
    const tempo = Math.pow(10, logV);
    const yy = margemTopo + (alturaGrafico / N_LINHAS_Y) * i;
    const label = criarSvg("text", { x: margemEsq - 10, y: yy + 4, "text-anchor": "end" });
    label.textContent = formatarTempo(tempo);
    svg.appendChild(label);
  }

  tamanhos.forEach((tamanho, i) => {
    const xGrupo = margemEsq + i * (larguraGrupo + espacamento);

    algoritmos.forEach((algoritmo, j) => {
      const registro = porAlgoritmo.get(algoritmo)?.get(tamanho);
      const tempo = registro ? registro.tempo_s : null;
      const xBarra = xGrupo + j * larguraBarra;
      if (tempo == null) return;
      const h = Math.max(alturaBarra(tempo), 1);
      const yTopo = margemTopo + alturaGrafico - h;
      const rect = criarSvg("rect", {
        x: xBarra + larguraBarra * 0.08,
        y: yTopo,
        width: larguraBarra * 0.84,
        height: h,
        fill: CORES_ALGORITMO[algoritmo],
      });
      const tip = criarSvg("title", {});
      tip.textContent = `${NOMES_ALGORITMO[algoritmo]}, ${formatarNumero(tamanho)}, ${formatarTempo(tempo)}`;
      rect.appendChild(tip);
      svg.appendChild(rect);

      const valorTxt = criarSvg("text", {
        x: xBarra + larguraBarra / 2,
        y: yTopo - 6,
        "text-anchor": "middle",
        class: "barra-valor",
      });
      valorTxt.textContent = formatarTempo(tempo);
      svg.appendChild(valorTxt);
    });

    const rotulo = criarSvg("text", {
      x: xGrupo + larguraGrupo / 2,
      y: margemTopo + alturaGrafico + 20,
      "text-anchor": "middle",
    });
    rotulo.textContent = formatarNumero(tamanho);
    svg.appendChild(rotulo);
  });

  const container = document.createElement("div");
  container.className = "grafico-tamanho";
  const titulo = document.createElement("h3");
  titulo.textContent = `Comparando ${algoritmos.length} de ${ORDEM_ALGORITMOS.length} algoritmos, dataset ${tipo}`;
  container.appendChild(titulo);
  container.appendChild(renderLegenda(algoritmos));
  container.appendChild(svg);
  return container;
}

function renderGraficoFiltrado() {
  const destino = document.getElementById("grafico-filtro-comparativo");
  if (!_registrosCache) return;
  const tipo = document.getElementById("select-tipo-comparativo").value;
  const algoritmos = algoritmosSelecionados();
  destino.innerHTML = "";
  if (algoritmos.length === 0) {
    destino.innerHTML = "<p>Selecione ao menos um algoritmo.</p>";
    return;
  }
  destino.appendChild(renderGraficoBarrasAgrupadas(_registrosCache, tipo, algoritmos));
}

async function carregarComparativo() {
  const destinoLinha = document.getElementById("grafico-linha-comparativo");
  const tipo = document.getElementById("select-tipo-comparativo").value;
  destinoLinha.innerHTML = "Carregando...";
  try {
    const { registros } = await apiGet("/api/tempos");
    _registrosCache = registros;
    if (registros.length === 0) {
      destinoLinha.innerHTML = "<p>Nenhum tempo registrado ainda em resultados/tempos.md.</p>";
      document.getElementById("grafico-filtro-comparativo").innerHTML = "";
      return;
    }
    destinoLinha.innerHTML = "";
    destinoLinha.appendChild(
      renderGraficoLinha(registros, tipo, {
        titulo: `Todos os algoritmos: tempo x tamanho`,
      })
    );
    destinoLinha.appendChild(renderGraficoBarrasMaiorTamanho(registros, tipo));
    renderGraficoFiltrado();
  } catch (err) {
    destinoLinha.innerHTML = `<span class="aviso">Erro ao carregar tempos: ${err.message}</span>`;
  }
}

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
      if (btn.dataset.aba === "comparativo") carregarComparativo();
    });
  });

  document
    .getElementById("btn-atualizar-comparativo")
    .addEventListener("click", () => carregarComparativo());
  document
    .getElementById("select-tipo-comparativo")
    .addEventListener("change", () => carregarComparativo());

  configurarDropdownAlgoritmos();
}

function configurarDropdownAlgoritmos() {
  const raiz = document.getElementById("filtro-algoritmos-comparativo");
  const botao = raiz.querySelector(".dropdown-multi-btn");
  const lista = raiz.querySelector(".dropdown-multi-lista");
  const rotulo = raiz.querySelector(".dropdown-multi-rotulo");
  const checkboxes = [...raiz.querySelectorAll("input[type=checkbox]")];

  function atualizarRotulo() {
    const n = checkboxes.filter((c) => c.checked).length;
    rotulo.textContent =
      n === checkboxes.length ? `${n} algoritmos` : `${n} de ${checkboxes.length} algoritmos`;
  }

  botao.addEventListener("click", (ev) => {
    ev.stopPropagation();
    lista.hidden = !lista.hidden;
  });

  document.addEventListener("click", (ev) => {
    if (!lista.hidden && !raiz.contains(ev.target)) lista.hidden = true;
  });

  checkboxes.forEach((c) =>
    c.addEventListener("change", () => {
      atualizarRotulo();
      renderGraficoFiltrado();
    })
  );

  atualizarRotulo();
}

main().catch((err) => {
  document.getElementById("conteudo").innerHTML =
    `<p style="color:#ff8a65">Erro ao iniciar: ${err.message}</p>`;
});
