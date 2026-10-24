# Árvores Rubro-Negras: Inserir e Remover

Árvore binária de busca auto-balanceada. Cada nó tem cor (vermelho ou preto).

## Propriedades
1. Todo nó é vermelho ou preto.
2. A raiz é preta.
3. Toda folha (NIL) é preta.
4. Nó vermelho tem filhos pretos (sem dois vermelhos seguidos).
5. Todo caminho de um nó até suas folhas NIL tem o mesmo número de nós pretos (altura negra).

Consequência: altura <= 2·log2(n+1), então busca, inserção e remoção são O(log n).

## Inserir
1. Insere como em uma ABB comum e pinta o novo nó de **vermelho**.
2. Corrige violações subindo pela árvore. Seja `z` o nó, `p` o pai, `a` o avô, `t` o tio:
   - **Pai preto** (ou z é raiz): nada a fazer (raiz pinta de preto).
   - **Caso 1, tio vermelho**: recolore pai e tio de preto, avô de vermelho; repete com `z = a`.
   - **Caso 2, tio preto, z "dobrado"** (z filho direito de p esquerdo, ou o espelho): rotação em `p` para cair no caso 3.
   - **Caso 3, tio preto, z "reto"** (esquerda-esquerda ou direita-direita): rotação em `a` no sentido oposto, troca as cores de `p` e `a`.
3. Pinta a raiz de preto no final.

No máximo 2 rotações; recolorações podem subir até a raiz (O(log n)).

## Remover
1. Remove como em ABB:
   - 0 ou 1 filho: o nó é substituído pelo filho.
   - 2 filhos: copia o sucessor (menor da subárvore direita) e remove o sucessor.
2. Seja `y` o nó fisicamente removido e `x` o filho que o substitui.
   - Se `y` era **vermelho**: nada a corrigir.
   - Se `y` era **preto**: `x` fica com "preto duplo" (falta um preto no caminho). Corrige:
     - **x vermelho**: pinta de preto, fim.
     - **Caso 1, irmão `w` vermelho**: recolore `w` de preto e pai de vermelho, rotação no pai; cai nos casos 2-4.
     - **Caso 2, `w` preto, ambos sobrinhos pretos**: pinta `w` de vermelho, sobe o preto extra para o pai (`x = pai`).
     - **Caso 3, `w` preto, sobrinho distante preto e próximo vermelho**: recolore, rotação em `w`; cai no caso 4.
     - **Caso 4, `w` preto, sobrinho distante vermelho**: `w` recebe a cor do pai, pai e sobrinho distante ficam pretos, rotação no pai; fim.
3. Raiz sempre preta no final.

No máximo 3 rotações na remoção; recolorações O(log n).

## Referência
Cormen et al., *Algoritmos: Teoria e Prática*, cap. Árvores Rubro-Negras.
