import os
import json
import requests
from datetime import datetime

BASE_URL = 'https://cna.oab.org.br/'
PASTA_OAB = 'output_CNA_OAB'
PASTA_DETALHES_OAB = 'resultados_CNA_detalhes'

# Garantindo a criação das pastas necessárias
os.makedirs(PASTA_OAB, exist_ok=True)
os.makedirs(PASTA_DETALHES_OAB, exist_ok=True)

def salvar_em_arquivo(pasta, nome_arquivo, conteudo):
    """Função utilitária para salvar dados em arquivo JSON."""
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, nome_arquivo)
    try:
        with open(caminho, 'w', encoding='utf-8') as arquivo:
            json.dump(conteudo, arquivo, ensure_ascii=False, indent=4)
        print(f"Arquivo salvo em: {caminho}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo: {e}")

class SessaoCNA:
    def __init__(self, NomeAdvo: str):
        self.sessao = requests.Session()
        self.NomeAdvo = NomeAdvo

    def enviar_requisicao(self):
        """Envia uma requisição POST para buscar informações do advogado."""
        payload = {
            "__RequestVerificationToken": "",
            "IsMobile": "false",
            "NomeAdvo": self.NomeAdvo,
            "Insc": "",
            "Uf": "",
            "TipoInsc": "",
        }
        try:
            resposta = self.sessao.post(BASE_URL + 'Home/Search', json=payload, headers={'Content-Type': 'application/json'})
            if resposta.status_code == 200:
                documentos = resposta.json()
                if documentos:
                    timestamp = datetime.now().strftime("%d-%m-%Y")
                    nome_arquivo = f"advogado_{self.NomeAdvo.replace(' ', '_')}_{timestamp}.json"
                    salvar_em_arquivo(PASTA_OAB, nome_arquivo, documentos)  # Passando o conteúdo corretamente
                    print(f"Dados obtidos com sucesso para o advogado: {self.NomeAdvo}")
                else:
                    print(f"Nenhum dado encontrado para o advogado: {self.NomeAdvo}")
            else:
                print(f"Erro na requisição: Status {resposta.status_code}")
        except Exception as e:
            print(f"Erro ao realizar a requisição: {e}")

class DetalhesCNA:
    def __init__(self):
        self.sessao = requests.Session()

    def processar_arquivo_output(self):
        """Processa os arquivos gerados pela SessaoCNA e busca os detalhes adicionais."""
        try:
            arquivos = [f for f in os.listdir(PASTA_OAB) if f.endswith('.json')]
            if not arquivos:
                print(f"Nenhum arquivo JSON encontrado na pasta {PASTA_OAB}.")
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
        """Busca detalhes adicionais de um advogado e salva em um arquivo."""
        try:
            resposta = self.sessao.post(url, headers={'Content-Type': 'application/json'})
            if resposta.status_code == 200:
                detalhes = resposta.json()
                timestamp = datetime.now().strftime("%d-%m-%Y")
                nome_arquivo = f"detalhes_{nome_advogado.replace(' ', '_')}_{timestamp}.json"
                salvar_em_arquivo(PASTA_DETALHES_OAB, nome_arquivo, detalhes)  # Passando o conteúdo corretamente
                print(f"Detalhes salvos para URL: {url}")
            else:
                print(f"Erro ao acessar detalhes: Status {resposta.status_code} para URL: {url}")
        except Exception as e:
            print(f"Erro ao buscar detalhes para URL: {e}")

def main():
    NomeAdvo = input("Digite o nome do advogado: ")
    
    sessao_cna = SessaoCNA(NomeAdvo)
    sessao_cna.enviar_requisicao()

    detalhes_cna = DetalhesCNA()
    detalhes_cna.processar_arquivo_output()

if __name__ == "__main__":
    main()
