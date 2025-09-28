from src.classifier import classify_with_keywords

# Exemplos de frases para testar a classificação
testes = [
    # Frases improdutivas
    ("Muito obrigado pelo seu trabalho, ficou excelente!", "Improdutivo"),
    ("Recebi sua mensagem, obrigado.", "Improdutivo"),
    ("Entendido, tenha um bom dia!", "Improdutivo"),
    ("Perfeito, muito bom trabalho.", "Improdutivo"),
    ("Só para confirmar que recebi o documento.", "Improdutivo"),
    ("Mensagem recebida, agradeço a atenção.", "Improdutivo"),
    ("Ciente do comunicado, obrigado.", "Improdutivo"),
    ("Beleza, combinado então.", "Improdutivo"),
    
    # Frases produtivas
    ("Preciso que você me envie o relatório até amanhã.", "Produtivo"),
    ("Quando podemos marcar uma reunião para discutir o projeto?", "Produtivo"),
    ("Por favor, verifique se os dados estão corretos.", "Produtivo"),
    ("Estou com um problema no sistema, você pode me ajudar?", "Produtivo"),
    ("Gostaria de solicitar informações sobre o novo produto.", "Produtivo"),
    ("Não consigo acessar o sistema, o que devo fazer?", "Produtivo"),
    ("Seria possível adiantar a entrega para sexta-feira?", "Produtivo"),
    ("Precisamos organizar os documentos para a auditoria.", "Produtivo"),
    
    # Casos ambíguos ou desafiadores
    ("Obrigado pelo relatório. Preciso que você atualize os números da última seção.", "Produtivo"),
    ("Recebi o documento, mas está faltando a assinatura do diretor.", "Produtivo"),
    ("Excelente trabalho! Poderia compartilhar sua metodologia com a equipe?", "Produtivo"),
    ("Agradeço o envio. Quando teremos a versão final?", "Produtivo"),
    ("Entendi sua explicação, mas ainda tenho dúvidas sobre o processo.", "Produtivo"),
    ("Parabéns pela promoção! Vamos marcar um almoço para comemorar?", "Produtivo"),
    ("Obrigado pela ajuda, funcionou perfeitamente.", "Improdutivo"),
    ("Recebi sua solicitação e já providenciei o que foi pedido.", "Improdutivo"),
]

def test_classificacao():
    print("\nTESTANDO CLASSIFICAÇÃO DE TEXTOS\n" + "-"*30)
    acertos = 0
    total = len(testes)
    
    for texto, esperado in testes:
        categoria, confianca = classify_with_keywords(texto)
        acerto = categoria == esperado
        status = "✓" if acerto else "✗"
        
        if acerto:
            acertos += 1
        
        print(f"{status} [{confianca:.2f}] {categoria:11} | {texto[:50]}{'...' if len(texto) > 50 else ''}")
    
    taxa_acerto = (acertos / total) * 100
    print(f"\nResultado: {acertos}/{total} acertos ({taxa_acerto:.1f}%)")

if __name__ == "__main__":
    test_classificacao()