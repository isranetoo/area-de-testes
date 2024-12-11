import os
import json
import requests
from datetime import datetime

BASE_URL = 'https://cna.oab.org.br/'
PASTA_OAB = 'output_oab'
PASTA_RESULTADOS = 'resultados_detalhes'

class SessaoCNA:
    """
        Classe para manipular a busca de informações de advogados e salvar os detalhes obtidos.

        Args: 
            NomeAdvo: Nome do advogado para a pesquisa inicial.
    """
    def __init__(self, NomeAdvo: str):
        self.sessao = requests.Session()
        self.NomeAdvo = NomeAdvo

    def salvar_em_arquivo(self, pasta, nome_arquivo, conteudo):
        """Salva os resultados em um arquivo JSON."""
        os.makedirs(pasta, exist_ok=True)
        caminho = os.path.join(pasta, nome_arquivo)
        try:
            with open(caminho, 'w', encoding='utf-8') as arquivo:
                json.dump(conteudo, arquivo, ensure_ascii=False, indent=4)
            print(f"Arquivo salvo em: {caminho}")
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {e}")

    def processar_arquivos_output(self):
        """Processa os arquivos na pasta de output, coletando informações do campo DetailUrl."""
        try:
            arquivos = [f for f in os.listdir(PASTA_OAB) if f.endswith('.json')]
            if not arquivos:
                print("Nenhum arquivo JSON encontrado na pasta output_oab.")
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
        """Envia requisição POST para a URL de detalhes e salva a resposta."""
        try:
            resposta = self.sessao.post(url, headers={'Content-Type': 'application/json'})
            if resposta.status_code == 200:
                detalhes = resposta.json()
                timestamp = datetime.now().strftime("%d-%m-%Y")
                nome_arquivo = f"detalhes_{nome_advogado.replace(' ', '_')}_{timestamp}.json"
                self.salvar_em_arquivo(PASTA_RESULTADOS, nome_arquivo, detalhes)
                print(f"Detalhes salvos para URL: {url}")
            else:
                print(f"Erro ao acessar detalhes: Status {resposta.status_code} para URL: {url}")
        except Exception as e:
            print(f"Erro ao buscar detalhes para URL {url}: {e}")

if __name__ == "__main__":
    NomeAdvo = input("Digite o nome do advogado: ")
    sessao = SessaoCNA(NomeAdvo)
    sessao.processar_arquivos_output()
