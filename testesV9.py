import os
import json
import requests
from datetime import datetime

URL_CNA_OAB = 'https://cna.oab.org.br/Home/Search'
PASTA_OAB = 'output_oab'

class SessaoCNA:
    def __init__(self, NomeAdvo: str):
        self.sessao = requests.Session()
        self.NomeAdvo = NomeAdvo

    def salvar_em_arquivo(self, pasta, nome_arquivo, conteudo):
        """Salva os resultados da busca em um arquivo JSON."""
        os.makedirs(pasta, exist_ok=True)
        caminho = os.path.join(pasta, nome_arquivo)
        try:
            with open(caminho, 'w', encoding='utf-8') as arquivo:
                json.dump(conteudo, arquivo, ensure_ascii=False, indent=4)
            print(f"Arquivo salvo em: {caminho}")
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {e}")

    def enviar_requisicao(self):
        """Envia a requisição POST para buscar informações do advogado."""
        payload = {
            "__RequestVerificationToken": "",
            "IsMobile": "false",
            "NomeAdvo": self.NomeAdvo,
            "Insc": "",
            "Uf": "",
            "TipoInsc": "",
        }

        try:
            resposta = self.sessao.post(URL_CNA_OAB, json=payload, headers={'Content-Type': 'application/json'})
            if resposta.status_code == 200:
                documentos = resposta.json()
                if documentos:
                    timestamp = datetime.now().strftime("%d-%m-%Y")
                    nome_arquivo = f"advogado_{self.NomeAdvo.replace(' ', '_')}_{timestamp}.json"
                    self.salvar_em_arquivo(PASTA_OAB, nome_arquivo, documentos)
                    print(f"Dados obtidos com sucesso para o advogado: {self.NomeAdvo}")
                else:
                    print(f"Nenhum dado encontrado para o advogado: {self.NomeAdvo}")
            else:
                print(f"Erro na requisição: Status {resposta.status_code}")
        except Exception as e:
            print(f"Erro ao realizar a requisição: {e}")

if __name__ == "__main__":
    NomeAdvo = input("Digite o nome do advogado: ")
    sessao = SessaoCNA(NomeAdvo)
    sessao.enviar_requisicao()
