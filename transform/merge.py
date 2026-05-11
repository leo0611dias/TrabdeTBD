import pandas as pd
import numpy as np
import os

PASTA_INPUT = "../transform/output"
PASTA_OUTPUT = "../transform/output"

os.makedirs(PASTA_OUTPUT, exist_ok=True)

def achar_coluna_inep(df):
    """
    Cada dataset pode ter o código INEP com nome diferente.
    Essa função procura pelo nome mais provável.
    """
    candidatos = ['co_entidade', 'codigo_inep', 'cod_inep', 'inep',
                  'id_escola', 'codesc', 'cod_escola']
    for candidato in candidatos:
        if candidato in df.columns:
            return candidato
    return None  # Não encontrou — vai precisar ajuste manual

print("Carregando datasets normalizados...")

datasets = {}
arquivos = {
    'escolas':       'escolas_normalizado.csv',
    'ideb':          'ideb_normalizado.csv',
    'infraestrutura':'infraestrutura_normalizado.csv',
    'matriculas':    'matriculas_normalizado.csv',
}

for chave, arquivo in arquivos.items():
    caminho = os.path.join(PASTA_INPUT, arquivo)
    if os.path.exists(caminho):
        df = pd.read_csv(caminho, encoding='utf-8')
        datasets[chave] = df
        print(f"  ✅ {chave}: {len(df)} linhas, {len(df.columns)} colunas")
    else:
        print(f"  ⚠️  Não encontrado: {arquivo}")

if not datasets:
    print("\n❌ Nenhum dataset encontrado. Execute limpeza.py e normalizacao.py primeiro.")
    exit()

print("\nPadronizando a chave de merge (Código INEP)...")

for nome, df in datasets.items():
    col_inep = achar_coluna_inep(df)

    if col_inep is None:
        print(f"  ⚠️  Dataset '{nome}' não tem coluna INEP reconhecível!")
        print(f"     Colunas disponíveis: {list(df.columns)}")
        print(f"     → Você precisará ajustar manualmente.")
    else:
        if col_inep != 'codigo_inep':
            df = df.rename(columns={col_inep: 'codigo_inep'})
            datasets[nome] = df
            print(f"  → '{nome}': renomeado '{col_inep}' para 'codigo_inep'")
        else:
            print(f"  → '{nome}': já usa 'codigo_inep' ✅")

        # Garante que o código seja string limpa (sem .0 no final)
        datasets[nome]['codigo_inep'] = (
            datasets[nome]['codigo_inep']
            .astype(str)
            .str.replace('.0', '', regex=False)
            .str.strip()
        )

print("\nRealizando merge dos datasets...")

if 'escolas' not in datasets:
    print("❌ Dataset de escolas é obrigatório para o merge!")
    exit()

df_final = datasets['escolas'].copy()
print(f"  Base: escolas — {len(df_final)} linhas")

# Ordem de merge: do mais importante ao menos importante
ordem_merge = ['ideb', 'infraestrutura', 'matriculas']

for nome in ordem_merge:
    if nome not in datasets:
        continue

    df_aux = datasets[nome]

    if 'codigo_inep' not in df_aux.columns:
        print(f"  ⚠️  '{nome}' sem 'codigo_inep' — pulando.")
        continue

    colunas_ja_existentes = set(df_final.columns) - {'codigo_inep'}
    colunas_novas = [col for col in df_aux.columns
                     if col not in colunas_ja_existentes or col == 'codigo_inep']
    df_aux = df_aux[colunas_novas]

    antes = len(df_final)
    df_final = pd.merge(df_final, df_aux, on='codigo_inep', how='left')
    print(f"  + merge com '{nome}': {antes} → {len(df_final)} linhas "
          f"({len(df_final.columns)} colunas)")


print("\nPreenchendo NaNs pós-merge...")

nans_surgidos = df_final.isna().sum()
nans_surgidos = nans_surgidos[nans_surgidos > 0]

if len(nans_surgidos) > 0:
    print(f"  Colunas com NaN após merge:")
    for col, qtd in nans_surgidos.items():
        pct = qtd / len(df_final) * 100
        print(f"    '{col}': {qtd} NaNs ({pct:.1f}%)")

    for col in df_final.columns:
        if df_final[col].isna().sum() == 0:
            continue
        if df_final[col].dtype in [np.float64, np.int64]:
            df_final[col] = df_final[col].fillna(df_final[col].median())
        else:
            df_final[col] = df_final[col].fillna('NAO_INFORMADO')
else:
    print("  Nenhum NaN! Merge perfeito ✅")

# Arquivo principal para mineração
caminho_final = os.path.join(PASTA_OUTPUT, "dataset_transformado.csv")
df_final.to_csv(caminho_final, index=False, encoding='utf-8')

# Versão Parquet
caminho_parquet = os.path.join(PASTA_OUTPUT, "dataset_transformado.parquet")
df_final.to_parquet(caminho_parquet, index=False)

print(f"\n{'='*50}")
print("MERGE CONCLUÍDO")
print(f"  Dataset final: {len(df_final)} linhas × {len(df_final.columns)} colunas")
print(f"  Tamanho CSV:     {os.path.getsize(caminho_final) / 1024:.1f} KB")
print(f"  Tamanho Parquet: {os.path.getsize(caminho_parquet) / 1024:.1f} KB")
print(f"\n  Arquivos gerados:")
print(f"    → {caminho_final}")
print(f"    → {caminho_parquet}")
print(f"\n  Colunas do dataset final:")
for col in df_final.columns:
    print(f"    - {col}")