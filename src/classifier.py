from typing import Tuple, Literal, Optional
from src.config import OPENAI_API_KEY, OPENAI_MODEL

try:
    from openai import OpenAI
    _openai_available = True
except Exception:
    _openai_available = False

# Prompt especializado para classificação
_CLASSIFICATION_PROMPT = """
Você é um especialista em classificação de emails. Analise o texto do email a seguir e classifique-o em uma das duas categorias:

**Produtivo**: Emails que requerem ação, resposta ou acompanhamento
- Exemplos: perguntas, solicitações, pedidos de informação, problemas técnicos, agendamentos

**Improdutivo**: Emails apenas informativos ou de cortesia que não requerem ação
- Exemplos: agradecimentos, felicitações, confirmações simples, mensagens de cortesia

IMPORTANTE: Responda EXATAMENTE no formato:
CATEGORIA: [Produtivo ou Improdutivo]
CONFIANÇA: [número de 0 a 1]
JUSTIFICATIVA: [breve explicação]
"""

_REPLY_PROMPT = """
Você é um assistente especializado em gerar respostas para emails. 

Para emails PRODUTIVOS: Gere uma resposta que reconheça a solicitação e indique próximos passos.
Para emails IMPRODUTIVOS: Gere uma resposta educada de agradecimento sem criar expectativas de ação.

Mantenha as respostas curtas (2-4 frases) e profissionais.
"""

def classify_text(text: str) -> Tuple[Literal['Produtivo', 'Improdutivo'], float]:
    """
    Classifica texto usando OpenAI
    
    Args:
        text: Texto do email para classificar
        
    Returns:
        Tuple com (categoria, confiança)
    """
    if not _openai_available or not OPENAI_API_KEY:
        # Fallback simples se OpenAI não estiver disponível
        return classify_with_keywords(text)
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": _CLASSIFICATION_PROMPT},
                {"role": "user", "content": f"Email para classificar:\n\n{text}"}
            ],
            temperature=0.1,  # Baixa temperatura para consistência
            max_tokens=150
        )
        
        result = response.choices[0].message.content.strip()
        print(f"DEBUG: Resposta da OpenAI para classificação: {result}")
        
        # Parse da resposta
        category, confidence = parse_classification_response(result)
        
        return category, confidence
        
    except Exception as e:
        print(f"Erro na classificação OpenAI: {e}")
        # Fallback para classificação por palavras-chave
        return classify_with_keywords(text)

def parse_classification_response(response: str) -> Tuple[Literal['Produtivo', 'Improdutivo'], float]:
    """
    Extrai categoria e confiança da resposta da OpenAI
    """
    lines = response.split('\n')
    category = 'Produtivo'  # Default
    confidence = 0.5  # Default
    
    for line in lines:
        line = line.strip()
        if line.startswith('CATEGORIA:'):
            cat_text = line.split(':', 1)[1].strip()
            if 'Improdutivo' in cat_text:
                category = 'Improdutivo'
            else:
                category = 'Produtivo'
                
        elif line.startswith('CONFIANÇA:'):
            try:
                conf_text = line.split(':', 1)[1].strip()
                confidence = float(conf_text)
            except:
                confidence = 0.8  # Default alto se não conseguir parsear
    
    return category, confidence

def classify_with_keywords(text: str) -> Tuple[Literal['Produtivo', 'Improdutivo'], float]:
    """
    Classificação de fallback usando palavras-chave e análise de contexto
    """
    text_lower = text.lower()
    words = text_lower.split()
    
    # Indicadores de mensagem improdutiva (cortesia, agradecimentos, confirmações)
    improdutivo_indicators = [
        # Agradecimentos
        'obrigado', 'obrigada', 'agradecimento', 'agradeço', 'grato', 'grata',
        'valeu', 'thanks', 'thank you', 'gracias',
        
        # Felicitações
        'parabéns', 'felicitações', 'congratulações', 'meus parabéns', 'parabenizo',
        'congratulations', 'felicito',
        
        # Elogios
        'ótimo', 'excelente', 'perfeito', 'maravilhoso', 'bom trabalho', 'incrível',
        'fantástico', 'espetacular', 'sensacional', 'excepcional', 'admirável',
        'impressionante', 'notável', 'extraordinário',
        
        # Saudações e despedidas
        'tenha um', 'bom dia', 'boa tarde', 'boa noite', 'abraços', 'abraço',
        'atenciosamente', 'cordialmente', 'saudações', 'até mais', 'até logo',
        'até breve', 'até a próxima', 'até amanhã',
        
        # Confirmações simples
        'recebi', 'recebido', 'confirmado', 'ciente', 'entendido', 'compreendido',
        'ok', 'beleza', 'combinado', 'fechado', 'perfeito', 'tudo bem',
        
        # Expressões de cortesia
        'gentileza', 'atenção', 'disponibilidade', 'presteza', 'cordialidade'
    ]
    
    # Indicadores de mensagem produtiva (ação necessária, perguntas, solicitações)
    produtivo_indicators = [
        # Necessidade/Urgência
        'preciso', 'necessito', 'necessário', 'urgente', 'importante', 'crucial',
        'essencial', 'fundamental', 'imprescindível', 'prioritário',
        
        # Perguntas
        'quando', 'como', 'onde', 'por que', 'qual', 'quais', 'quem', 'quanto',
        'quantos', 'quantas', 'aonde', 'o que', 'será que', 'poderia me informar',
        
        # Solicitações
        'por favor', 'poderia', 'gostaria', 'solicito', 'pedido', 'requisição',
        'favor', 'peço', 'requeiro', 'demando', 'exijo', 'solicito', 'requisito',
        
        # Problemas
        'problema', 'erro', 'falha', 'bug', 'defeito', 'dificuldade', 'obstáculo',
        'empecilho', 'complicação', 'transtorno', 'inconveniente', 'impasse',
        
        # Ajuda
        'ajuda', 'suporte', 'auxílio', 'assistência', 'apoio', 'socorro', 'amparo',
        
        # Ações futuras
        'precisa ser feito', 'deve ser realizado', 'necessita ser', 'aguardo',
        'espero', 'aguardando', 'esperando', 'pendente', 'em aberto',
        
        # Verbos de ação no imperativo ou futuro
        'faça', 'envie', 'prepare', 'organize', 'desenvolva', 'crie', 'elabore',
        'analise', 'verifique', 'confira', 'avalie', 'examine', 'investigue',
        'será', 'faremos', 'vamos', 'iremos', 'precisamos', 'devemos'
    ]
    
    # Frases completas que indicam improdutividade
    improdutivo_phrases = [
        'muito obrigado', 'agradeço sua atenção', 'grato pela atenção',
        'só para confirmar', 'apenas confirmando', 'só para avisar',
        'só para informar', 'apenas para informar', 'só queria agradecer',
        'só isso mesmo', 'era só isso', 'sem mais para o momento',
        'tenha um bom dia', 'tenha uma boa semana', 'bom final de semana',
        'recebi sua mensagem', 'mensagem recebida', 'email recebido',
        'entendi perfeitamente', 'compreendi completamente'
    ]
    
    # Frases completas que indicam produtividade
    produtivo_phrases = [
        'preciso de sua ajuda', 'gostaria de solicitar', 'poderia me ajudar',
        'quando podemos', 'como faço para', 'por favor verifique',
        'aguardo retorno', 'aguardo resposta', 'espero seu feedback',
        'preciso que você', 'necessito que seja', 'é necessário que',
        'por gentileza', 'favor verificar', 'favor analisar',
        'estou com problema', 'estou com dificuldade', 'não consigo',
        'você poderia', 'seria possível', 'é possível',
        'o que acha de', 'o que você pensa sobre', 'qual sua opinião'
    ]
    
    # Análise de palavras individuais
    improdutivo_score = sum(1 for word in improdutivo_indicators if word in text_lower)
    produtivo_score = sum(1 for word in produtivo_indicators if word in text_lower)
    
    # Análise de frases completas (peso maior)
    improdutivo_score += sum(2 for phrase in improdutivo_phrases if phrase in text_lower)
    produtivo_score += sum(2 for phrase in produtivo_phrases if phrase in text_lower)
    
    # Análise de sinais de pontuação
    if '?' in text:  # Perguntas são fortes indicadores de produtividade
        produtivo_score += 3
    
    # Análise de verbos no imperativo ou futuro (indicam ação necessária)
    imperative_future_verbs = ['faça', 'envie', 'prepare', 'organize', 'desenvolva', 'será', 'faremos']
    produtivo_score += sum(1.5 for verb in imperative_future_verbs if verb in text_lower)
    
    # Análise de comprimento e contexto
    if len(words) < 15:  # Textos curtos
        if improdutivo_score > 0:  # Com palavras de cortesia tendem a ser improdutivos
            improdutivo_score += 2
        if '?' in text:  # Perguntas curtas são muito produtivas
            produtivo_score += 2
    else:  # Textos longos
        # Textos longos com muitas palavras produtivas são mais provavelmente produtivos
        if produtivo_score > 3:
            produtivo_score += 1
    
    # Análise de estrutura
    sentences = text.split('.')
    if len(sentences) >= 3:  # Emails com várias frases tendem a ser mais produtivos
        produtivo_score += 1
    
    # Detecção de listas (indicam tarefas ou itens a serem considerados)
    list_indicators = ['1.', '2.', '•', '-', '*', 'primeiro', 'segundo', 'terceiro']
    if any(indicator in text for indicator in list_indicators):
        produtivo_score += 2
    
    # Análise de contexto final
    if improdutivo_score > produtivo_score:
        confidence = min(0.95, 0.6 + (improdutivo_score - produtivo_score) * 0.08)
        return 'Improdutivo', confidence
    else:
        confidence = min(0.95, 0.6 + (produtivo_score - improdutivo_score) * 0.08)
        return 'Produtivo', confidence

def generate_reply(category: str, email_text: str) -> str:
    """
    Gera resposta usando OpenAI com contexto da categoria
    """
    if not _openai_available or not OPENAI_API_KEY:
        # Templates de fallback
        fallback_templates = {
            "Produtivo": (
                "Olá! Recebi sua mensagem e vou analisar sua solicitação. "
                "Retornarei em breve com mais informações."
            ),
            "Improdutivo": (
                "Olá! Muito obrigado pela sua mensagem. "
                "Fico feliz em saber disso!"
            ),
        }
        return fallback_templates.get(category, fallback_templates["Produtivo"])
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        user_prompt = (
            f"Categoria do email: {category}\n"
            f"Texto do email:\n\n{email_text}\n\n"
            "Gere uma resposta apropriada em 2-4 frases."
        )
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": _REPLY_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Erro na geração de resposta OpenAI: {e}")
        # Fallback para templates
        fallback_templates = {
            "Produtivo": "Olá! Recebi sua mensagem e vou analisar sua solicitação. Envie documentos se necessário.",
            "Improdutivo": "Olá! Muito obrigado pela sua mensagem. Fico feliz em saber disso!",
        }
        return fallback_templates.get(category, fallback_templates["Produtivo"])

