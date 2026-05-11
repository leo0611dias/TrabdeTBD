import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler

PASTA_INPUT = "../transform/output"   # saída do limpeza.py
PASTA_OUTPUT = "../transform/output"  # sobrescreve com versão normalizada


def converter_tipos(df, nome):
    """
    Tenta converter colunas para os tipos certos.
    Colunas numéricas devem ser float/int, não texto.
    """
    print(f"\n--- Convertendo tipos: {nome} ---")

    for col in df.columns:
        palavras_texto = ['nome', 'endereco', 'regiao', 'municipio', 'uf',
                          'inep', 'codigo', 'tipo', 'modalidade', 'dependencia']
        if any(p in col for p in palavras_texto):
            continue

        convertido = pd.to_numeric(df[col], errors='coerce')

        taxa_sucesso = convertido.notna().sum() / len(df)
        if taxa_sucesso > 0.5:
            df[col] = convertido
            print(f"  ✅ '{col}' → numérico ({taxa_sucesso:.0%} convertido)")

    return df


def preencher_nans(df, nome):
    """
    Preenche valores faltantes (NaN) de forma inteligente:
    - Colunas numéricas: preenche com a MEDIANA (mais robusto que a média)
    - Colunas de texto: preenche com 'NAO_INFORMADO'
    """
    print(f"\n--- Preenchendo NaNs: {nome} ---")

    nans_antes = df.isna().sum().sum()

    colunas_numericas = df.select_dtypes(include=[np.number]).columns
    for col in colunas_numericas:
        qtd_nan = df[col].isna().sum()
        if qtd_nan > 0:
            mediana = df[col].median()
            df[col] = df[col].fillna(mediana)
            print(f"  → '{col}': {qtd_nan} NaNs preenchidos com mediana={mediana:.2f}")

    colunas_texto = df.select_dtypes(include=['object']).columns
    for col in colunas_texto:
        qtd_nan = df[col].isna().sum()
        if qtd_nan > 0:
            df[col] = df[col].fillna('NAO_INFORMADO')
            print(f"  → '{col}': {qtd_nan} NaNs preenchidos com 'NAO_INFORMADO'")

    nans_depois = df.isna().sum().sum()
    print(f"  Total NaNs: {nans_antes} → {nans_depois}")

    return df


def normalizar_numericos(df, nome):
    """
    Aplica normalização Min-Max nas colunas numéricas.
    Isso é NECESSÁRIO para o K-Means funcionar bem —
    sem isso, colunas com valores grandes (ex: nº alunos = 1000)
    dominam colunas com valores pequenos (ex: IDEB = 5.2).

    Resultado: todos os valores ficam entre 0 e 1.
    Colunas normalizadas ganham o sufixo '_norm'.
    """
    print(f"\n--- Normalizando valores numéricos: {nome} ---")

    excluir = ['co_entidade', 'codigo_inep', 'cod_inep', 'inep', 'ano', 'year']

    colunas_numericas = [
        col for col in df.select_dtypes(include=[np.number]).columns
        if not any(ex in col for ex in excluir)
    ]

    if not colunas_numericas:
        print("  Nenhuma coluna numérica para normalizar.")
        return df

    scaler = MinMaxScaler()
    valores_norm = scaler.fit_transform(df[colunas_numericas])

    for i, col in enumerate(colunas_numericas):
        df[f"{col}_norm"] = valores_norm[:, i]

    print(f"  ✅ {len(colunas_numericas)} colunas normalizadas (sufixo _norm adicionado)")
    return df

arquivos_limpos = [
    "escolas_limpo.csv",
    "ideb_limpo.csv",
    "infraestrutura_limpo.csv",
    "matriculas_limpo.csv",
]

for arquivo in arquivos_limpos:
    caminho = os.path.join(PASTA_INPUT, arquivo)

    if not os.path.exists(caminho):
        print(f"\n⚠️  Não encontrado: {caminho} — pulando.")
        continue

    print(f"\n{'='*50}")
    print(f"Processando: {arquivo}")

    df = pd.read_csv(caminho, encoding='utf-8')

    df = converter_tipos(df, arquivo)
    df = preencher_nans(df, arquivo)
    df = normalizar_numericos(df, arquivo)

    # Salva de volta (substitui o arquivo limpo com a versão normalizada)
    nome_saida = arquivo.replace('_limpo.csv', '_normalizado.csv')
    caminho_saida = os.path.join(PASTA_OUTPUT, nome_saida)
    df.to_csv(caminho_saida, index=False, encoding='utf-8')
    print(f"  💾 Salvo em: {caminho_saida}")

print("\n" + "="*50)
print("NORMALIZAÇÃO CONCLUÍDA")