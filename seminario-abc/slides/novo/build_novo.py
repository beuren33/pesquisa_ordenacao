"""Gera abc-seminario-novo.pptx (16 slides 16:9) do seminario ABC.

Uso: python3 slides/novo/build_novo.py   (ou de qualquer pasta; caminhos relativos ao script)
Regras: fundo branco, texto preto, Arial em todos os runs e no tema.
"""
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent
VIDEO = PROJECT / "video" / "out" / "abc-ciclo.mp4"
POSTER = HERE / "poster_video.png"
OUT = HERE / "abc-seminario-novo.pptx"

FONT = "Arial"
BLACK = RGBColor(0, 0, 0)
WHITE = RGBColor(255, 255, 255)
YELLOW = RGBColor(0xFF, 0xC4, 0x00)  # só em formas; nenhum texto usa esta cor

SLIDE_W = Emu(12192000)  # 13.333 in
SLIDE_H = Emu(6858000)   # 7.5 in
MARGIN_L = Inches(0.9)
CONTENT_W = Inches(11.5)


def style(run, size, bold=False):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = False
    run.font.color.rgb = BLACK


def fill(tf, lines, size, bold=False, spacing=1.5, align=PP_ALIGN.LEFT):
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run()
        r.text = line
        style(r, size, bold)


def set_notes(slide, text):
    tf = slide.notes_slide.notes_text_frame
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = text
    r.font.name = FONT
    r.font.color.rgb = BLACK


def add_shape_rect(slide, left, top, width, height, shape=MSO_SHAPE.RECTANGLE):
    """Forma amarela sem contorno nem sombra (enfeite; não contém texto)."""
    sh = slide.shapes.add_shape(shape, left, top, width, height)
    sh.fill.solid()
    sh.fill.fore_color.rgb = YELLOW
    sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def add_title(slide, text, top=0.55, size=40):
    t = slide.shapes.title
    t.left, t.top = MARGIN_L, Inches(top)
    t.width, t.height = CONTENT_W, Inches(1.0)
    t.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    fill(t.text_frame, [text], size, bold=True, spacing=1.0)
    add_shape_rect(slide, MARGIN_L + Inches(0.1), Inches(top + 0.97), Inches(1.2), Inches(0.07))
    return t


def add_body(slide, lines, top=1.9, height=4.8, size=26, spacing=1.5, width=CONTENT_W):
    box = slide.shapes.add_textbox(MARGIN_L, Inches(top), width, Inches(height))
    fill(box.text_frame, lines, size, spacing=spacing)
    return box


FIG_DIR = HERE / "fig"
FIG_LEFT, FIG_TOP, FIG_W, FIG_H = 7.55, 1.75, 5.0, 4.8  # polegadas: caixa onde a figura é encaixada


def add_figure(slide, n):
    """Figura do slide n (se existir), encaixada à direita do parágrafo, sem distorcer."""
    path = FIG_DIR / f"fig-{n}.png"
    if not path.exists():
        return False
    from PIL import Image
    w, h = Image.open(path).size
    scale = min(FIG_W / w, FIG_H / h)
    pw, ph = w * scale, h * scale
    left = FIG_LEFT + (FIG_W - pw) / 2
    top = FIG_TOP + (FIG_H - ph) / 2
    slide.shapes.add_picture(str(path), Inches(left), Inches(top), Inches(pw), Inches(ph))
    return True


def add_number(slide, n):
    pill = add_shape_rect(slide, Inches(12.3), Inches(6.88), Inches(0.7), Inches(0.42),
                          MSO_SHAPE.ROUNDED_RECTANGLE)
    pill.adjustments[0] = 0.5
    box = slide.shapes.add_textbox(Inches(12.3), Inches(6.88), Inches(0.7), Inches(0.42))
    tf = box.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.word_wrap = False
    tf.auto_size = MSO_AUTO_SIZE.NONE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = str(n)
    style(r, 16)


# ---------------------------------------------------------------- slides

def slide_cover(prs, notes):
    s = prs.slides.add_slide(prs.slide_layouts[5])
    add_title(s, "ABC: Artificial Bee Colony", top=2.2)
    has_fig = add_figure(s, 1)
    add_body(s, ["Matheus Beuren", "Pesquisa e Ordenação, professora Glória Patricia"],
             top=3.5, height=1.8, width=Inches(6.4) if has_fig else CONTENT_W)
    set_notes(s, notes)
    add_number(s, 1)


def slide_text(prs, n, title, paragraph, notes):
    s = prs.slides.add_slide(prs.slide_layouts[5])
    add_title(s, title)
    has_fig = add_figure(s, n)
    add_body(s, [paragraph], width=Inches(6.4) if has_fig else CONTENT_W,
             size=24 if has_fig else 26)
    set_notes(s, notes)
    add_number(s, n)


def slide_video(prs, n, notes):
    s = prs.slides.add_slide(prs.slide_layouts[5])
    add_title(s, "Exemplo prático")
    vh = Inches(5.35)
    vw = Emu(int(vh * 16 / 9))
    left = Emu(int((SLIDE_W - vw) / 2))
    s.shapes.add_movie(str(VIDEO), left, Inches(1.8), vw, vh,
                       poster_frame_image=str(POSTER), mime_type="video/mp4")
    set_notes(s, notes)
    add_number(s, n)


def slide_qr(prs, n, notes):
    s = prs.slides.add_slide(prs.slide_layouts[5])
    add_title(s, "Simulador do ABC")
    size = Inches(4.4)
    left = Emu(int((SLIDE_W - size) / 2))
    box = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, Inches(1.8), size, size)
    box.fill.solid()
    box.fill.fore_color.rgb = WHITE
    box.line.color.rgb = BLACK
    box.line.width = Pt(1)
    box.shadow.inherit = False
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    fill(tf, ["QR CODE PLACEHOLDER", "URL da Vercel pendente"], 20, bold=True,
         spacing=1.0, align=PP_ALIGN.CENTER)
    tf.paragraphs[1].runs[0].font.size = Pt(16)
    tf.paragraphs[1].runs[0].font.bold = False
    set_notes(s, notes)
    add_number(s, n)


REFS = [
    "KARABOGA, D. An idea based on honey bee swarm for numerical optimization. "
    "Technical Report TR06, Erciyes University, 2005.",
    "KARABOGA, D.; BASTURK, B. A powerful and efficient algorithm for numerical function optimization: "
    "artificial bee colony (ABC) algorithm. Journal of Global Optimization, 2007.",
    "KARABOGA, D.; BASTURK, B. On the performance of artificial bee colony (ABC) algorithm. "
    "Applied Soft Computing, 2008.",
    "KARABOGA, D.; AKAY, B.; OZTURK, C. Artificial Bee Colony (ABC) Optimization Algorithm for Training "
    "Feed-Forward Neural Networks. In: Modeling Decisions for Artificial Intelligence (MDAI), 2007.",
    "KARABOGA, D. et al. A comprehensive survey: artificial bee colony (ABC) algorithm and applications. "
    "Artificial Intelligence Review, 2014.",
]


def slide_conclusion(prs, n, notes):
    s = prs.slides.add_slide(prs.slide_layouts[5])
    add_title(s, "Conclusão")
    add_body(s,
        ["O ABC mostra como um comportamento simples de abelhas vira um método de busca eficaz, "
         "com poucos parâmetros e boa exploração de soluções, útil em otimização numérica e em treino de redes neurais."])
    set_notes(s, notes)
    add_number(s, n)


def slide_refs(prs, n, notes):
    s = prs.slides.add_slide(prs.slide_layouts[5])
    add_title(s, "Referências")
    box = add_body(s, REFS, top=1.9, height=4.8, size=20, spacing=1.15, width=Inches(11.5))
    for para in box.text_frame.paragraphs:
        para.space_after = Pt(12)
    set_notes(s, notes)
    add_number(s, n)


# ---------------------------------------------------------------- textos (literais do plano) e notas

TEXT_SLIDES = [
    (2, "O problema",
     "Muitos problemas têm soluções demais para testar uma por uma. Um entregador com 20 paradas tem cerca de "
     "60 quadrilhões de rotas possíveis. Mesmo testando um bilhão por segundo, levaria quase dois anos para "
     "conferir todas, então é preciso um método que busque boas soluções sem testar tudo.",
     "Vou começar com um problema concreto. Imagine um entregador que precisa visitar 20 paradas e quer escolher a "
     "ordem com a menor distância possível. Se contarmos todas as ordens possíveis, chegamos a cerca de 60 quadrilhões "
     "de rotas. Mesmo que o computador testasse um bilhão de rotas por segundo, levaria quase dois anos só para "
     "conferir todas. Esse tipo de problema aparece em rotas de entrega, na montagem de horários e no planejamento de "
     "produção, e em todos eles a lista de opções cresce muito rápido. Por isso testar uma por uma deixa de funcionar, "
     "e a gente precisa de um método que ache boas soluções sem testar tudo. É exatamente aí que entram as metaheurísticas."),
    (3, "O que é uma metaheurística",
     "Metaheurística é uma estratégia geral para procurar boas soluções sem testar todas. Ela combina sorteio com "
     "um critério de qualidade: explora lugares novos e aproveita os que já deram certo. Não garante a melhor "
     "solução, mas costuma achar uma muito boa em pouco tempo.",
     "Uma metaheurística é uma estratégia geral, que serve para muitos problemas diferentes, e não uma receita fechada "
     "para um problema só. Ela mistura sorteio com um critério de qualidade, então explora lugares novos e, ao mesmo "
     "tempo, aproveita os que já deram bons resultados. Pense numa pessoa procurando um bom restaurante numa cidade "
     "grande: ela testa bairros diferentes, mas volta para os que já se mostraram bons. O ponto central é que essa "
     "estratégia não garante a melhor solução. Em compensação, costuma achar uma solução muito boa em pouco tempo, "
     "e na prática é isso que interessa."),
    (4, "Como o ABC foi criado",
     "O ABC foi proposto por Dervis Karaboga, da Universidade Erciyes, na Turquia, em 2005. Ele se inspira em como "
     "as abelhas de uma colmeia procuram néctar: algumas ficam nas flores conhecidas, outras escolhem onde ir, e "
     "outras exploram lugares novos.",
     "O ABC foi proposto por Dervis Karaboga e, segundo o relatório técnico TR06, a confirmar no PDF original, o "
     "trabalho veio da Universidade Erciyes, na Turquia, em 2005. A inspiração vem de abelhas reais, que saem da "
     "colmeia para buscar néctar. Algumas ficam nas flores que já conhecem, outras escolhem para onde ir e outras "
     "exploram lugares novos. Karaboga pegou esse comportamento e o transformou em um algoritmo de busca numérica. "
     "Nos próximos slides eu mostro como cada um desses papéis aparece no algoritmo, sempre com o mesmo exemplo. "
     "Vale lembrar que o ABC é uma proposta relativamente recente, da década de 2000, quando comparada a métodos clássicos de otimização."),
    (5, "Objetivos do ABC",
     "O objetivo do ABC é encontrar o valor que minimiza ou maximiza uma função, como o menor erro ou o menor custo. "
     "Ele busca isso de forma simples: poucos parâmetros, sem precisar de derivadas, e equilibrando a busca local com "
     "a exploração de regiões novas.",
     "O objetivo do ABC é achar o valor que minimiza ou maximiza uma função. Pense em ajustar um modelo para que o erro "
     "dele seja o menor possível, ou em escolher uma configuração em que o custo fique o mais baixo. A ideia é fazer "
     "isso de forma simples, com poucos parâmetros para ajustar. Segundo o artigo de 2007, a confirmar, o método também "
     "dispensa derivadas, que nem sempre existem ou são fáceis de calcular. Além disso, ele equilibra a busca local, que "
     "refina o que já tem, com a exploração de regiões novas. "
     "Em termos práticos, a pessoa pode aplicar o método a uma função nova sem precisar calcular a inclinação dela em cada ponto."),
    (6, "Flor, néctar e as três abelhas",
     "No ABC, cada flor é uma solução possível e o néctar é a qualidade dessa solução. Três tipos de abelha trabalham "
     "juntos: as empregadas refinam uma flor, as observadoras escolhem flores boas para visitar e as exploradoras "
     "procuram flores novas.",
     "Agora o vocabulário, que é a chave para entender o resto. Cada flor é uma solução possível, e o néctar é a "
     "qualidade dessa solução: quanto mais néctar, melhor a flor. No nosso problema, a qualidade é melhor quanto menor "
     "for o valor de x ao quadrado, então a flor boa é a que fica mais perto de zero. Temos três tipos de abelha "
     "trabalhando juntas. As empregadas ficam numa flor e a refinam, as observadoras escolhem flores boas para visitar, "
     "e as exploradoras procuram flores novas quando alguma flor já não rende mais. Nos próximos slides eu uso o mesmo "
     "exemplo, com as flores A, B e C, para cada papel ficar concreto."),
    (7, "Empregada",
     "A empregada fica na sua flor e testa um ponto novo perto dela, usando uma flor vizinha para definir a direção "
     "do passo. Se o ponto novo tiver mais néctar, ela se muda para lá. Senão, fica onde está e soma uma falha.",
     "Aqui está a empregada. Ela fica na sua flor, testa um ponto novo perto dela e usa uma flor vizinha só para "
     "decidir a direção do passo. Lembrem que a comparação é sempre com a própria flor, nunca com a vizinha. No exemplo, "
     "a flor A está em 7, e a empregada testa o ponto 1,0. Como o valor de x ao quadrado cai de 49 para 1, o ponto novo "
     "tem mais néctar, então a abelha se muda para lá. Na mesma rodada, a flor B tentou o ponto menos 7,8, que é pior que "
     "menos 5, então ela ficou onde estava e ganhou uma falha. Papel da empregada: refinar o que já tem."),
    (8, "Observadora",
     "As observadoras esperam na colmeia e escolhem flores por sorteio, em que quanto mais néctar, maior a chance. "
     "Depois repetem a mesma visita da empregada. Assim, a busca se concentra onde as soluções são melhores, sem "
     "abandonar de vez as piores.",
     "Agora entram as observadoras. Elas esperam na colmeia e escolhem flores por sorteio, numa roleta em que quanto "
     "mais néctar, maior a fatia. Pense numa roleta de feira, em que cada prêmio tem um pedaço proporcional ao que vale. "
     "No exemplo, as chances ficam em torno de 33% para A, 3% para B e 65% para C, então a flor C tem a maior chance. "
     "Cada observadora faz a mesma visita da empregada, e assim a busca se concentra onde as soluções são melhores. "
     "Mesmo assim, a flor B ainda tem alguma chance de ser sorteada, porque as piores não são descartadas de vez. "
     "Papel da observadora: reforçar o que já está bom."),
    (9, "Exploradora e o limite",
     "Quando uma flor acumula falhas além do limite, ela é abandonada e a exploradora sorteia um lugar novo, mesmo que "
     "seja pior. O limite regula a busca: baixo, a colônia troca de flor cedo; alto, insiste nas flores que já tem.",
     "Agora a exploradora, que é a parte que evita ficar preso. Quando uma flor acumula falhas além do limite, ela é "
     "abandonada e a exploradora sorteia um lugar novo, aceito mesmo que seja pior. Pense num garçom que insiste num prato "
     "que ninguém pede: depois de certo número de recusas, ele troca o cardápio. No exemplo do ciclo, o limite é 3 e "
     "nenhuma flor chegou lá, então a exploradora não aparece nesse ciclo. O limite é o botão entre explorar e explotar: "
     "baixo, a colônia troca de flor cedo; alto, insiste mais tempo nas flores que já tem. Esse mesmo controle aparece no "
     "simulador, que eu mostro daqui a pouco."),
    (10, "Ciclo completo",
     "Um ciclo do ABC tem quatro passos: as empregadas visitam suas flores, as observadoras escolhem flores boas e "
     "visitam, o melhor ponto encontrado é guardado e a exploradora troca flores abandonadas. O ciclo se repete até "
     "o número de ciclos definido.",
     "Agora juntamos tudo em um ciclo completo, com quatro passos. Primeiro, as empregadas visitam suas flores, uma de "
     "cada vez. Depois, as observadoras escolhem flores boas por sorteio e fazem as visitas. Em seguida, o melhor ponto "
     "encontrado no ciclo é guardado, para a colônia não perder o que já achou. Por fim, a exploradora troca as flores "
     "que passaram do limite. O ciclo se repete até atingir o número de ciclos definido, e a tendência é que a colônia "
     "fique cada vez mais perto do mínimo. No exemplo com as flores A, B e C, o melhor do primeiro ciclo foi a flor C, "
     "em menos 0,1, e isso é o que eu quero que vocês acompanhem no vídeo."),
    (13, "Problemas que o ABC resolve",
     "O ABC resolve problemas de otimização numérica, como achar o mínimo de funções com muitos vales, e foi comparado "
     "a outros algoritmos em testes. Também pode treinar redes neurais, ajustando os pesos da rede como se cada "
     "conjunto fosse uma flor.",
     "O ABC resolve problemas de otimização numérica, como encontrar o mínimo de funções com muitos vales, onde é fácil "
     "ficar preso num vale que não é o mais baixo. Segundo o artigo de Karaboga e Basturk, de 2007, a confirmar no PDF, "
     "o ABC foi comparado com GA, PSO e PS-EA na Tabela 1, e eu não vou citar nenhum número aqui. Também dá para usar o "
     "ABC para treinar redes neurais, em que cada flor guarda um conjunto de pesos e o néctar é o erro baixo. Pense numa "
     "rede que reconhece letras: ajustar os pesos dela é um problema de otimização, e o ABC pode ser o otimizador que "
     "procura essa combinação. Esse uso aparece no trabalho de 2007 sobre redes neurais, a confirmar."),
    (14, "Áreas e principal uso",
     "O principal uso do ABC é a otimização numérica: encontrar valores que minimizam um erro ou um custo. A revisão "
     "de Karaboga e colaboradores (2014) reúne aplicações em áreas como engenharia, redes neurais, processamento de "
     "imagens e agendamento.",
     "O principal uso do ABC é a otimização numérica, ou seja, encontrar valores que minimizam um erro ou um custo. "
     "Segundo a revisão de Karaboga e colaboradores, de 2014, a confirmar, o método aparece em áreas como engenharia, "
     "redes neurais, processamento de imagens e agendamento. Pense em agendamento como organizar turnos de funcionários, "
     "em que o custo é o número de conflitos entre horários. Eu ainda vou checar essa lista no survey antes da "
     "apresentação, e as áreas que não forem confirmadas saem do slide. Não cito quantidades de artigos, porque esse "
     "dado ainda não foi conferido. "
     "Quando eu falo de áreas, quero dizer tipos de problema que aparecem no dia a dia, como ajustar parâmetros de um sistema para gastar menos."),
    (15, "Vantagens e limitações",
     "O ABC é simples de implementar, tem poucos parâmetros de controle e combina busca local com busca global. Em "
     "contrapartida, seu desempenho depende do limite e do número de flores, e a convergência perto do ótimo pode ser "
     "lenta.",
     "Aqui eu resumo vantagens e limitações. Segundo o survey de 2014 e o artigo de 2008, ambos a confirmar, o ABC é "
     "simples de implementar, tem poucos parâmetros de controle e combina busca local com busca global. Em contrapartida, "
     "o desempenho depende do limite e do número de flores, e a convergência perto do ótimo pode ser lenta. Pense numa "
     "chave perdida dentro de casa: procurar por perto é rápido, mas achar o último canto pode demorar. Como essas "
     "afirmações ainda estão marcadas para confirmar, eu não as apresento como fato definitivo. "
     "Na prática, a lição é que o ABC é uma boa opção para começar, mas não a única, e que a escolha depende do problema."),
]

NOTES_COVER = (
    "Oi, pessoal, eu sou o Matheus Beuren, e hoje vou apresentar o ABC, sigla de Artificial Bee Colony, ou colônia "
    "artificial de abelhas. O seminário é para a disciplina de Pesquisa e Ordenação, com a professora Glória Patricia. "
    "Vou começar pelo problema que motiva métodos como esse e depois explicar como o algoritmo funciona, passo a passo. "
    "Na sequência, mostro um exemplo em vídeo e um simulador ao vivo, e no fim eu deixo as referências. "
    "A apresentação tem cerca de quinze minutos de fala, então vou manter um ritmo tranquilo e deixar tempo para perguntas."
)

NOTES_VIDEO = (
    "Este é o exemplo prático, em vídeo. O vídeo minimiza x ao quadrado no intervalo entre menos 10 e 10, com as três "
    "flores A, B e C, que começam em 7, menos 5 e 2. Eu deixo o vídeo rodar e, enquanto ele roda, aponto as empregadas "
    "fazendo suas visitas, a roleta com as fatias de chance e as observadoras escolhendo flores. A exploradora só aparece "
    "numa cena marcada como e se, em que a flor B murcha e uma nova posição é sorteada, mesmo sendo pior. Essa cena é "
    "só uma ilustração, e não o que aconteceu no exemplo real. O vídeo tem cerca de um minuto e meio, então eu aproveito "
    "esse tempo para acompanhar o ciclo com vocês."
)

NOTES_QR = (
    "Agora o exemplo ao vivo. Pelo QR code, vocês podem abrir o simulador no próprio celular e mexer nos controles, como "
    "o limite e o número de flores. Este quadrado ainda é só um marcador, porque o endereço do site ainda não existe, então "
    "eu vou trocar por um QR code real antes da apresentação. Enquanto vocês testam, observem como o número de flores muda "
    "a rapidez com que a colônia chega ao mínimo. Depois eu volto para as últimas partes do deck."
)

NOTES_CONCL = (
    "Para fechar, o ABC mostra como um comportamento simples de abelhas vira um método de busca eficaz, com poucos "
    "parâmetros e boa exploração de soluções. Ele é útil em otimização numérica e em treino de redes neurais. A ideia "
    "central é a divisão de papéis: as empregadas refinam, as observadoras reforçam o que é bom e as exploradoras "
    "renovam a busca. Obrigado, e fico à disposição para perguntas. Se surgir alguma dúvida sobre o que foi mostrado, "
    "eu posso voltar ao exemplo das flores A, B e C e refazer o ciclo passo a passo."
)

NOTES_REFS = (
    "Estas são as referências do seminário: o relatório técnico de 2005, em que Karaboga propôs o algoritmo, os dois "
    "artigos de Karaboga e Basturk, de 2007 e 2008, o trabalho de 2007 sobre treino de redes neurais e a revisão de "
    "2014 com as aplicações. Os títulos e os periódicos foram conferidos na web, mas volumes e páginas ficaram de fora "
    "e ainda precisam ser completados antes da entrega final. Se alguém quiser aprofundar, o relatório de 2005 e o "
    "artigo de 2007 são os melhores pontos de partida."
)


def main():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    slide_cover(prs, NOTES_COVER)
    by_n = {n: (t, p, nt) for n, t, p, nt in TEXT_SLIDES}
    for n in range(2, 11):
        t, p, nt = by_n[n]
        slide_text(prs, n, t, p, nt)
    slide_video(prs, 11, NOTES_VIDEO)
    slide_qr(prs, 12, NOTES_QR)
    for n in (13, 14, 15):
        t, p, nt = by_n[n]
        slide_text(prs, n, t, p, nt)
    slide_conclusion(prs, 16, NOTES_CONCL)
    slide_refs(prs, 17, NOTES_REFS)

    # Tema com Arial em todas as partes de tema do pacote.
    for part in prs.part.package.iter_parts():
        if str(part.partname).startswith("/ppt/theme/"):
            root = etree.fromstring(part.blob)
            for el in root.iter(qn("a:latin")):
                el.set("typeface", FONT)
            part._blob = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)

    prs.save(OUT)
    print(f"OK: {len(prs.slides)} slides -> {OUT}")


if __name__ == "__main__":
    main()
