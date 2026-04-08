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
    clinica: int  # Clínica padrão = 1
    sala: int
    paciente: int  # Correspondente ao campo paciente no model
    medico: int   # Correspondente ao campo medico no model
    data_consulta: datetime  # DateTime completo
    turno: int    # Correspondente ao campo turno no model
    hora_inicio: str  # Formato HH:MM
    hora_fim: str    # Formato HH:MM
    status: str = "agendado"

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
        # Buscar paciente
        paciente = db.query(models.User).filter(
            models.User.id == agendamento_data.paciente,
            models.User.role == 'paciente'
        ).first()
        
        if not paciente:
            return AgendamentoResponse(
                success=False,
                message="Paciente não encontrado."
            )
        
        # Buscar médico
        medico = db.query(models.User).filter(
            models.User.id == agendamento_data.medico,
            models.User.role == 'medico'
        ).first()
        
        if not medico:
            return AgendamentoResponse(
                success=False,
                message="Médico não encontrado."
            )
        
        # Buscar sala
        sala = db.query(models.Salas).filter(models.Salas.id == agendamento_data.sala).first()
        if not sala:
            return AgendamentoResponse(
                success=False,
                message="Sala não encontrada."
            )
        
        # Buscar turno
        turno = db.query(models.Turnos).filter(models.Turnos.id == agendamento_data.turno).first()
        if not turno:
            return AgendamentoResponse(
                success=False,
                message="Turno não encontrado."
            )
        
        # Verificar se já existe agendamento neste horário
        agendamento_existente = db.query(models.Agendamentos).filter(
            models.Agendamentos.paciente == agendamento_data.paciente,
            models.Agendamentos.medico == agendamento_data.medico,
            models.Agendamentos.data_consulta == agendamento_data.data_consulta,
            models.Agendamentos.hora_inicio == agendamento_data.hora_inicio,
            models.Agendamentos.hora_fim == agendamento_data.hora_fim,
            models.Agendamentos.status == 'agendado'
        ).first()
        
        if agendamento_existente:
            return AgendamentoResponse(
                success=False,
                message="Já existe um agendamento para este paciente neste horário."
            )
        
        # Criar novo agendamento
        novo_agendamento = models.Agendamentos(
            clinica=agendamento_data.clinica,
            sala=agendamento_data.sala,
            paciente=agendamento_data.paciente,
            medico=agendamento_data.medico,
            data_consulta=agendamento_data.data_consulta,
            turno=agendamento_data.turno,
            hora_inicio=agendamento_data.hora_inicio,
            hora_fim=agendamento_data.hora_fim,
            status=agendamento_data.status
        )
        
        db.add(novo_agendamento)
        db.commit()
        db.refresh(novo_agendamento)
        
        # Retornar sucesso
        return AgendamentoResponse(
            success=True,
            message="Agendamento realizado com sucesso!",
            agendamento_id=novo_agendamento.id,
            paciente_nome=paciente.nome,
            medico_nome=medico.nome,
            data_consulta=novo_agendamento.data_consulta.strftime('%d/%m/%Y'),
            sala_nome=sala.nome,
            turno_nome=turno.nome
        )
        
    except Exception as e:
        print(f"Erro ao criar agendamento: {e}")
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
