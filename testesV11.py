import os
import json
import requests
from datetime import datetime

BASE_URL = 'https://cna.oab.org.br/'
PASTA_OAB = 'output_CNA_OAB'
PASTA_DETALHES_OAB = 'resultados_CNA_detalhes'
PASTA_SAIDA = 'detalhes_CNA_processados'
os.makedirs(PASTA_OAB, exist_ok=True)
os.makedirs(PASTA_DETALHES_OAB, exist_ok=True)
os.makedirs(PASTA_SAIDA, exist_ok=True)

def salvar_em_arquivo(pasta, nome_arquivo, conteudo):
    """Salva o conteúdo em um arquivo JSON na pasta especificada."""
    caminho = os.path.join(pasta, nome_arquivo)
    try:
        with open(caminho, 'w', encoding='utf-8') as arquivo:
            json.dump(conteudo, arquivo, ensure_ascii=False, indent=4)
        print(f"Arquivo salvo em: {caminho}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo em: {e}")

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
                    nome_arquivo = f"Advogado_{self.NomeAdvo.replace(' ','_')}_data_{timestamp}.json"
                    salvar_em_arquivo(PASTA_OAB, nome_arquivo, documentos)
                    print(f"Dados obtidos com sucesso para advogado: {self.NomeAdvo}")
                else:
                    print(f"Nenhum dado encontrado para o advogado: {self.NomeAdvo}")
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
                    nome = item.get('Nome')
                    if detail_url:
                        url_completa = BASE_URL + detail_url
                        self.buscar_detalhes(url_completa, nome)
                        self.atualizar_detalhes(nome, item)
        except Exception as e:
            print(f"Erro ao processar arquivo JSON: {e}")

    def buscar_detalhes(self, url, nome_advogado):
        """Busca detalhes adicionais para um advogado através da URL fornecida."""
        try:
            resposta = self.sessao.post(url, headers={'Content-Type': 'application/json'})
            if resposta.status_code == 200:
                detalhes = resposta.json()
                timestamp = datetime.now().strftime("%d-%m-%Y")
                nome_arquivo = f"detalhes_{nome_advogado.replace(' ','_')}_data_{timestamp}.json"
                salvar_em_arquivo(PASTA_DETALHES_OAB, nome_arquivo, detalhes)
                print(f"Detalhes salvos em URL: {url}")
            else:
                print(f"Erro ao acessar detalhes: Status {resposta.status_code} para URL {url}")
        except Exception as e:
            print(f"Erro ao buscar detalhes para URL: {e}")

    def atualizar_detalhes(self, nome_advogado, dados_item):
        """Atualiza o arquivo final com as informações do advogado se o nome coincidir."""
        try:
            arquivos_resultado = [f for f in os.listdir(PASTA_DETALHES_OAB) if f.endswith('.json')]
            for arquivo_resultado in arquivos_resultado:
                if nome_advogado.replace(" ", "_") in arquivo_resultado:
                    caminho_arquivo_resultado = os.path.join(PASTA_DETALHES_OAB, arquivo_resultado)
                    with open(caminho_arquivo_resultado, 'r', encoding='utf-8') as arquivo:
                        dados_resultado = json.load(arquivo)
                
                    if dados_item.get("Nome"):
                        dados_resultado["Data"]["Nome"] = dados_item.get("Nome")
                    if dados_item.get("DetailUrl"):
                        dados_resultado["Data"]["DetailUrl"] = dados_item.get("DetailUrl")
                    salvar_em_arquivo(PASTA_DETALHES_OAB, arquivo_resultado, dados_resultado)
                    print(f"Arquivo {arquivo_resultado} atualizado com sucesso.")
        except Exception as e:
            print(f"Erro ao atualizar detalhes: {e}")

def processar_arquivo_json(caminho_arquivo):
    """Processa um arquivo JSON e extrai informações relevantes."""
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
        insc = None
        detail_url = None

        if dados.get("Data") and dados["Data"].get("Sociedades"):
            sociedade = dados["Data"]["Sociedades"][0]
            insc = sociedade.get("Inscricao")
        if dados.get("Data") and dados["Data"].get("DetailUrl"):
            detail_url = dados["Data"]["DetailUrl"]

        if detail_url:
            url_completa = BASE_URL + detail_url
        else:
            url_completa = None

        novo_json = {
            "Inscricao": insc,
            "DetailUrl": detail_url,
            "URL": url_completa
        }
        return novo_json

def salvar_novo_arquivo(nome_arquivo, dados):
    """Salva o novo arquivo JSON com as informações processadas."""
    caminho_novo_arquivo = os.path.join(PASTA_SAIDA, nome_arquivo)
    with open(caminho_novo_arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def atualizar_arquivo_json():
    """Atualiza os arquivos JSON na pasta 'resultados_CNA_detalhes' com os dados dos arquivos na pasta 'detalhes_CNA_processados'."""
    try:
        arquivos_processados = [f for f in os.listdir(PASTA_SAIDA) if f.endswith('.json')]
        if not arquivos_processados:
            print(f"Nenhum arquivo JSON encontrado na pasta {PASTA_SAIDA}")
            return
        
        for arquivo in arquivos_processados:
            caminho_arquivo_processado = os.path.join(PASTA_SAIDA, arquivo)
            caminho_arquivo_resultado = os.path.join(PASTA_DETALHES_OAB, arquivo)
            
            if os.path.exists(caminho_arquivo_resultado):
                with open(caminho_arquivo_processado, 'r', encoding='utf-8') as arquivo_processado:
                    dados_processados = json.load(arquivo_processado)
                
                with open(caminho_arquivo_resultado, 'r', encoding='utf-8') as arquivo_resultado:
                    dados_resultado = json.load(arquivo_resultado)
                
                if dados_processados.get("URL"):
                    dados_resultado["Data"]["URL"] = dados_processados["URL"]
                if dados_processados.get("Inscricao"):
                    dados_resultado["Data"]["Inscricao"] = dados_processados["Inscricao"]
                
                salvar_em_arquivo(PASTA_DETALHES_OAB, arquivo, dados_resultado)
                print(f"Arquivo {arquivo} atualizado com sucesso.")
            else:
                print(f"Arquivo {arquivo} não encontrado na pasta de resultados.")
    except Exception as e:
        print(f"Erro ao atualizar os arquivos JSON: {e}")

def main():
    NomeAdvo = input("Digite o nome do Advogado: ").strip()
    sessao_cna = SessaoCNA(NomeAdvo)
    sessao_cna.enviar_requisicao()
    detalhes_cna = DetalhesCNA()
    detalhes_cna.processar_arquivo_output()
    for nome_arquivo in os.listdir(PASTA_DETALHES_OAB):
        if nome_arquivo.endswith(".json"):
            caminho_arquivo = os.path.join(PASTA_DETALHES_OAB, nome_arquivo)
            novo_dado = processar_arquivo_json(caminho_arquivo)
            salvar_novo_arquivo(nome_arquivo, novo_dado)
            print(f"Processamento de {nome_arquivo} concluído")
    
    atualizar_arquivo_json()

if __name__ == "__main__":
    main()
