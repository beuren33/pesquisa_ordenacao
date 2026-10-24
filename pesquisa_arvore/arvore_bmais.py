class No:
    def __init__(self, folha):
        self.folha = folha
        self.chaves = []
        self.filhos = []


class BMais:
    """Ordem m: no máximo m filhos e m-1 chaves por nó."""

    def __init__(self, ordem):
        self.ordem = ordem
        self.raiz = No(True)

    def inserir(self, chave):
        res = self._inserir(self.raiz, chave)
        if res:
            nova = No(False)
            nova.chaves = [res[0]]
            nova.filhos = [self.raiz, res[1]]
            self.raiz = nova

    def _inserir(self, no, chave):
        if no.folha:
            if chave in no.chaves:
                return None
            no.chaves.append(chave)
            no.chaves.sort()
            if len(no.chaves) < self.ordem:
                return None
            meio = (len(no.chaves) + 1) // 2
            dir_ = No(True)
            dir_.chaves = no.chaves[meio:]
            no.chaves = no.chaves[:meio]
            return dir_.chaves[0], dir_  # copia a chave para o pai

        i = 0
        while i < len(no.chaves) and chave >= no.chaves[i]:
            i += 1
        res = self._inserir(no.filhos[i], chave)
        if not res:
            return None
        no.chaves.insert(i, res[0])
        no.filhos.insert(i + 1, res[1])
        if len(no.chaves) < self.ordem:
            return None
        mid = len(no.chaves) // 2
        sobe = no.chaves[mid]  # chave do meio sobe
        dir_ = No(False)
        dir_.chaves = no.chaves[mid + 1:]
        dir_.filhos = no.filhos[mid + 1:]
        no.chaves = no.chaves[:mid]
        no.filhos = no.filhos[:mid + 1]
        return sobe, dir_

    def mostrar(self):
        nivel = [self.raiz]
        while nivel:
            print("  ".join(str(n.chaves) for n in nivel))
            nivel = [f for n in nivel for f in n.filhos]


if __name__ == "__main__":
    meses = ["janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho",
             "agosto", "setembro", "outubro", "novembro", "dezembro"]
    arv = BMais(4)
    for m in meses:
        arv.inserir(m)
        print(f"\nInserir {m}")
        arv.mostrar()

    valores = [34, 2, 1, 4, 7, 5, 102, 23, 45, 67, 43, 112, 32, 765, 234, 12,
               14, 15, 23, 25, 33, 46, 35, 18, 26]
    arv = BMais(6)
    for v in valores:
        arv.inserir(v)
    print("\nÁrvore B+ de ordem 6 final")
    arv.mostrar()
