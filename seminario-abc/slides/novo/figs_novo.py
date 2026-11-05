#!/usr/bin/env python3
"""Figuras dos slides novos (fundo transparente; só preto, branco e amarelo).

Gera slides/novo/fig/fig-<n>.png, onde n é o número do slide. Rodar antes de build_novo.py.
Poucos rótulos (só letras A, B, C e nomes curtos): o texto de cada slide continua sendo o parágrafo.
"""
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Wedge  # noqa: E402

OUT = Path(__file__).resolve().parent / "fig"
INK = "#0A0A0A"
YEL = "#FFC400"
GREY = "#D9D9D9"
plt.rcParams["font.family"] = ["Arial", "Liberation Sans", "DejaVu Sans"]

W, H = 5.4, 4.6


def canvas():
    fig, ax = plt.subplots(figsize=(W, H))
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    return fig, ax


def save(fig, n):
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / f"fig-{n}.png", dpi=220, transparent=True, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def flower(ax, x, y, s=1.0, petal=YEL, core=INK, stem=True, z=5):
    if stem:
        ax.plot([x, x], [y - 0.55 * s, y - 0.12 * s], color=INK, lw=2.4 * s, solid_capstyle="round", zorder=z)
    for k in range(6):
        a = k * math.pi / 3
        ax.add_patch(Circle((x + 0.17 * s * math.cos(a), y + 0.17 * s * math.sin(a)), 0.13 * s,
                            fc=petal, ec=INK, lw=1.3, zorder=z + 1))
    ax.add_patch(Circle((x, y), 0.11 * s, fc=core, ec=INK, lw=1.2, zorder=z + 2))


def hill(ax, x0=0.4, x1=5.0, base=0.7, top=3.2):
    xs = np.linspace(-1, 1, 200)
    ys = base + (top - base) * (1 - xs ** 2)
    X = x0 + (xs + 1) / 2 * (x1 - x0)
    ax.fill_between(X, base - 0.3, ys, color=GREY, zorder=1)
    ax.plot(X, ys, color=INK, lw=2.8, zorder=2)
    return lambda u: (x0 + (u + 1) / 2 * (x1 - x0), base + (top - base) * (1 - u * u))


def arrow(ax, p, q, rad=0.3, dashed=False, color=INK):
    ax.add_patch(FancyArrowPatch(p, q, connectionstyle=f"arc3,rad={rad}", arrowstyle="-|>", mutation_scale=18,
                                 lw=2.2, color=color, linestyle=(0, (3, 3)) if dashed else "-", zorder=8))


def label(ax, x, y, t, size=20, color=INK):
    ax.text(x, y, t, fontsize=size, fontweight="bold", ha="center", va="center", color=color, zorder=12)


def hexagon(ax, cx, cy, r, fc):
    pts = [(cx + r * math.cos(math.pi / 6 + k * math.pi / 3), cy + r * math.sin(math.pi / 6 + k * math.pi / 3))
           for k in range(6)]
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec=INK, lw=2.4, zorder=3))


def honeycomb(ax, cx, cy, r, rings=2, yellow_ratio=0.65):
    rng = np.random.default_rng(3)
    dx = math.sqrt(3) * r
    for q in range(-rings, rings + 1):
        for p in range(-rings, rings + 1):
            if abs(q + p) > rings:
                continue
            x = cx + dx * (q + p / 2)
            y = cy + 1.5 * r * p
            hexagon(ax, x, y, r, YEL if rng.random() < yellow_ratio else "white")


def fig1():  # capa: favo de mel
    fig, ax = canvas()
    honeycomb(ax, 2.7, 2.3, 0.5, rings=2)
    save(fig, 1)


def fig2():  # problema: rota entre paradas
    fig, ax = canvas()
    rng = np.random.default_rng(11)
    pts = rng.uniform([0.5, 0.5], [W - 0.5, H - 0.5], size=(12, 2))
    order = [0]
    left = set(range(1, 12))
    while left:
        j = min(left, key=lambda k: np.hypot(*(pts[k] - pts[order[-1]])))
        order.append(j)
        left.remove(j)
    # linhas finas de rotas alternativas
    for _ in range(14):
        perm = rng.permutation(12)
        ax.plot(pts[perm, 0], pts[perm, 1], color="#BDBDBD", lw=0.8, zorder=1)
    r = pts[order + [order[0]]]
    ax.plot(r[:, 0], r[:, 1], color=INK, lw=3.0, zorder=3)
    ax.scatter(pts[:, 0], pts[:, 1], s=210, c="white", edgecolors=INK, linewidths=2.2, zorder=5)
    ax.scatter(*pts[0], s=330, c=YEL, edgecolors=INK, linewidths=2.4, zorder=6)
    save(fig, 2)


def fig3():  # metaheurística: terreno com picos, pontos sorteados e foco nos melhores
    fig, ax = canvas()
    xs = np.linspace(0.3, 5.1, 400)
    f = lambda x: 1.6 + 0.85 * np.sin(1.7 * x) + 0.55 * np.sin(4.1 * x + 1) + 0.9 * np.exp(-((x - 3.6) ** 2) / 0.35)
    ax.fill_between(xs, 0.4, f(xs), color=GREY, zorder=1)
    ax.plot(xs, f(xs), color=INK, lw=2.8, zorder=2)
    for x in (0.7, 1.3, 2.1, 2.8, 4.5, 4.9):
        ax.scatter(x, f(x), s=150, c="white", edgecolors=INK, linewidths=2, zorder=5)
    for x in (3.45, 3.6, 3.75):
        ax.scatter(x, f(x), s=190, c=YEL, edgecolors=INK, linewidths=2.2, zorder=6)
    save(fig, 3)


def fig4():  # criação: favo + abelha estilizada
    fig, ax = canvas()
    honeycomb(ax, 2.6, 2.1, 0.5, rings=2, yellow_ratio=0.5)
    # abelha simples sobre o favo
    bx, by = 3.9, 3.6
    ax.add_patch(Circle((bx - 0.2, by + 0.28), 0.3, fc="white", ec=INK, lw=2, zorder=10))
    ax.add_patch(Circle((bx + 0.15, by + 0.34), 0.26, fc="white", ec=INK, lw=2, zorder=10))
    ax.add_patch(matplotlib.patches.Ellipse((bx, by), 0.95, 0.6, fc=YEL, ec=INK, lw=2.4, zorder=11))
    for dx in (-0.12, 0.08):
        ax.plot([bx + dx, bx + dx], [by - 0.27, by + 0.27], color=INK, lw=4.5, zorder=12, solid_capstyle="butt")
    ax.add_patch(Circle((bx + 0.5, by), 0.2, fc=INK, ec=INK, zorder=12))
    save(fig, 4)


def fig5():  # objetivos: curva com o mínimo
    fig, ax = canvas()
    xs = np.linspace(-1, 1, 200)
    X = 0.5 + (xs + 1) / 2 * 4.4
    Y = 0.9 + 3.1 * xs ** 2
    ax.plot(X, Y, color=INK, lw=3.2, zorder=3)
    ax.plot([0.4, 5.1], [0.9, 0.9], color=INK, lw=1.4, zorder=1)
    ax.scatter(2.7, 0.9, s=420, c=YEL, edgecolors=INK, linewidths=2.6, zorder=6)
    ax.scatter([1.0, 4.3], [0.9 + 3.1 * ((1.0 - 2.7) / 2.2) ** 2, 0.9 + 3.1 * ((4.3 - 2.7) / 2.2) ** 2], s=170,
               c="white", edgecolors=INK, linewidths=2, zorder=5)
    save(fig, 5)


def three_flowers(ax, role_colors=None):
    pos = hill(ax)
    for name, u, col in (("A", 0.7, YEL), ("B", -0.55, YEL), ("C", 0.1, YEL)):
        x, y = pos(u)
        flower(ax, x, y + 0.45, 1.25, petal=col)
        label(ax, x, y - 0.5, name, 20)
    return pos


def fig6():  # vocabulário: colina com três flores
    fig, ax = canvas()
    three_flowers(ax)
    save(fig, 6)


def fig7():  # empregada: flor A se muda para ponto melhor, vizinha B ao lado
    fig, ax = canvas()
    pos = hill(ax)
    xa, ya = pos(0.75)
    xb, yb = pos(-0.5)
    xn, yn = pos(0.35)
    flower(ax, xb, yb + 0.45, 1.2)
    label(ax, xb, yb - 0.5, "B", 20)
    flower(ax, xa, ya + 0.45, 1.2, petal="white")
    label(ax, xa, ya - 0.5, "A", 20)
    ax.scatter(xn, yn + 0.1, s=260, c="white", edgecolors=INK, linewidths=2.2, linestyle="--", zorder=6)
    flower(ax, xn, yn + 0.45, 1.2, petal=YEL, stem=False, z=7)
    arrow(ax, (xa - 0.25, ya + 0.75), (xn + 0.2, yn + 0.75), rad=0.35)
    save(fig, 7)


def fig8():  # observadora: roleta com fatias desiguais (C grande, A média, B fininha)
    fig, ax = canvas()
    cx, cy, r = 2.7, 2.3, 1.85
    parts = (("C", 64, YEL), ("A", 33, "white"), ("B", 3, INK))
    ang = 90
    for name, pct, col in parts:
        ax.add_patch(Wedge((cx, cy), r, ang - pct * 3.6, ang, fc=col, ec=INK, lw=2.6, zorder=3))
        mid = math.radians(ang - pct * 3.6 / 2)
        if pct > 10:
            label(ax, cx + 0.62 * r * math.cos(mid), cy + 0.62 * r * math.sin(mid), name, 26)
        ang -= pct * 3.6
    ax.add_patch(Circle((cx, cy), 0.26, fc="white", ec=INK, lw=2.4, zorder=6))
    ax.add_patch(Polygon([(cx - 0.17, cy + r + 0.42), (cx + 0.17, cy + r + 0.42), (cx, cy + r - 0.02)],
                         fc=INK, ec=INK, zorder=7))
    label(ax, cx - 0.55, cy + r + 0.3, "B", 22)
    save(fig, 8)


def fig9():  # exploradora e limite: flor murcha vira ponto novo, mesmo pior
    fig, ax = canvas()
    pos = hill(ax)
    xb, yb = pos(-0.6)
    xn, yn = pos(0.55)
    # flor abandonada: pétalas brancas caídas e pontilhado
    ax.plot([xb, xb], [yb - 0.1, yb + 0.35], color=INK, lw=2.4, zorder=5)
    for k in range(6):
        a = k * math.pi / 3
        ax.add_patch(Circle((xb + 0.12 * math.cos(a), yb + 0.35 + 0.12 * math.sin(a)), 0.1, fc="white", ec=INK,
                            lw=1.2, linestyle=(0, (2, 2)), zorder=6))
    ax.plot([xb - 0.35, xb + 0.35], [yb + 0.55, yb + 0.55], color=INK, lw=0, zorder=6)
    ax.plot([xb - 0.3, xb + 0.3], [yb + 0.8, yb + 0.1], color=INK, lw=3, zorder=9)
    ax.plot([xb - 0.3, xb + 0.3], [yb + 0.1, yb + 0.8], color=INK, lw=3, zorder=9)
    flower(ax, xn, yn + 0.45, 1.25, petal=YEL, stem=True)
    arrow(ax, (xb + 0.4, yb + 1.1), (xn - 0.25, yn + 1.25), rad=-0.5, dashed=True)
    # contador de falhas: barras cheias até o limite
    for k in range(5):
        ax.add_patch(matplotlib.patches.Rectangle((0.55 + 0.34 * k, 3.95), 0.26, 0.38, fc=INK if k < 4 else "white",
                                                  ec=INK, lw=2, zorder=5))
    save(fig, 9)


def fig10():  # ciclo: quatro passos em círculo
    fig, ax = canvas()
    cx, cy, R = 2.7, 2.3, 1.5
    names = ["Empregadas", "Observadoras", "Melhor", "Exploradora"]
    for k, nm in enumerate(names):
        a = math.pi / 2 - k * math.pi / 2
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        ax.add_patch(matplotlib.patches.FancyBboxPatch((x - 1.05, y - 0.27), 2.1, 0.54,
                                                       boxstyle="round,pad=0.02,rounding_size=0.25",
                                                       fc=YEL if k == 0 else "white", ec=INK, lw=2.4, zorder=5))
        label(ax, x, y, nm, 13)
        a2 = a - math.pi / 2
        p = (cx + R * math.cos(a - 0.5 * math.pi / 2 + 0.07), cy + R * math.sin(a - 0.5 * math.pi / 2 + 0.07))
        ax.add_patch(FancyArrowPatch((cx + 1.05 * R * math.cos(a - 0.32), cy + 1.05 * R * math.sin(a - 0.32)),
                                     (cx + 1.05 * R * math.cos(a - math.pi / 2 + 0.32),
                                      cy + 1.05 * R * math.sin(a - math.pi / 2 + 0.32)),
                                     connectionstyle="arc3,rad=-0.25", arrowstyle="-|>", mutation_scale=20, lw=2.4,
                                     color=INK, zorder=3))
    ax.set_xlim(-0.2, W + 0.2)
    save(fig, 10)


def fig13():  # problemas: terreno 2D com muitos vales (curvas de nível) e o mínimo
    fig, ax = plt.subplots(figsize=(W, H))
    g = np.linspace(-5, 5, 300)
    X, Y = np.meshgrid(g, g)
    Z = 20 + X ** 2 - 10 * np.cos(2 * np.pi * X) + Y ** 2 - 10 * np.cos(2 * np.pi * Y)
    ax.contourf(X, Y, Z, levels=8, cmap=matplotlib.colors.LinearSegmentedColormap.from_list("bw", ["#FFFFFF", "#8C8C8C"]))
    ax.contour(X, Y, Z, levels=8, colors=INK, linewidths=0.9)
    ax.scatter(0, 0, s=520, c=YEL, edgecolors=INK, linewidths=2.8, zorder=6)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_alpha(0)
    save(fig, 13)


def main():
    for f in (fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10, fig13):
        f()
    print("OK:", sorted(p.name for p in OUT.glob("fig-*.png")))


if __name__ == "__main__":
    main()
