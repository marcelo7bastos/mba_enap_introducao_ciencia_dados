# SOLUÇÃO COMPLETA: CARREGAR DBF + SELECIONAR COLUNAS
# Este código resolve tanto o erro FieldMissingError quanto o KeyError

import dbf
import pandas as pd

def read_dbf_safe(filename):
    """Lê arquivo DBF de forma segura, evitando FieldMissingError"""
    table = dbf.Table(filename=filename)
    table.open(dbf.READ_ONLY)
    
    try:
        records = []
        for record in table:
            record_dict = {}
            for field_name in table.field_names:
                record_dict[field_name] = record[field_name]
            records.append(record_dict)
        
        df = pd.DataFrame(records)
        
    finally:
        table.close()
    
    return df

def create_geo_dataframe(df):
    """
    Cria DataFrame geo com as colunas corretas, usando múltiplas estratégias
    """
    print("🔍 Analisando estrutura do DataFrame...")
    print(f"   Dimensões: {df.shape}")
    print(f"   Colunas: {len(df.columns)}")
    
    # Estratégia 1: Tentar usar índices originais (se DataFrame tem colunas suficientes)
    if len(df.columns) > 19:
        try:
            print("\n📍 Tentativa 1: Usando índices originais [9, 16, 18, 19]")
            
            # Verificar se as colunas nos índices fazem sentido
            col_9 = df.columns[9]
            col_16 = df.columns[16]
            col_18 = df.columns[18]
            col_19 = df.columns[19]
            
            print(f"   Coluna [9]:  {col_9}")
            print(f"   Coluna [16]: {col_16}")
            print(f"   Coluna [18]: {col_18}")
            print(f"   Coluna [19]: {col_19}")
            
            # Testar se consegue criar o DataFrame
            df_geo = df[[col_9, col_16, col_18, col_19]].rename(columns={
                col_9: "cod_ibge", 
                col_16: "categoria", 
                col_18: "long", 
                col_19: "lat"
            })
            
            print("✅ Estratégia 1 funcionou!")
            return df_geo, "índices_originais"
            
        except Exception as e:
            print(f"❌ Estratégia 1 falhou: {e}")
    
    # Estratégia 2: Buscar por nomes de colunas
    print("\n📍 Tentativa 2: Buscando por nomes de colunas")
    
    # Buscar colunas por padrões de nome
    cod_ibge_candidates = [col for col in df.columns if any(term in str(col).upper() for term in ['COD', 'IBGE', 'GEOCOD', 'CODIGO'])]
    categoria_candidates = [col for col in df.columns if any(term in str(col).upper() for term in ['CATEG', 'TIPO', 'CLASS', 'CATEGORIA'])]
    long_candidates = [col for col in df.columns if any(term in str(col).upper() for term in ['LONG', 'X', 'LONGITUDE'])]
    lat_candidates = [col for col in df.columns if any(term in str(col).upper() for term in ['LAT', 'Y', 'LATITUDE'])]
    
    print(f"   Candidatos código IBGE: {cod_ibge_candidates}")
    print(f"   Candidatos categoria: {categoria_candidates}")
    print(f"   Candidatos longitude: {long_candidates}")
    print(f"   Candidatos latitude: {lat_candidates}")
    
    if cod_ibge_candidates and categoria_candidates and long_candidates and lat_candidates:
        try:
            df_geo = df[[cod_ibge_candidates[0], categoria_candidates[0], long_candidates[0], lat_candidates[0]]].rename(columns={
                cod_ibge_candidates[0]: "cod_ibge",
                categoria_candidates[0]: "categoria", 
                long_candidates[0]: "long",
                lat_candidates[0]: "lat"
            })
            
            print("✅ Estratégia 2 funcionou!")
            return df_geo, "nomes_colunas"
            
        except Exception as e:
            print(f"❌ Estratégia 2 falhou: {e}")
    
    # Estratégia 3: Mostrar todas as colunas para seleção manual
    print("\n📍 Tentativa 3: Seleção manual necessária")
    print("📋 Todas as colunas disponíveis:")
    for i, col in enumerate(df.columns):
        sample_value = df.iloc[0, i] if len(df) > 0 else "N/A"
        print(f"  [{i:2d}] {col} - Exemplo: {sample_value}")
    
    print("\n💡 Identifique manualmente as colunas corretas e ajuste o código!")
    return None, "manual_required"

# EXECUÇÃO PRINCIPAL
print("🚀 INICIANDO PROCESSAMENTO DO ARQUIVO DBF")
print("=" * 50)

# Passo 1: Carregar o arquivo DBF
print("\n📂 Passo 1: Carregando arquivo DBF...")
try:
    df = read_dbf_safe('./BR_Localidades_2010.dbf')
    print("✅ Arquivo DBF carregado com sucesso!")
except Exception as e:
    print(f"❌ Erro ao carregar DBF: {e}")
    exit()

# Passo 2: Criar DataFrame geo
print("\n🗺️  Passo 2: Criando DataFrame geo...")
df_geo, strategy = create_geo_dataframe(df)

if df_geo is not None:
    # Passo 3: Processar dados
    print(f"\n⚙️  Passo 3: Processando dados (estratégia: {strategy})...")
    
    # Limpar dados
    df_geo['cod_ibge'] = df_geo['cod_ibge'].astype(str).str.strip()
    df_geo['categoria'] = df_geo['categoria'].astype(str).str.strip()
    
    # Mostrar categorias únicas
    print(f"📂 Categorias encontradas: {df_geo['categoria'].unique()}")
    
    # Filtrar apenas cidades
    df_geo_cidades = df_geo[df_geo['categoria'] == 'CIDADE'].copy()
    
    print(f"✅ Processamento concluído!")
    print(f"   Total de registros: {len(df_geo)}")
    print(f"   Cidades encontradas: {len(df_geo_cidades)}")
    
    # Mostrar resultado
    print(f"\n📊 Informações do DataFrame final:")
    df_geo_cidades.info()
    
    print(f"\n🔍 Primeiras 5 cidades:")
    print(df_geo_cidades.head())
    
else:
    print("\n❌ Não foi possível criar o DataFrame geo automaticamente.")
    print("💡 Use as informações mostradas acima para ajustar o código manualmente.")
