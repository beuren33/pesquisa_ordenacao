class No:
    def __init__(self, item, esq=None, dir=None):
        self.item = item
        self.esq = esq
        self.dir = dir


def remover_folhas(ab, x):
    """Remove recursivamente todas as folhas com item igual a x.
    Retorna a raiz da árvore resultante."""
    if ab is None:
        return None
    if ab.esq is None and ab.dir is None:
        return None if ab.item == x else ab
    ab.esq = remover_folhas(ab.esq, x)
    ab.dir = remover_folhas(ab.dir, x)
    return ab


def contar_nos(ab):
    if ab is None:
        return 0
    pilha = [ab]
    total = 0
    while pilha:
        no = pilha.pop()
        total += 1
        if no.esq:
            pilha.append(no.esq)
        if no.dir:
            pilha.append(no.dir)
    return total


def _folha(no):
    return no.esq is None and no.dir is None


def folhas_in_order(ab):
    if ab is None:
        return 0
    total = folhas_in_order(ab.esq)
    if _folha(ab):
        total += 1
    return total + folhas_in_order(ab.dir)


def folhas_pre_order(ab):
    if ab is None:
        return 0
    total = 1 if _folha(ab) else 0
    total += folhas_pre_order(ab.esq)
    return total + folhas_pre_order(ab.dir)


def folhas_pos_order(ab):
    if ab is None:
        return 0
    total = folhas_pos_order(ab.esq) + folhas_pos_order(ab.dir)
    if _folha(ab):
        total += 1
    return total


def em_ordem(ab):
    return em_ordem(ab.esq) + [ab.item] + em_ordem(ab.dir) if ab else []


if __name__ == "__main__":

    def monta():
        return No(5, No(3, No(1), No(3)), No(7, None, No(7)))

    a = monta()
    print("nós:", contar_nos(a))
    print("folhas in/pre/pos:", folhas_in_order(a), folhas_pre_order(a), folhas_pos_order(a))

    a = remover_folhas(a, 3)
    print("apos remover folhas 3:", em_ordem(a))
    a = remover_folhas(a, 7)
    print("após remover folhas 7:", em_ordem(a))
    print("nos:", contar_nos(a), "  arvore vazia:", contar_nos(None))
