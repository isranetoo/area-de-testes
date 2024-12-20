import pandas as pd

data = pd.read_json('resultado_combinado.json')

data.to_excel('resultado_combinado.xlsx', index=False)

print("Dados convertidos com sucesso!")


def coleta_sociedade(self, url):
    try:
        resposta = self.sessao.get(url)
        if resposta.status_code == 200:
            return resposta.json()
        else:
            print(f"Erro ao coletar sociedade: {resposta.status_code}")
            return {}
    except Exception as e:
        print(f"Erro ao coletar sociedade: {e}")
        return {}
