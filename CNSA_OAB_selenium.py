import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

PASTA_ENTRADA = "resultados_CNA_detalhes"
PASTA_SAIDA = "resultados_CNSA_detalhes"
URL_BASE = "https://cna.oab.org.br"

os.makedirs(PASTA_SAIDA, exist_ok=True)

def iniciar_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def coletar_texto(driver, xpath, replace_from=None, replace_to=""):
    try:
        elemento = driver.find_element(By.XPATH, xpath)
        texto = elemento.text
        return texto.replace(replace_from, replace_to) if replace_from else texto
    except Exception:
        return None

def processar_socios(driver):
    socios = []
    for i in range(1, 301):
        try:
            xpath = f'//*[@id="bodyContent"]/div[3]/div/div/div[2]/div[7]/div/table/tbody/tr[{i}]/td[2]'
            socios.append(coletar_texto(driver, xpath))
        except Exception:
            break
    return socios

def processar_arquivo(driver, arquivo):
    caminho_arquivo = os.path.join(PASTA_ENTRADA, arquivo)
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    sociedades = dados.get("Data", {}).get("Sociedades", [])
    if not sociedades:
        return {"erro": "Nenhuma sociedade encontrada", "url": None}

    url_parcial = sociedades[0].get("Url")
    if not url_parcial:
        return {"erro": "URL não encontrada", "url": None}

    url_completa = URL_BASE + url_parcial
    print(f"Acessando: {url_completa}")
    try:
        driver.get(url_completa)
        time.sleep(3)
        resultado = {
            "url": url_completa,
            "nome_escritorio": coletar_texto(driver, '//*[@id="bodyContent"]/div[3]/div/div/div[1]/h4/b'),
            "situacao_escritorio": coletar_texto(driver, '//*[@id="bodyContent"]/div[3]/div/div/div[2]/div[3]/span'),
            "inscricao": coletar_texto(driver, '//*[@id="bodyContent"]/div[3]/div/div/div[2]/div[1]', "Inscrição:\n"),
            "uf": coletar_texto(driver, '//*[@id="bodyContent"]/div[3]/div/div/div[2]/div[2]', "\n", " "),
            "endereco": coletar_texto(driver, '//*[@id="enderecoContainer"]', "\n", " "),
            "telefone_escritorio": coletar_texto(driver, '//*[@id="bodyContent"]/div[3]/div/div/div[2]/div[6]', "Telefones:\n"),
            "socios": processar_socios(driver),
        }
        return resultado
    except Exception as e:
        print(f"Erro ao coletar dados: {e}")
        return {"erro": str(e), "url": url_completa}

def processar_arquivos():
    driver = iniciar_driver()
    for arquivo in os.listdir(PASTA_ENTRADA):
        if arquivo.endswith(".json"):
            resultado = processar_arquivo(driver, arquivo)
            caminho_saida = os.path.join(PASTA_SAIDA, arquivo)
            with open(caminho_saida, 'w', encoding='utf-8') as f_out:
                json.dump(resultado, f_out, ensure_ascii=False, indent=4)
            print(f"Arquivo salvo: {caminho_saida}")
    driver.quit()

if __name__ == "__main__":
    processar_arquivos()
