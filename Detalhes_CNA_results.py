import os
import json
import requests
from datetime import datetime

BASE_URL = 'https://cna.oab.org.br/'
PASTA_OAB = 'output_CNA_OAB'
PASTA_DETALHES_OAB = 'resultados_CNA_detalhes'

class DetalhesCNA:
    """
    

    """
    def __init__(self, NomeAdvo: str):
        self.sessao = requests.Session()
        self.NomeAdvo = NomeAdvo

    def salvar_em_arquivo(self, pasta, nome_arquivo, conteudo):
        """  """
        os.makedirs(pasta, exist_ok=True)
        caminho = os.path.join(pasta, nome_arquivo)
        try:
            with open(caminho, 'w', encoding='utf-8') as arquivo:
                json.dump(conteudo, arquivo, ensure_ascii=False, indent=4)
                print(f"Arquivo salvo em: {caminho}")
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {e}")
        
    def processar_arquivo_output(self):
        """  """
        try:
            arquivos = [f for f in os.listdir(PASTA_OAB) if f.endswith('.json')]
            if not arquivos:
                print(f"Nenhum arquivo JSON encotrado na pasta output_oab.")
                return
            for arquivo in arquivos:
                caminho_arquivo = os.path.join(PASTA_OAB, arquivo)
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                for item in dados.get('Data', []):
                    detail_url = item.get('DetailUrl')
                    if detail_url:
                        url_completa = BASE_URL + detail_url
                        self.buscar_detalhes(url_completa, item.get('Nome', 'desconhecido'))
        except Exception as e:
            print(f"Erro ao processar arquivos: {e}")

    def buscar_detalhes(self, url, nome_advogado):
        """  """
        try:
            resposta = self.sessao.post(url, headers={'Content-Type': 'appication/json'})
            if resposta.status_code == 200:
                detalhes = resposta.json()
                timestamp = datetime.now().strftime("%d-%m-%Y")
                nome_arquivo = f"detalhes_{nome_advogado}_data_{timestamp}.json"
                self.salvar_em_arquivo(PASTA_DETALHES_OAB, nome_arquivo, detalhes)
                print(f"Detalhes salvos para URL: {url}")
            else:
                print(f"Erro ao acessar detalhes: Status{resposta.status_code} para URL: {url}")
        except Exception as e:
            print(f"Erro ao buscar detalhes para URL: {e}")

if __name__ == "__main__":
    NomeAdvo = input("Digite o nome do Advogado: ")
    sessao = DetalhesCNA(NomeAdvo)
    sessao.processar_arquivo_output()