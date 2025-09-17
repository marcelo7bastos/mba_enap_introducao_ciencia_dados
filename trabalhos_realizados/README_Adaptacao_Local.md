# Adaptação do Notebook Google Colab para Ambiente Local

## Arquivo Original vs Adaptado

- **Original**: `Aula6_PIB_GeoMunicipios.ipynb` (Google Colab)
- **Adaptado**: `Aula6_PIB_GeoMunicipios_Local.ipynb` (Ambiente Local)

## Principais Mudanças Realizadas

### 1. Remoção da Autenticação do Google Colab
**Antes:**
```python
from google.colab import auth
auth.authenticate_user()
print('Authenticated')
```

**Depois:**
```python
# Versão local - removida autenticação do Google Colab
import pandas as pd
import os
import subprocess
import sys
print('Ambiente local configurado!')
```

### 2. Substituição de Comandos de Sistema

#### Instalação de Pacotes
**Antes:**
```python
!pip install dbf
```

**Depois:**
```python
try:
    import dbf
    print("Biblioteca 'dbf' já está instalada")
except ImportError:
    print("Instalando biblioteca 'dbf'...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "dbf"])
    import dbf
    print("Biblioteca 'dbf' instalada com sucesso!")
```

#### Download de Arquivos
**Antes:**
```python
!wget https://github.com/renatocol/Latitude_Longitude_Brasil/raw/master/BR_Localidades_2010.dbf
```

**Depois:**
```python
import urllib.request
import os

url = "https://github.com/renatocol/Latitude_Longitude_Brasil/raw/master/BR_Localidades_2010.dbf"
filename = "BR_Localidades_2010.dbf"

if not os.path.exists(filename):
    print(f"Baixando {filename}...")
    urllib.request.urlretrieve(url, filename)
    print(f"Download concluído: {filename}")
else:
    print(f"Arquivo {filename} já existe")
```

#### Listagem de Arquivos
**Antes:**
```python
!ls .
```

**Depois:**
```python
print("Arquivos no diretório atual:")
for item in os.listdir('.'):
    if os.path.isfile(item):
        size = os.path.getsize(item)
        print(f"{item} ({size:,} bytes)")
    else:
        print(f"{item}/ (diretório)")
```

### 3. Melhorias Adicionadas

1. **Verificação de dependências**: O notebook agora verifica se as bibliotecas necessárias estão instaladas antes de usá-las
2. **Tratamento de erros**: Adicionada verificação se arquivos já existem antes de fazer download
3. **Informações adicionais**: Adicionadas estatísticas descritivas dos dados
4. **Salvamento de resultados**: Adicionada funcionalidade para salvar os dados processados em CSV

## Funcionalidades Mantidas

✅ **Todas as funcionalidades principais foram mantidas:**
- Processamento de arquivos DBF
- Leitura de arquivos Excel online
- Manipulação de dados com pandas
- Filtragem de dados geográficos
- Criação de coordenadas lat/long
- Análise de dados municipais

## Como Usar

1. **Instale o Jupyter Notebook** (se ainda não tiver):
   ```bash
   pip install jupyter notebook
   ```

2. **Navegue até o diretório do projeto**:
   ```bash
   cd "c:\Users\marce\OneDrive - mtegovbr\0001_NOVA_PASTA\DESENVOLVIMENTO_PESSOAL\001_mba_ciencia_dados_enap\016_introducao_ciencia_dados\mba_enap_introducao_ciencia_dados\trabalhos_realizados"
   ```

3. **Inicie o Jupyter Notebook**:
   ```bash
   jupyter notebook
   ```

4. **Abra o arquivo**: `Aula6_PIB_GeoMunicipios_Local.ipynb`

5. **Execute as células** sequencialmente

## Dependências Necessárias

O notebook instalará automaticamente as seguintes bibliotecas se não estiverem presentes:
- `pandas`
- `dbf`
- `openpyxl`
- `urllib.request` (padrão do Python)

## Vantagens da Versão Local

1. **Independência**: Não depende de conexão com Google Colab
2. **Controle**: Maior controle sobre o ambiente de execução
3. **Persistência**: Arquivos e dados ficam salvos localmente
4. **Flexibilidade**: Pode ser executado em qualquer ambiente Python
5. **Performance**: Pode ser mais rápido dependendo da máquina local

## Resultado Final

O notebook adaptado produz exatamente os mesmos resultados que a versão original do Google Colab, mas funciona perfeitamente no seu ambiente local sem perder nenhuma funcionalidade.
