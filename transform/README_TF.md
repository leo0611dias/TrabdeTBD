# Transform — Etapa ETL
 
## O que essa etapa faz
 
Recebe os arquivos brutos da etapa **Extract** e entrega um dataset
limpo, padronizado e pronto para a etapa de **Load/Mineração**.
 
---
 
## Como executar (em ordem)
 
```bash
# 1. Limpeza
python transform/limpeza.py
 
# 2. Normalização
python transform/normalizacao.py
 
# 3. Merge
python transform/merge.py
```
 
O resultado final é o arquivo `transform/output/dataset_transformado.parquet`.
 
---
 
## O que cada script faz
 
### `limpeza.py`
- Remove colunas e linhas completamente vazias
- Remove duplicatas
- Padroniza nomes das colunas (minúsculo, sem acentos, underline)
- Padroniza o Código INEP (chave de integração entre datasets)
- Suporta CSV com separador `,` ou `;` e encodings `utf-8` / `latin-1`
### `normalizacao.py`
- Converte colunas numéricas que vieram como texto
- Preenche valores faltantes (NaN) com mediana (numérico) ou "NAO_INFORMADO" (texto)
- Aplica normalização Min-Max nas colunas numéricas (valores entre 0 e 1)
- A normalização é obrigatória para o K-Means funcionar corretamente
### `merge.py`
- Une os 4 datasets usando o **Código INEP** como chave
- Usa `left join`: mantém todas as escolas mesmo sem IDEB ou infraestrutura
- Salva em `.csv` e `.parquet`
---
 
## Arquivos esperados na pasta `raw/`
 
| Arquivo | Conteúdo |
|---|---|
| `escolas.csv` | Nome, endereço, região, tipo de ensino |
| `ideb.csv` | Notas IDEB, fluxo escolar, desempenho |
| `infraestrutura.csv` | Internet, laboratório, computadores |
| `matriculas.csv` | Número de alunos, turmas, histórico |
 
---
 
## Por que normalizar?
 
O K-Means mede **distância** entre pontos. Se uma coluna tem valores
de 0 a 5000 (alunos) e outra de 0 a 10 (IDEB), a primeira domina
o cálculo. A normalização Min-Max coloca tudo entre 0 e 1.
 
---
 
## Justificativa acadêmica
 
| Técnica usada | Justificativa |
|---|---|
| Remoção de duplicatas | Integridade dos dados |
| Preenchimento com mediana | Robusto a outliers |
| Normalização Min-Max | Pré-requisito para K-Means |
| Chave INEP para merge | Padrão oficial do MEC/INEP |
| Saída em Parquet | Armazenamento colunar para Big Data |