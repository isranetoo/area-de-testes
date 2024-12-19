def limpar_pastas():
    """Remove as pastas especificadas após a execução do programa."""
    try:
        pastas_para_remover = ['resultados_CNA_detalhes', 'output_CNA_OAB', 'detalhes_CNA_processados']
        for pasta in pastas_para_remover:
            caminho_completo = os.path.join(os.getcwd(), pasta)
            if os.path.exists(caminho_completo):
                for root, dirs, files in os.walk(caminho_completo, topdown=False):
                    for file in files:
                        os.remove(os.path.join(root, file))
                    for dir in dirs:
                        os.rmdir(os.path.join(root, dir))
                os.rmdir(caminho_completo)
                print(f"Pasta '{pasta}' removida com sucesso.")
            else:
                print(f"Pasta '{pasta}' não encontrada.")
    except Exception as e:
        print(f"Erro ao remover pastas: {e}")


def main():
    NomeAdvo = input("Digite o nome do Advogado: ").strip()
    sessao_cna = SessaoCNA(NomeAdvo)
    sessao_cna.enviar_requisicao()
    detalhes_cna = DetalhesCNA()
    detalhes_cna.processar_arquivos()
    for nome_arquivo in os.listdir(PASTAS['Detalhes']):
        if nome_arquivo.endswith(".json"):
            novo_dado = processar_arquivo_json(os.path.join(PASTAS['Detalhes'], nome_arquivo))
            salvar_em_arquivo(PASTAS['Saida'], nome_arquivo, novo_dado)
            print(f"Processamento de {nome_arquivo} concluído.")
    atualizar_arquivo_json()
    executar_script('corte_img.py')
    executar_script('separador.py')
    executar_script('CNSA_OAB_selenium.py')
    executar_script('compilador.py')
    executar_script('numero_e_resultado.py')
    limpar_pastas()

if __name__ == "__main__":
    main()
