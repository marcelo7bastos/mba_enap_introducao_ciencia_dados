# 📘 Fluxo de Trabalho - MBA Ciência de Dados

Este repositório contém o material do professor e meus **trabalhos realizados**  
(armazenados na pasta `trabalhos_realizados`).

---

## 🔄 Atualizar material com as mudanças do professor

Antes de começar um novo estudo ou exercício, sincronize o repositório:

```bash
git fetch upstream
git merge upstream/main
git push origin main
```

---

## 📝 Fluxo do dia a dia (meus trabalhos)

Depois de criar ou editar arquivos (ex.: dentro da pasta `trabalhos_realizados`):

```bash
git add .
git commit -m "minhas alterações"
git push origin main
```

---

## 📂 Estrutura

- `CD/` → material do professor  
- `Python/` → material do professor  
- `data/` → material do professor  
- `trabalhos_realizados/` → **meus trabalhos e anotações**
  - **Exercício de Web Scraping (4.1b):**
    - `webscrapy_41b.py`: Versão inicial do script. Realiza a busca no Google e extrai os resultados em um único fluxo.
    - `webscrapy_41b_v2.py`: Versão refatorada e melhorada, com funções separadas e mais robustez. **(Recomendado para estudo)**
    - `webscraping_41b_resultado.csv`: Arquivo com os dados coletados pelo script (título e URL).


---

## ✅ Boas práticas

1. Sempre rode **atualização (`fetch` + `merge`) antes de começar a estudar**.  
2. Salve seus trabalhos com `commit` + `push` para manter seu fork atualizado.  
3. Nunca edite diretamente os arquivos do professor, use a pasta `trabalhos_realizados` para seus próprios estudos.

---

## 🙏 Créditos

Material original disponibilizado pelo professor **Alex Lopes Pereira**  
🔗 [Repositório Original](https://github.com/alexlopespereira/mba_enap)
