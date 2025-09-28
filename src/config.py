from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
CLASSIFIER_MODEL = os.getenv('CLASSIFIER_MODEL', 'joeddav/xlm-roberta-large-xnli')
LANG = os.getenv('LANG', 'pt')
HF_API_TOKEN = os.getenv('HF_API_TOKEN')
