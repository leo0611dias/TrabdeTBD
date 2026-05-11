# Projeto Data Major - Tópicos de Banco de Dados

Este projeto implementa um pipeline de ETL para processar dados de docentes do INEP, utilizando arquiteturas RDBMS, NoSQL e NewSQL.

## Arquitetura
- **Engine de Processamento:** Python / Pandas
- **Formato Intermediário:** Apache Parquet (colunar e otimizado)
- **Armazenamento RDBMS:** PostgreSQL
- **Modelagem:** Esquema relacional para análise de métricas educacionais.

## Como Executar
1. Instale as dependências: `pip install -r requirements.txt`
2. Configure as variáveis de ambiente para conexão com o banco.
3. Execute o script em `scripts/etl_pipeline.py`.