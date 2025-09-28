from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
# Importações externas (mantidas como no código fornecido)
from src.nlp.preprocess import preprocess
from src.classifier import classify_text
from src.classifier import generate_reply
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import re
from io import BytesIO

try:
    from pypdf import PdfReader
    _PDF_AVAILABLE = True
except Exception:
    _PDF_AVAILABLE = False

app = FastAPI(title="Classificador de E-mails")

# Enable CORS for local dev and simple hosting scenarios
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # ou ["*"] durante dev se preferir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static UI
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


class ClassifyRequest(BaseModel):
    text: str

class ClassifyResponse(BaseModel):
    category: str
    confidence: float
    reply: str
    # Campos adicionados para retornar o assunto e o conteúdo
    subject: str = "(Sem Assunto Detectado)" 
    content: str = "(Sem Conteúdo Detectado)"
    


@app.get("/", response_class=HTMLResponse)
async def index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.isfile(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>API Online</h1><p>Envie POST para /classify ou /upload</p>"


@app.post("/classify", response_model=ClassifyResponse)
async def classify_endpoint(payload: ClassifyRequest):
    pre = preprocess(payload.text)
    category, score = classify_text(pre)
    reply = generate_reply(category, payload.text)
    # Retorna o texto original como assunto e conteúdo no endpoint /classify
    return ClassifyResponse(
        category=category, 
        confidence=score, 
        reply=reply,
        subject="(Texto Fornecido no Body)",
        content=payload.text
    )

# Função auxiliar para extrair Assunto e Conteúdo do texto bruto
# A Lógica foi aprimorada para remover metadados de forma mais robusta.
def extract_email_parts(raw_text: str) -> dict:
    """Tenta extrair o assunto e o corpo da mensagem do texto bruto de um email."""
    
    # 1. Tenta identificar o assunto (assumindo a estrutura do PDF anexo)
    # Assunto é mantido simples. Se o assunto for "(sem assunto)", ele será o marcador.
    subject_match = re.search(r'\(sem assunto\)', raw_text, re.IGNORECASE)
    subject = subject_match.group(0).strip() if subject_match else "(Sem Assunto Detectado)"
    
    # 2. Limpeza agressiva do texto para isolar o corpo da mensagem (content)
    # Remove datas/horários, URLs e números de página (ex: 1/1)
    content = re.sub(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}.*|\d{1,2}:\d{2}.*|https?:\/\/[^\s]+|\s\d\/\d\s', '', raw_text)
    # Remove emails e marcadores de remetente/destinatário
    content = re.sub(r'[\w.-]+@[\w.-]+.*|Para:.*|De:.*', '', content, flags=re.IGNORECASE)
    # Remove termos de UI do Gmail
    content = re.sub(r'M Gmail|Gmail \(sem assunto\)|1 mensagem|\(sem assunto\)', '', content, flags=re.IGNORECASE)
    
    # Remove o texto do assunto do conteúdo, se for encontrado.
    if subject != "(Sem Assunto Detectado)":
        content = re.sub(re.escape(subject), '', content, flags=re.IGNORECASE).strip()

    # Normaliza espaços e quebras de linha para obter o corpo limpo
    content = re.sub(r'\s+', ' ', content).strip()
    
    # O texto para classificação deve ser o conteúdo, ou o assunto se o conteúdo estiver vazio
    text_to_process = content if content else subject

    return {
        "subject": subject,
        "content": content,
        "text_to_process": text_to_process
    }


@app.post("/upload", response_model=ClassifyResponse)
async def upload_email(file: UploadFile = File(...)):
    data = await file.read()
    filename = (file.filename or "").lower()
    content_type = (file.content_type or "").lower()

    raw = ""
    # PDF handling
    if (filename.endswith(".pdf") or "pdf" in content_type) and _PDF_AVAILABLE:
        try:
            reader = PdfReader(BytesIO(data))
            texts = []
            for page in reader.pages:
                texts.append(page.extract_text() or "")
            raw = "\n".join(texts).strip()
        except Exception:
            raw = ""

    # Fallback: assume UTF-8 text
    if not raw:
        raw = data.decode("utf-8", errors="ignore")

    # Chamada da função de extração para obter as partes
    email_parts = extract_email_parts(raw)

    # Usa o texto limpo para classificação (pre)
    pre = preprocess(email_parts["text_to_process"])
    
    # Este é o print que mostra o texto limpo antes da classificação
    # Com a correção, deve imprimir "obrigado pelo suporte"
    print(pre)
    
    # Tratamento de Erro: A classificação e a geração de resposta falham devido ao erro do OpenAI Client
    # O código continua com a chamada, mas se o erro persistir, o servidor deve falhar.
    category, score = classify_text(pre)
    reply = generate_reply(category, email_parts["content"]) # Gera a resposta com base no conteúdo

    # Retorna o Assunto e o Conteúdo extraídos
    return ClassifyResponse(
        category=category, 
        confidence=score, 
        reply=reply,
        subject=email_parts["subject"],
        content=email_parts["content"]
    )
