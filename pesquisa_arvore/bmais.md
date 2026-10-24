Ordem m = máximo de m filhos e m-1 chaves por nó. Divisão de folha copia a primeira chave da direita para o pai; nó interno sobe a chave do meio. Valor repetido (23) ignorado.

## Exercício 1: B+ de ordem 4, meses do ano

### 1. Inserir janeiro

```
nível 0: ['janeiro']
```

### 2. Inserir fevereiro

```
nível 0: ['fevereiro', 'janeiro']
```

### 3. Inserir marco

```
nível 0: ['fevereiro', 'janeiro', 'marco']
```

### 4. Inserir abril

Divisão: folha dividida em ['abril', 'fevereiro'] | ['janeiro', 'marco'], janeiro copiada para o pai.
Divisão: raiz dividida, nova raiz [janeiro].

```
nível 0: ['janeiro']
nível 1: ['abril', 'fevereiro'] ['janeiro', 'marco']
```

### 5. Inserir maio

```
nível 0: ['janeiro']
nível 1: ['abril', 'fevereiro'] ['janeiro', 'maio', 'marco']
```

### 6. Inserir junho

Divisão: folha dividida em ['janeiro', 'junho'] | ['maio', 'marco'], maio copiada para o pai.

```
nível 0: ['janeiro', 'maio']
nível 1: ['abril', 'fevereiro'] ['janeiro', 'junho'] ['maio', 'marco']
```

### 7. Inserir julho

```
nível 0: ['janeiro', 'maio']
nível 1: ['abril', 'fevereiro'] ['janeiro', 'julho', 'junho'] ['maio', 'marco']
```

### 8. Inserir agosto

```
nível 0: ['janeiro', 'maio']
nível 1: ['abril', 'agosto', 'fevereiro'] ['janeiro', 'julho', 'junho'] ['maio', 'marco']
```

### 9. Inserir setembro

```
nível 0: ['janeiro', 'maio']
nível 1: ['abril', 'agosto', 'fevereiro'] ['janeiro', 'julho', 'junho'] ['maio', 'marco', 'setembro']
```

### 10. Inserir outubro

Divisão: folha dividida em ['maio', 'marco'] | ['outubro', 'setembro'], outubro copiada para o pai.

```
nível 0: ['janeiro', 'maio', 'outubro']
nível 1: ['abril', 'agosto', 'fevereiro'] ['janeiro', 'julho', 'junho'] ['maio', 'marco'] ['outubro', 'setembro']
```

### 11. Inserir novembro

```
nível 0: ['janeiro', 'maio', 'outubro']
nível 1: ['abril', 'agosto', 'fevereiro'] ['janeiro', 'julho', 'junho'] ['maio', 'marco', 'novembro'] ['outubro', 'setembro']
```

### 12. Inserir dezembro

Divisão: folha dividida em ['abril', 'agosto'] | ['dezembro', 'fevereiro'], dezembro copiada para o pai.
Divisão: nó interno dividido em ['dezembro', 'janeiro'] | ['outubro'], maio sobe para o pai.
Divisão: raiz dividida, nova raiz [maio].

```
nível 0: ['maio']
nível 1: ['dezembro', 'janeiro'] ['outubro']
nível 2: ['abril', 'agosto'] ['dezembro', 'fevereiro'] ['janeiro', 'julho', 'junho'] ['maio', 'marco', 'novembro'] ['outubro', 'setembro']
```

## Exercício 2: B+ de ordem 6 resultante

```
nível 0: [5, 14, 25, 34, 67]
nível 1: [1, 2, 4] [5, 7, 12] [14, 15, 18, 23] [25, 26, 32, 33] [34, 35, 43, 45, 46] [67, 102, 112, 234, 765]
```
