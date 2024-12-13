import os
import json
import requests
from datetime import datetime

BASE_URL = 'https://cna.oab.org.br/'
PASTA_OAB = 'output_CNA_OAB'
PASTA_DETALHES_OAB = 'resultados_CNA_detalhes'
PASTA_SAIDA = 'detalhes_CNA_processados'
PASTA_JSON_SEPARADOS = 'json_separados'
os.makedirs(PASTA_OAB, exist_ok=True)
os.makedirs(PASTA_DETALHES_OAB, exist_ok=True)
os.makedirs(PASTA_SAIDA, exist_ok=True)
os.makedirs(PASTA_JSON_SEPARADOS, exist_ok=True)

def salvar_em_arquivo(pasta, nome_arquivo, conteudo):
    """Salva o conteúdo em um arquivo JSON na pasta especificada."""
    caminho = os.path.join(pasta, nome_arquivo)
    try:
        with open(caminho, 'w', encoding='utf-8') as arquivo:
            json.dump(conteudo, arquivo, ensure_ascii=False, indent=4)
        print(f"Arquivo salvo em: {caminho}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo: {e}")

def baixar_imagem(url, nome_arquivo):
    """Baixa uma imagem de uma URL e a salva localmente."""
    try:
        resposta = requests.get(url, stream=True)
        if resposta.status_code == 200:
            caminho_imagem = os.path.join(PASTA_SAIDA, f"{nome_arquivo}.png")
            with open(caminho_imagem, 'wb') as arquivo:
                for chunk in resposta.iter_content(1024):
                    arquivo.write(chunk)
                print(f"Imagem baixada e salva em: {caminho_imagem}")
        else:
            print(f"Erro ao baixar a imagem: Status {resposta.status_code} para URL {url}")
    except Exception as e:
        print(f"Erro ao salvar a imagem: {e}")

class SessaoCNA:
    """
    Classe para realizar requisições ao sistema CNA.
    """
    def __init__(self, NomeAdvo: str):
        self.sessao = requests.Session()
        self.NomeAdvo = NomeAdvo

    def enviar_requisicao(self):
        """Envia uma requisição para buscar os dados do advogado."""
        payload = {
            "__RequestVerificationToken": "",
            "IsMobile": "false",
            "NomeAdvo": self.NomeAdvo,
            "Inscricao": "",
            "Uf": "",
            "TipoInsc": "",
        }
        try:
            resposta = self.sessao.post(BASE_URL + 'Home/Search', json=payload, headers={'Content-Type': 'application/json'})
            if resposta.status_code == 200:
                documentos = resposta.json()
                if documentos:
                    timestamp = datetime.now().strftime("%d-%m-%Y")
                    nome_arquivo = f"Advogado_{self.NomeAdvo.replace(' ',('_'))}_data_{timestamp}.json"
                    salvar_em_arquivo(PASTA_OAB, nome_arquivo, documentos)
                    print(f"Dados obtidos com sucesso para o advogado: {self.NomeAdvo}")
                else:
                    print(f"Nenhum dado encontrado para o Advogado: {self.NomeAdvo}")
            else:
                print(f"Erro na requisição: Status {resposta.status_code}")
        except Exception as e:
            print(f"Erro ao realizar a requisição: {e}")

class DetalhesCNA:
    """
    Classe para buscar os detalhes adicionais dos advogados.
    """
    def __init__(self):
        self.sessao = requests.Session()

    def processar_arquivo_output(self):
        """Processa os arquivos da pasta 'output_CNA_OAB' e coleta detalhes adicionais."""
        try:
            arquivos = [f for f in os.listdir(PASTA_OAB) if f.endswith('.json')]
            if not arquivos:
                print(f"Nenhum arquivo JSON encontrado na pasta {PASTA_OAB}")
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
            print(f"Erro ao processar arquivo JSON: {e}")

    def buscar_detalhes(self, url, nome_advogado):
        """Busca detalhes adicionais para um advogado através da URL fornecida."""
        try:
            resposta = self.sessao.post(url, headers={'Content-Type': 'application/json'})
            if resposta.status_code == 200:
                detalhes = resposta.json()
                timestamp = datetime.now().strftime("%d-%m-%Y")
                nome_arquivo = f"detalhes_{nome_advogado.replace(' ', '_')}_data_{timestamp}.json"
                salvar_em_arquivo(PASTA_DETALHES_OAB, nome_arquivo, detalhes)
                print(f"Detalhes salvos em URL: {url}")
            else:
                print(f"Erro ao acessar detalhes: Status {resposta.status_code} para URL {url}")
        except Exception as e:
            print(f"Erro ao buscar detalhes para URL: {e}")

def coletar_url_completa(nome_arquivo):
    """Coleta a URL de detalhes e passa para buscar_detalhes."""
    caminho_detalhes = os.path.join(PASTA_SAIDA, nome_arquivo)
    if not os.path.exists(caminho_detalhes):
        print(f"Arquivo correspondente não encontrado na pasta {PASTA_SAIDA}: {nome_arquivo}")
        return None

    try:
        with open(caminho_detalhes, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        url_completa = dados.get('URL')
        if url_completa:
            nome_advogado = dados.get('Nome', 'desconhecido')
            detalhes_cna = DetalhesCNA()
            detalhes_cna.buscar_detalhes(url_completa, nome_advogado)
    except Exception as e:
        print(f"Erro ao ler o arquivo {nome_arquivo}: {e}")

def separar_itens_e_adicionar_url():
    """Lê os arquivos JSON da pasta output_CNA_OAB, separa os itens em arquivos individuais e adiciona o campo URL."""
    arquivos = [f for f in os.listdir(PASTA_OAB) if f.endswith('.json')]

    if not arquivos:
        print(f"Nenhum arquivo JSON encontrado na pasta {PASTA_OAB}")
        return

    for arquivo in arquivos:
        caminho_arquivo = os.path.join(PASTA_OAB, arquivo)

        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            for idx, item in enumerate(dados.get('Data', [])):
                nome_arquivo_individual = f"{os.path.splitext(arquivo)[0]}_item_{idx + 1}.json"
                url_completa = coletar_url_completa(nome_arquivo_individual)
                if url_completa:
                    item['URL'] = url_completa

                caminho_saida = os.path.join(PASTA_JSON_SEPARADOS, nome_arquivo_individual)
                with open(caminho_saida, 'w', encoding='utf-8') as arquivo_individual:
                    json.dump(item, arquivo_individual, ensure_ascii=False, indent=4)

                print(f"Item {idx + 1} salvo em {caminho_saida}")

        except Exception as e:
            print(f"Erro ao processar o arquivo {arquivo}: {e}")

def main():
    NomeAdvo = input("Digite o nome do Advogado: ").strip()
    sessao_cna = SessaoCNA(NomeAdvo)
    sessao_cna.enviar_requisicao()

    detalhes_cna = DetalhesCNA()
    detalhes_cna.processar_arquivo_output()

    separar_itens_e_adicionar_url()

if __name__ == "__main__":
    main()
