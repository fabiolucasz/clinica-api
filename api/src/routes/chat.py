from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.crud import chat as chat_crud
from src.deps.user import CurrentUser, SessionDep, get_db
from src.schemas.chat import ChatRequest, ChatResponse, LeadCreate, LeadResponse
from src.services.ai_service import (
    extract_patient_data_from_chat,
    get_assistant_response,
    is_patient_data_complete,
)

router = APIRouter()

# Armazenamento em memória para histórico de chat
# Estrutura: {session_id: [{"role": "user|assistant", "content": str}]}
chat_history_memory: dict[str, list[dict]] = {}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Endpoint para chat com IA. Recebe mensagem do usuário, armazena na memória,
    obtém resposta da IA e salva também na memória.
    """
    # Inicializar histórico da sessão se não existir
    if request.session_id not in chat_history_memory:
        chat_history_memory[request.session_id] = []

    # Adicionar mensagem do usuário ao histórico em memória
    chat_history_memory[request.session_id].append(
        {"role": "user", "content": request.message}
    )

    # Obter resposta da IA
    assistant_response = get_assistant_response(
        request.message, chat_history_memory[request.session_id]
    )

    # Adicionar resposta do assistente ao histórico em memória
    chat_history_memory[request.session_id].append(
        {"role": "assistant", "content": assistant_response}
    )

    # Verificar se a resposta contém o resumo final dos dados
    lower_response = assistant_response.lower()
    if "nome:" in lower_response and (
        "whatsapp:" in lower_response
        or "zap:" in lower_response
        or "whats:" in lower_response
        or "telef" in lower_response
    ):
        # Tentar extrair dados estruturados
        extracted_data = extract_patient_data_from_chat(
            chat_history_memory[request.session_id]
        )
        if is_patient_data_complete(extracted_data):
            try:
                chat_crud.create_or_update_lead(db, LeadCreate(**extracted_data))
            except Exception as e:
                print(f"Erro ao salvar lead: {e}")

    return ChatResponse(response=assistant_response)


@router.get("/leads", response_model=list[LeadResponse])
async def get_leads(
    current_user: CurrentUser, db: SessionDep, skip: int = 0, limit: int = 100
):
    """
    Retorna todos os leads (pacientes extraídos do chat) - Requer autenticação
    """
    leads = chat_crud.get_all_leads(db, skip=skip, limit=limit)
    return [LeadResponse.model_validate(lead) for lead in leads]
