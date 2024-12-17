import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

PASTA_ENTRADA = "resultados_CNA_detalhes"
PASTA_SAIDA = "resultados_CNSA_detalhes"

if not os.path.exists(PASTA_SAIDA):
    os.makedirs(PASTA_SAIDA)

URL_BASE = "https://cna.oab.org.br"

def iniciar_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executa o navegador sem interface gráfica
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def fazer_post_na_url(url):
    """ Faz um POST na URL usando requests e retorna o JSON do response. """
    try:
        print(f"Fazendo POST na URL: {url}")
        response = requests.post(url)
        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                print("Resposta inválida (não JSON).")
                return {"erro": "Resposta inválida", "status_code": response.status_code, "conteudo": response.text}
        else:
            print(f"Erro HTTP {response.status_code} ao acessar: {url}")
            return {"erro": f"HTTP {response.status_code}", "conteudo": response.text}
    except Exception as e:
        print(f"Erro ao fazer POST: {e}")
        return {"erro": str(e)}

def processar_arquivos():
    driver = iniciar_driver()
    
    for arquivo in os.listdir(PASTA_ENTRADA):
        if arquivo.endswith(".json"):
            caminho_arquivo = os.path.join(PASTA_ENTRADA, arquivo)
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            sociedades = dados.get("Data", {}).get("Sociedades", [])
            if not sociedades:
                print(f"Nenhuma sociedade encontrada no arquivo: {arquivo}")
                resultado = {"erro": "Nenhuma sociedade encontrada", "url": None}
            else:
                url_parcial = sociedades[0].get("Url")
                if url_parcial:
                    url_completa = URL_BASE + url_parcial
                    print(f"Acessando a URL: {url_completa}")
                    try:
                        # Usar Selenium para acessar a página e aguardar o carregamento
                        driver.get(url_completa)
                        time.sleep(2)  # Aguardar o carregamento da página
                        url_final = driver.current_url  # Coletar a URL final
                        
                        # Fazer POST na URL final e capturar o response
                        response_json = fazer_post_na_url(url_final)
                        response_json["url"] = url_final  # Adicionar a URL no resultado
                        resultado = response_json
                        
                    except Exception as e:
                        print(f"Erro ao acessar ou processar a URL: {e}")
                        resultado = {"erro": str(e), "url": url_completa}
                else:
                    print(f"URL não encontrada no arquivo: {arquivo}")
                    resultado = {"erro": "URL não encontrada", "url": None}
            
            # Salvar o resultado em um novo arquivo na pasta de saída
            caminho_saida = os.path.join(PASTA_SAIDA, arquivo)
            with open(caminho_saida, 'w', encoding='utf-8') as f_out:
                json.dump(resultado, f_out, ensure_ascii=False, indent=4)
            
            print(f"Arquivo processado e salvo em: {caminho_saida}")

    driver.quit()

if __name__ == "__main__":
    processar_arquivos()
