import pandas as pd

data = pd.read_json('resultado_combinado.json')

data.to_excel('resultado_combinado.xlsx', index=False)

print("Dados convertidos com sucesso!")
