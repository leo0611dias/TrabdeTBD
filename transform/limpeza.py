import pandas as pd
import os

PASTA_RAW = "../raw"          
PASTA_TRANSFORM = "../transform/output"  

# Cria a pasta de saída se não existir
os.makedirs(PASTA_TRANSFORM, exist_ok=True)

def limpar_dataframe(df, nome):
    
    print(f"\n{'='*50}")
    print(f"Limpando: {nome}")
    print(f"Linhas antes: {len(df)} | Colunas antes: {len(df.columns)}")

    colunas_antes = len(df.columns)
    df = df.dropna(axis=1, how='all')
    colunas_depois = len(df.columns)
    print(f"  → Colunas vazias removidas: {colunas_antes - colunas_depois}")

    linhas_antes = len(df)
    df = df.dropna(axis=0, how='all')
    print(f"  → Linhas completamente vazias removidas: {linhas_antes - len(df)}")

    linhas_antes = len(df)
    df = df.drop_duplicates()
    print(f"  → Duplicatas removidas: {linhas_antes - len(df)}")

    df.columns = (
        df.columns
        .str.strip()           # remove espaços nas pontas
        .str.lower()           # tudo minúsculo
        .str.replace(' ', '_') # espaço vira underline
        .str.replace('ç', 'c')
        .str.replace('ã', 'a')
        .str.replace('õ', 'o')
        .str.replace('á', 'a')
        .str.replace('é', 'e')
        .str.replace('í', 'i')
        .str.replace('ó', 'o')
        .str.replace('ú', 'u')
        .str.replace('â', 'a')
        .str.replace('ê', 'e')
        .str.replace('ô', 'o')
    )

    colunas_texto = df.select_dtypes(include=['object']).columns
    for col in colunas_texto:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace('nan', pd.NA)

    possiveis_nomes_inep = ['co_entidade', 'codigo_inep', 'cod_inep', 'inep', 'id_escola']
    for nome_col in possiveis_nomes_inep:
        if nome_col in df.columns:
            df[nome_col] = (
                df[nome_col]
                .astype(str)
                .str.replace('.0', '', regex=False)
                .str.strip()
            )
            print(f"  → Código INEP padronizado na coluna '{nome_col}'")
            break  

    print(f"Linhas depois: {len(df)} | Colunas depois: {len(df.columns)}")
    return df

# CARREGAMENTO E LIMPEZA DE CADA DATASET


# Lista de arquivos esperados na pasta raw/
# Formato: (nome_do_arquivo, apelido_para_logs)
arquivos = [
    ("escolas.csv",       "Escolas Públicas DF"),
    ("ideb.csv",          "IDEB / Desempenho"),
    ("infraestrutura.csv","Infraestrutura Escolar"),
    ("matriculas.csv",    "Matrículas e Turmas"),
]

dataframes_limpos = {} 

for arquivo, apelido in arquivos:
    caminho = os.path.join(PASTA_RAW, arquivo)

    if not os.path.exists(caminho):
        print(f"\n⚠️  Arquivo não encontrado: {caminho} — pulando.")
        continue

    for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
        try:
            df = pd.read_csv(caminho, sep=None, engine='python', encoding=encoding)
            print(f"\n✅ '{arquivo}' carregado com encoding={encoding}")
            break
        except Exception as e:
            print(f"  Falha com encoding={encoding}: {e}")
            df = None

    if df is None:
        print(f"❌ Não foi possível carregar {arquivo}")
        continue

    df_limpo = limpar_dataframe(df, apelido)

    nome_saida = arquivo.replace('.csv', '_limpo.csv')
    caminho_saida = os.path.join(PASTA_TRANSFORM, nome_saida)
    df_limpo.to_csv(caminho_saida, index=False, encoding='utf-8')
    print(f"  💾 Salvo em: {caminho_saida}")

    dataframes_limpos[arquivo] = df_limpo

print("\n" + "="*50)
print("LIMPEZA CONCLUÍDA")
print(f"Datasets processados: {len(dataframes_limpos)}")
for nome, df in dataframes_limpos.items():
    print(f"  - {nome}: {len(df)} linhas, {len(df.columns)} colunas")