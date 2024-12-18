import os
import json
import requests
from datetime import datetime
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

BASE_URL = 'https://cna.oab.org.br/'
PASTAS = {
    'OAB': 'output_CNA_OAB',
    'Detalhes': 'resultados_CNA_detalhes',
    'Saida': 'detalhes_CNA_processados',
    'SaidaImg': 'imgs_CNA_OAB',
    'SaidaSelenium': 'resultados_CNSA_detalhes'
}

# Criar todas as pastas necessárias
for pasta in PASTAS.values():
    os.makedirs(pasta, exist_ok=True)

def salvar_em_arquivo(pasta, nome_arquivo, conteudo):
    """Salva conteúdo em arquivo JSON."""
    try:
        with open(os.path.join(pasta, nome_arquivo), 'w', encoding='utf-8') as arquivo:
            json.dump(conteudo, arquivo, ensure_ascii=False, indent=4)
        print(f"Arquivo salvo em: {pasta}/{nome_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")

def baixar_imagem(url, nome_arquivo):
    """Baixa imagem da URL e salva localmente."""
    try:
        resposta = requests.get(url, stream=True)
        if resposta.status_code == 200:
            with open(os.path.join(PASTAS['SaidaImg'], f"{nome_arquivo}.png"), 'wb') as arquivo:
                for chunk in resposta.iter_content(1024):
                    arquivo.write(chunk)
            print(f"Imagem salva: {nome_arquivo}")
        else:
            print(f"Erro ao baixar imagem: {resposta.status_code}")
    except Exception as e:
        print(f"Erro ao salvar imagem: {e}")

class SessaoCNA:
    """Classe para interagir com o sistema CNA."""
    def __init__(self, nome_advo):
        self.sessao = requests.Session()
        self.nome_advo = nome_advo

    def enviar_requisicao(self):
        """Realiza a requisição e salva os dados do advogado."""
        payload = {"NomeAdvo": self.nome_advo, "UF": "SP", "IsMobile": "false"}
        try:
            resposta = self.sessao.post(BASE_URL + 'Home/Search', json=payload, headers={'Content-Type': 'application/json'})
            if resposta.status_code == 200:
                dados = resposta.json()
                if dados:
                    timestamp = datetime.now().strftime("%d-%m-%Y")
                    salvar_em_arquivo(PASTAS['OAB'], f"Advogado_{self.nome_advo.replace(' ', '_')}_data_{timestamp}.json", dados)
                    print(f"Dados do advogado {self.nome_advo} obtidos com sucesso.")
                else:
                    print(f"Nenhum dado encontrado para {self.nome_advo}")
            else:
                print(f"Erro na requisição: {resposta.status_code}")
        except Exception as e:
            print(f"Erro ao realizar requisição: {e}")

def iniciar_driver():
    """Inicia o driver do Selenium com configurações."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def processar_arquivos_selenium():
    """Processa arquivos JSON e coleta informações com Selenium."""
    driver = iniciar_driver()
    for arquivo in os.listdir(PASTAS['Detalhes']):
        if arquivo.endswith(".json"):
            caminho_arquivo = os.path.join(PASTAS['Detalhes'], arquivo)
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            sociedades = dados.get("Data", {}).get("Sociedades", [])
            if not sociedades:
                print(f"Nenhuma sociedade encontrada no arquivo: {arquivo}")
                resultado = {"erro": "Nenhuma sociedade encontrada", "url": None}
            else:
                url_parcial = sociedades[0].get("Url")
                if url_parcial:
                    url_completa = BASE_URL + url_parcial
                    print(f"Acessando a URL: {url_completa}")
                    try:
                        driver.get(url_completa)
                        time.sleep(3)
                        elemento = driver.find_element(By.XPATH, '//*[@id="bodyContent"]/div[3]/div/div/div[2]/div[6]')
                        conteudo_elemento = elemento.text
                        resultado = {"conteudo_coletado": conteudo_elemento, "url": url_completa}
                        print(f"Conteúdo coletado: {conteudo_elemento}")
                    except Exception as e:
                        print(f"Erro ao acessar a URL ou coletar o elemento: {e}")
                        resultado = {"erro": str(e), "url": url_completa}
                else:
                    print(f"URL não encontrada no arquivo: {arquivo}")
                    resultado = {"erro": "URL não encontrada", "url": None}
            
            caminho_saida = os.path.join(PASTAS['SaidaSelenium'], arquivo)
            with open(caminho_saida, 'w', encoding='utf-8') as f_out:
                json.dump(resultado, f_out, ensure_ascii=False, indent=4)
            print(f"Arquivo processado e salvo em: {caminho_saida}")
    driver.quit()

def main():
    NomeAdvo = input("Digite o nome do Advogado: ").strip()
    sessao_cna = SessaoCNA(NomeAdvo)
    sessao_cna.enviar_requisicao()
    processar_arquivos_selenium()

if __name__ == "__main__":
    main()
