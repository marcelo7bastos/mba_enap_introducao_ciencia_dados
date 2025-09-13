#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Exercício 4.1b — Webscrapy do Google (Selenium)
------------------------------------------------
Abre o Google, busca por "gov.br" e coleta os resultados orgânicos da
primeira página, retornando uma lista de dicionários:
    [{"titulo": "...", "url": "..."}, ...]

Também salva o resultado em CSV na pasta `trabalhos_realizados`.

Decisões de projeto:
- Selenium + WebDriverWait: o HTML do Google muda com frequência; carregar a
  página “de verdade” e esperar elementos específicos torna o scraper mais estável.
- Estratégia de seleção “robusta”: testamos alguns seletores (CSS/XPath) porque
  o Google alterna o markup entre experiências/regiões. O primeiro seletor que
  encontrar elementos é usado.
- Ética: coletamos apenas a 1ª página, com espera explícita e sem enviar
  requisições agressivas. Para uso intensivo, prefira API oficial (Programmable Search).

Manutenção:
- Caso o seletor pare de funcionar, ajuste a lista CANDIDATE_SELECTORS.
- Para mudar o termo de busca, altere DEFAULT_QUERY ou passe a parametrizar.
"""

from __future__ import annotations  # Permite o uso de anotações de tipo como strings

import csv  # Para manipulação de arquivos CSV
import os  # Para interação com o sistema de arquivos
from typing import List, Dict, Tuple  # Tipos para anotações estáticas

from selenium import webdriver  # Framework principal de automação web
from selenium.webdriver.common.by import By  # Estratégias de localização de elementos
from selenium.webdriver.common.keys import Keys  # Teclas especiais do teclado
from selenium.webdriver.support.ui import WebDriverWait  # Para esperas explícitas
from selenium.webdriver.support import expected_conditions as EC  # Condições de espera
from webdriver_manager.chrome import ChromeDriverManager  # Gerenciador do ChromeDriver
from selenium.webdriver.chrome.service import Service  # Configuração do serviço do Chrome
from selenium.webdriver.chrome.options import Options  # Opções de configuração do navegador


# ----------------------------- Constantes ------------------------------------

DEFAULT_QUERY: str = "gov.br"

# Seletores candidatos para encontrar os títulos (h3) de resultados orgânicos.
# A ordem importa: usamos o primeiro que retornar elementos.
CANDIDATE_SELECTORS: List[Tuple[str, str]] = [
    (By.CSS_SELECTOR, "div#search a h3"), # seletor usando css selector e id search
    (By.CSS_SELECTOR, "div#rso a h3"), # seletor usando css selector e id rso
    (By.XPATH, "//div[@id='search']//a//h3"), # seletor usando xpath e id search
    (By.XPATH, "//a//h3"), # seletor usando xpath
]

# Caminho de saída do CSV (relativo ao projeto/fork do aluno)
CSV_OUTPUT_RELATIVE: str = os.path.join(
    "mba_enap_introducao_ciencia_dados", "trabalhos_realizados", "webscraping_41b_resultado.csv"
)


def build_chrome_driver() -> webdriver.Chrome:
    """
    Cria e retorna uma instância do Chrome WebDriver com opções razoáveis para scraping leve.

    - `--start-maximized`: janela cheia ajuda no aprendizado (ver o que está acontecendo).
    - user-agent “realista”: reduz bloqueios triviais.
    - `--lang=pt-BR`: melhora a chance de rótulos tipo “Aceitar/Concordo” aparecerem.
    """
    chrome_options = Options() 
    # Descomente para rodar sem abrir janela (CI/servidor):
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--lang=pt-BR") # define o idioma do navegador
    chrome_options.add_argument("--start-maximized") # abre o navegador maximizado
    chrome_options.add_argument("--disable-blink-features=AutomationControlled") # desabilita o automação do navegador
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    ) # define o user agent do navegador para evitar bloqueios

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), 
        options=chrome_options
    )
    return driver


def handle_consent_if_present(driver: webdriver.Chrome, wait: WebDriverWait) -> None:
    """
    Tenta aceitar o banner de consentimento, caso apareça.

    Observação:
    - O Google apresenta variantes desse diálogo conforme país/conta/experimentos A/B.
    - Usamos XPaths mais genéricos com palavras “Aceitar/Concordo”.
    - Se não existir, seguimos normalmente.
    """
    try:
        consent_btn = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//button[.//div[contains(.,'Aceitar') or contains(.,'Concordo')]] "
                    "| //button[contains(.,'Aceitar')] "
                    "| //button[contains(.,'Concordo')]"
                )
            )
        )
        consent_btn.click()
    except Exception:
        # Sem banner de consentimento ou variação não reconhecida: prossiga.
        pass


def search_google(driver: webdriver.Chrome, wait: WebDriverWait, query: str) -> None:
    """
    Abre a home do Google, aceita consentimento (se houver), localiza a caixa de busca,
    envia a consulta e espera o container de resultados estar presente.
    """
    driver.get("https://www.google.com/")

    handle_consent_if_present(driver, wait)

    # Localiza a caixa de busca, envia o termo e confirma.
    search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.ENTER)

    # Aguarda o container principal de resultados para garantir que a página carregou.
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#search")))


def collect_results(driver: webdriver.Chrome) -> List[Dict[str, str]]:
    """
    Coleta os resultados orgânicos da 1ª página do Google.
    Retorna uma lista de dicionários: [{"titulo": "...", "url": "..."}].

    Estratégia:
    - Tenta múltiplos seletores e usa o primeiro que encontrar elementos.
    - Para cada <h3>, sobe ao elemento <a> ancestral para obter o href.
    - Remove duplicados por URL.
    """
    h3_elements = []
    for by, sel in CANDIDATE_SELECTORS:
        els = driver.find_elements(by, sel)
        if els:
            print(f"[debug] seletor que funcionou: {by} | {sel} | {len(els)} elementos")
            h3_elements = els
            break

    if not h3_elements:
        raise RuntimeError("Não consegui localizar resultados (h3). Ajuste CANDIDATE_SELECTORS.")

    resultados: List[Dict[str, str]] = []
    vistos = set()

    for h3 in h3_elements:
        try:
            a = h3.find_element(By.XPATH, "./ancestor::a")  # sobe do <h3> ao link <a>
            titulo = h3.text.strip()
            url = a.get_attribute("href")
            if not titulo or not url:
                continue
            if url in vistos:
                continue
            vistos.add(url)
            resultados.append({"titulo": titulo, "url": url})
        except Exception:
            # Em scraping, é saudável ignorar falhas pontuais em itens individuais.
            continue

    return resultados


def save_as_csv(rows: List[Dict[str, str]], csv_path: str) -> str:
    """
    Salva a lista de dicionários em CSV com as colunas ['titulo', 'url'].

    - Garante a criação do diretório.
    - Retorna o caminho **absoluto** gerado (útil para logs/prints).
    """
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["titulo", "url"])
        writer.writeheader()
        writer.writerows(rows)
    return os.path.abspath(csv_path)


def main() -> None:
    """
    Fluxo principal:
    1) Sobe o ChromeDriver
    2) Busca por DEFAULT_QUERY
    3) Coleta resultados da 1ª página
    4) Imprime no console e salva em CSV
    """
    driver = build_chrome_driver()
    try:
        wait = WebDriverWait(driver, 20) 
        search_google(driver, wait, DEFAULT_QUERY)

        resultados = collect_results(driver)

        # Mostra no formato pedido pelo enunciado
        print(resultados)

        # Persiste em CSV para consumo posterior (Looker Studio/Excel/ETL etc.)
        out_path = save_as_csv(resultados, CSV_OUTPUT_RELATIVE)
        print(f"\nResultados salvos em: {out_path}")

    finally:
        # Feche o navegador (em sessões de aprendizado, pode comentar para inspecionar a página).
        driver.quit()


if __name__ == "__main__":
    main()
