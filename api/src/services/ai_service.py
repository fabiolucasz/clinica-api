import json
import re
import time

from openai import APIError, OpenAI, RateLimitError

from src.database.config import settings


class AIServiceError(Exception):
    """Exceção customizada para erros do serviço de IA"""


client = OpenAI(base_url=settings.AI_BASE_URL, api_key=settings.AI_API_KEY)


def safe_chat_completion(messages, model=None, max_retries=5, **kwargs):
    """Executa chat completion com retry para rate limits"""
    if model is None:
        model = settings.AI_MODEL

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model, messages=messages, **kwargs
            )
            return response
        except RateLimitError as e:
            wait_time = (2**attempt) + 1
            print(
                f"Rate limit atingido (429). Tentando novamente em {wait_time}s... Erro: {e}"
            )
            time.sleep(wait_time)
        except APIError as e:
            if hasattr(e, "status_code") and e.status_code == 429:
                wait_time = (2**attempt) + 1
                print(
                    f"Rate limit atingido (429 APIError). Tentando novamente em {wait_time}s... Erro: {e}"
                )
                time.sleep(wait_time)
                continue
            if "429" in str(e):
                wait_time = (2**attempt) + 1
                print(
                    f"Rate limit detectado na mensagem do APIError. Tentando novamente em {wait_time}s... Erro: {e}"
                )
                time.sleep(wait_time)
                continue
            wait_time = (2**attempt) + 1
            print(f"Erro da API. Tentando novamente em {wait_time}s... Erro: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(wait_time)
        except Exception as e:
            if "429" in str(e):
                wait_time = (2**attempt) + 1
                print(
                    f"Erro contendo 429 detectado. Tentando novamente em {wait_time}s... Erro: {e}"
                )
                time.sleep(wait_time)
                continue
            print(f"Erro inesperado no chat completion: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2)
    raise AIServiceError("Falha ao obter resposta após várias tentativas.")


def extract_patient_data_from_chat(messages_history):
    """
    Usa o modelo de IA para extrair de forma estruturada os dados do paciente
    a partir do histórico da conversa. Retorna um dicionário com os campos ou None.
    """
    history_text = ""
    for msg in messages_history:
        role = "Assistente" if msg["role"] == "assistant" else "Usuário"
        history_text += f"{role}: {msg['content']}\n\n"

    prompt = f"""Você é um extrator de dados estruturados de pacientes. Sua tarefa é analisar o histórico de conversas entre o assistente da clínica e o paciente, e extrair os dados solicitados.

Campos a extrair:
1. Nome completo (name) - Nome completo do paciente.
2. WhatsApp (whatsapp) - Apenas os dígitos numéricos (com DDD), ex: 21974641169.
3. Data de nascimento (birth_date) - Formate como AAAA-MM-DD. Se não conseguir converter ou não souber o ano completo, tente aproximar ou manter o formato informado. Se não informado, retorne null.
4. Área de atendimento desejada (desired_specialty) - ex: Cardiologia, Dermatologia, etc.
5. Convênio (insurance) - Nome do convênio ou 'Particular'.

Retorne APENAS um objeto JSON válido contendo exatamente essas chaves. Se alguma informação não estiver presente na conversa ou não for informada pelo usuário, defina o valor como null.
Não inclua nenhuma formatação markdown como ```json ou explicações extras.

Histórico da Conversa:
{history_text}
"""

    try:
        response = safe_chat_completion(messages=[{"role": "user", "content": prompt}])
        content = response.choices[0].message.content.strip()

        # Limpar markdown code blocks se o modelo retornar
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\n", "", content, flags=re.IGNORECASE)
            content = re.sub(r"\n```$", "", content)

        data = json.loads(content)
        return data
    except Exception as e:
        print(f"Erro ao extrair dados estruturados: {e}")
        return None


def is_patient_data_complete(data):
    """
    Verifica se todas as informações obrigatórias do paciente foram coletadas.
    """
    if not data:
        return False

    required_keys = ["name", "whatsapp", "birth_date", "desired_specialty", "insurance"]
    for key in required_keys:
        val = data.get(key)
        if val is None or val == "":
            return False
        if isinstance(val, str):
            val_lower = val.lower().strip()
            if val_lower in [
                "null",
                "none",
                "não informado",
                "não fornecido",
                "n/a",
                "não especificado",
                "pendente",
            ]:
                return False
    return True


def get_assistant_response(user_message, chat_history):
    """
    Gera resposta do assistente com base no contexto da clínica
    """
    context = """
    1. Você é um assistente de atendimento para uma clínica médica.
    2. Seja cordial e profissional. Forneça respostas claras e objetivas.
    3. Responda em português brasileiro.
    4. Não invente informações que não foram fornecidas pelo paciente.
    5. Se o paciente fizer uma pergunta fora do escopo, diga que não consegue ajudar com isso.
    6. Sua função é coletar informações do paciente para agendamento de consultas.
    7. Pergunte um por um: nome completo, Whatsapp, data de nascimento, área de atendimento desejada, convênio ou particular:
        - Nome Completo
            ex: João Gomes da Silva
        - Whatsapp 
            ex: (11) 99999-9999
        - Data de nascimento 
            ex: 01/01/2000
        - Área de atendimento desejada 
            ex: Cardiologia, Dermatologia, etc.
        - Convênio ou particular
            ex: Sim, tenho convênio | Não, quero pagar no particular
        - Se tiver convênio, pergunte qual
            ex: Unimed, Sulamérica, Bradesco, etc.
    

    8. Após coletar as informações, se não estiver tudo certo, permita correções nas informações fornecidas, do contrário resuma apenas uma vez assim:
        - Nome: João Gomes da Silva
        - Whatsapp: (11) 99999-9999
        - Data de nascimento: 01/01/2000
        - Área de atendimento desejada: Cardiologia
        - Convênio: Unimed 
    9. Agradeça ao paciente por fornecer as informações e informe que logo alguém da clínica vai entrar em contato com ele.
    """

    # Construir prompt completo
    full_prompt = context + "\n\n"
    for msg in chat_history:
        role = "Assistente" if msg["role"] == "assistant" else "Usuário"
        full_prompt += f"{role}: {msg['content']}\n\n"
    full_prompt += "Assistente:"

    try:
        response = safe_chat_completion(
            messages=[{"role": "user", "content": full_prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro ao gerar resposta do assistente: {e}")
        return "Desculpe, ocorreu um erro de conexão com o servidor de IA. Por favor, tente novamente."
