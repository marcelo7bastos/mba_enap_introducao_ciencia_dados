# v1: abrir o Google e buscar "gov.br", capturar só o 1º resultado (título + url)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import csv
import os


def main():
    # 1) configurar o Chrome (pode rodar com janela visível para aprender melhor)
    chrome_options = Options()
    # se quiser “sem janela”, descomente:
    # chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--lang=pt-BR")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=chrome_options)

    try:
        # 2) abrir google.com
        driver.get("https://www.google.com/")

        wait = WebDriverWait(driver, 20)

        # 3) aceitar consentimento se aparecer (depende da região/conta)
        # tentamos achar botão “Aceitar tudo” / “Concordo” etc.; se não existir, só seguimos
        try:
            consent_btn = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//button[.//div[contains(.,'Aceitar') or contains(.,'Concordo')]] | //button[contains(.,'Aceitar')] | //button[contains(.,'Concordo')]")
                )
            )
            consent_btn.click()
        except Exception:
            pass  # sem consentimento, ok

        # 4) localizar a caixa de busca e digitar "gov.br"
        search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
        search_box.clear()
        search_box.send_keys("gov.br")
        search_box.send_keys(Keys.ENTER)

        # 5) esperar aparecer a área principal de resultados
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#search")))

        # 6) pegar o 1º resultado orgânico (h3 dentro de um link, dentro de #search)
        # esta estratégia é robusta para a maior parte dos layouts
        # 6) coletar TODOS os resultados orgânicos (h3 dentro de um link)
        # tentamos alguns seletores (Google muda layouts com frequência)
        candidate_selectors = [
            (By.CSS_SELECTOR, "div#search a h3"),
            (By.CSS_SELECTOR, "div#rso a h3"),
            (By.XPATH, "//div[@id='search']//a//h3"),
            (By.XPATH, "//a//h3"),
        ]

        h3_elements = []
        for by, sel in candidate_selectors:
            els = driver.find_elements(by, sel)
            if els:
                print(f"[debug] seletor que funcionou: {by} | {sel} | {len(els)} elementos")
                h3_elements = els
                break

        if not h3_elements:
            raise RuntimeError("Não consegui localizar resultados (h3).")

        # 7) transformar em lista de dicionários (titulo, url)
        resultados = []
        vistos = set()
        for h3 in h3_elements:
            try:
                a = h3.find_element(By.XPATH, "./ancestor::a")
                titulo = h3.text.strip()
                url = a.get_attribute("href")
                if not titulo or not url:
                    continue
                if url in vistos:
                    continue
                vistos.add(url)
                resultados.append({"titulo": titulo, "url": url})
            except Exception:
                # se algum item falhar, segue nos demais
                continue

        # 8) mostrar no formato pedido (lista de dicionários)
        print(resultados)
        
        # 9) salvar em arquivo CSV
        # Nome do arquivo CSV (usando caminho relativo)
        output_file = os.path.join('mba_enap_introducao_ciencia_dados',
                                   'trabalhos_realizados',
                                   'webscraping_41b_resultado.csv')
        # Garante que o diretório existe
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Cabeçalhos das colunas
        fieldnames = ['titulo', 'url']
        
        # Escrever no arquivo CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(resultados)
            
        print(f'\nResultados salvos em: {os.path.abspath(output_file)}')

    finally:
        # 8) feche o navegador ao final (deixe aberto enquanto estiver explorando com breakpoints)
        driver.quit()

if __name__ == "__main__":
    main()
