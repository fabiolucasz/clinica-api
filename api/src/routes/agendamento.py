from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from src.deps.user import SessionDep
from src.models import models
from src.deps.user import CurrentUser
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class AgendamentoRequest(BaseModel):
    paciente_id: int
    medico_id: int
    data_consulta: str  # YYYY-MM-DD
    turno_id: int

class AgendamentoResponse(BaseModel):
    success: bool
    message: str
    agendamento_id: Optional[int] = None
    paciente_nome: Optional[str] = None
    medico_nome: Optional[str] = None
    data_consulta: Optional[str] = None
    sala_nome: Optional[str] = None
    turno_nome: Optional[str] = None

@router.post("/agendar-consulta", response_model=AgendamentoResponse)
async def agendar_consulta(
    agendamento_data: AgendamentoRequest,
    db: SessionDep = None,
    current_user: CurrentUser = None
):
    """
    Endpoint otimizado para criar agendamentos
    """
    try:
        # Converter data
        data_consulta = datetime.strptime(agendamento_data.data_consulta, '%Y-%m-%d').date()
        
        # Determinar dia da semana (0=Segunda, 6=Domingo)
        dia_semana = data_consulta.weekday()
        nomes_dias = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo']
        
        if dia_semana >= 5:  # Sábado ou Domingo
            return AgendamentoResponse(
                success=False,
                message="Agendamentos apenas disponíveis de segunda a sexta-feira."
            )
        
        nome_dia = nomes_dias[dia_semana]
        
        # Buscar paciente
        paciente = db.query(models.User).filter(
            models.User.id == agendamento_data.paciente_id,
            models.User.role == 'paciente'
        ).first()
        
        if not paciente:
            return AgendamentoResponse(
                success=False,
                message="Paciente não encontrado."
            )
        
        # Buscar médico
        medico = db.query(models.User).filter(
            models.User.id == agendamento_data.medico_id,
            models.User.role == 'medico'
        ).first()
        
        if not medico:
            return AgendamentoResponse(
                success=False,
                message="Médico não encontrado."
            )
        
        # Buscar vaga do médico no dia e turno
        vaga = None
        if nome_dia == 'segunda':
            vaga = db.query(models.Vagas).filter(
                models.Vagas.segunda == agendamento_data.medico_id,
                models.Vagas.turno == agendamento_data.turno_id
            ).first()
        elif nome_dia == 'terca':
            vaga = db.query(models.Vagas).filter(
                models.Vagas.terca == agendamento_data.medico_id,
                models.Vagas.turno == agendamento_data.turno_id
            ).first()
        elif nome_dia == 'quarta':
            vaga = db.query(models.Vagas).filter(
                models.Vagas.quarta == agendamento_data.medico_id,
                models.Vagas.turno == agendamento_data.turno_id
            ).first()
        elif nome_dia == 'quinta':
            vaga = db.query(models.Vagas).filter(
                models.Vagas.quinta == agendamento_data.medico_id,
                models.Vagas.turno == agendamento_data.turno_id
            ).first()
        elif nome_dia == 'sexta':
            vaga = db.query(models.Vagas).filter(
                models.Vagas.sexta == agendamento_data.medico_id,
                models.Vagas.turno == agendamento_data.turno_id
            ).first()
        
        if not vaga:
            return AgendamentoResponse(
                success=False,
                message=f"Médico não possui vaga disponível para {nome_dia} neste turno."
            )
        
        # Verificar se há vagas disponíveis
        if vaga.pacientes_atuais >= vaga.max_pacientes:
            return AgendamentoResponse(
                success=False,
                message="Não há vagas disponíveis para este turno."
            )
        
        # Verificar se paciente já tem agendamento neste dia/horário
        agendamento_existente = db.query(models.Agendamentos).filter(
            models.Agendamentos.paciente == agendamento_data.paciente_id,
            models.Agendamentos.data_consulta == data_consulta,
            models.Agendamentos.turno == agendamento_data.turno_id
        ).first()
        
        if agendamento_existente:
            return AgendamentoResponse(
                success=False,
                message="Paciente já possui um agendamento neste dia e turno."
            )
        
        # Buscar informações do turno
        turno = db.query(models.Turnos).filter(models.Turnos.id == agendamento_data.turno_id).first()
        if not turno:
            return AgendamentoResponse(
                success=False,
                message="Turno não encontrado."
            )
        
        # Criar agendamento
        novo_agendamento = models.Agendamentos(
            clinica=vaga.clinica,
            sala=vaga.sala,
            paciente=agendamento_data.paciente_id,
            medico=agendamento_data.medico_id,
            data_consulta=data_consulta,
            turno=agendamento_data.turno_id,
            hora_inicio=turno.hora_inicio,
            hora_fim=turno.hora_fim,
            status='agendado'
        )
        
        db.add(novo_agendamento)
        
        # Incrementar contador de pacientes na vaga
        vaga.pacientes_atuais += 1
        
        db.commit()
        db.refresh(novo_agendamento)
        
        # Buscar sala para resposta
        sala = db.query(models.Salas).filter(models.Salas.id == vaga.sala).first()
        
        return AgendamentoResponse(
            success=True,
            message="Consulta agendada com sucesso!",
            agendamento_id=novo_agendamento.id,
            paciente_nome=paciente.nome,
            medico_nome=medico.nome,
            data_consulta=data_consulta.strftime('%d/%m/%Y'),
            sala_nome=sala.nome if sala else "Não definida",
            turno_nome=turno.nome
        )
        
    except Exception as e:
        print(f"Erro ao agendar consulta: {e}")
        db.rollback()
        return AgendamentoResponse(
            success=False,
            message=f"Erro ao agendar consulta: {str(e)}"
        )

@router.get("/dados-agendamento")
async def get_dados_agendamento(
    medico_id: Optional[int] = None,
    db: SessionDep = None,
    current_user: CurrentUser = None
):
    """
    Endpoint para buscar dados necessários para o formulário de agendamento
    """
    try:
        # Buscar médicos
        medicos_query = db.query(models.User)\
            .options(
                joinedload(models.User.especialidade_rel),
                joinedload(models.User.tipo_conselho_rel)
            )\
            .filter(models.User.role == 'medico')
        
        if medico_id:
            medicos_query = medicos_query.filter(models.User.id == medico_id)
        
        medicos = medicos_query.all()
        
        # Buscar vagas com relacionamentos
        vagas = db.query(models.Vagas)\
            .options(
                joinedload(models.Vagas.sala_rel),
                joinedload(models.Vagas.turno_rel),
                joinedload(models.Vagas.clinica_rel)
            )\
            .filter(models.Vagas.clinica == 1).all()  # Clínica padrão
        
        # Buscar pacientes
        pacientes = db.query(models.User)\
            .filter(models.User.role == 'paciente')\
            .limit(50)\
            .all()
        
        # Buscar horários de consultas
        horarios = db.query(models.HorariosConsultas)\
            .options(joinedload(models.HorariosConsultas.turno_rel))\
            .all()
        
        # Agrupar horários por turno
        horarios_por_turno = {}
        for horario in horarios:
            turno_id = horario.turno
            if turno_id not in horarios_por_turno:
                horarios_por_turno[turno_id] = []
            horarios_por_turno[turno_id].append({
                'id': horario.id,
                'hora_inicio': horario.hora_inicio,
                'hora_fim': horario.hora_fim
            })
        
        # Buscar turnos
        turnos = db.query(models.Turnos).all()
        
        turnos_data = []
        for turno in turnos:
            # Buscar horários deste turno
            horarios_do_turno = horarios_por_turno.get(turno.id, [])
            
            turno_dict = {
                'id': turno.id,
                'nome': turno.nome,
                'hora_inicio': turno.hora_inicio,
                'hora_fim': turno.hora_fim,
                'horarios': horarios_do_turno
            }
            turnos_data.append(turno_dict)
        
        # Construir resposta
        medicos_data = []
        for medico in medicos:
            medico_dict = {
                'id': medico.id,
                'nome': medico.nome,
                'especialidade': medico.especialidade,
                'especialidade_nome': medico.especialidade_rel.nome if medico.especialidade_rel else None,
                'tipo_conselho': medico.tipo_conselho,
                'tipo_conselho_nome': medico.tipo_conselho_rel.nome if medico.tipo_conselho_rel else None,
                'uf_conselho': medico.uf_conselho,
                'numero_conselho': medico.numero_conselho
            }
            medicos_data.append(medico_dict)
        
        vagas_data = []
        for vaga in vagas:
            dias_medicos = {}
            for dia in ['segunda', 'terca', 'quarta', 'quinta', 'sexta']:
                medico_id_vaga = getattr(vaga, dia)
                if medico_id_vaga and medico_id_vaga != 0:
                    dias_medicos[dia] = medico_id_vaga
            
            vaga_dict = {
                'id': vaga.id,
                'sala_id': vaga.sala,
                'sala_nome': vaga.sala_rel.nome if vaga.sala_rel else None,
                'turno_id': vaga.turno,
                'turno_nome': vaga.turno_rel.nome if vaga.turno_rel else None,
                'max_pacientes': vaga.max_pacientes,
                'pacientes_atuais': vaga.pacientes_atuais,
                'dias_medicos': dias_medicos
            }
            vagas_data.append(vaga_dict)
        
        pacientes_data = []
        for paciente in pacientes:
            paciente_dict = {
                'id': paciente.id,
                'nome': paciente.nome,
                'cpf': paciente.cpf,
                'celular': paciente.celular
            }
            pacientes_data.append(paciente_dict)
        
        return {
            'medicos': medicos_data,
            'vagas': vagas_data,
            'pacientes': pacientes_data,
            'turnos': turnos_data
        }
        
    except Exception as e:
        print(f"Erro ao buscar dados de agendamento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def garantir_turnos_padrao(db: Session):
    """
    Garante que os turnos padrão existam com os horários corretos
    """
    turnos_padrao = [
        {"nome": "Manhã", "hora_inicio": "08:00", "hora_fim": "12:00"},
        {"nome": "Tarde", "hora_inicio": "13:00", "hora_fim": "17:00"},
        {"nome": "Noite", "hora_inicio": "18:00", "hora_fim": "22:00"}
    ]
    
    for turno_data in turnos_padrao:
        # Verificar se turno já existe
        turno_existente = db.query(models.Turnos).filter(
            models.Turnos.nome == turno_data["nome"]
        ).first()
        
        if not turno_existente:
            # Criar novo turno
            novo_turno = models.Turnos(
                nome=turno_data["nome"],
                hora_inicio=turno_data["hora_inicio"],
                hora_fim=turno_data["hora_fim"]
            )
            db.add(novo_turno)
        else:
            # Atualizar horários se necessário
            if (turno_existente.hora_inicio != turno_data["hora_inicio"] or 
                turno_existente.hora_fim != turno_data["hora_fim"]):
                turno_existente.hora_inicio = turno_data["hora_inicio"]
                turno_existente.hora_fim = turno_data["hora_fim"]
    
    try:
        db.commit()
        print("Turnos padrão verificados/atualizados com sucesso")
    except Exception as e:
        print(f"Erro ao salvar turnos padrão: {e}")
        db.rollback()
