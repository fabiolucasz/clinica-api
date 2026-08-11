import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import joinedload

from src.deps.user import CurrentUser, SessionDep
from src.models import models

router = APIRouter()


@router.get("/agenda-completa")
async def get_agenda_completa(
    medico_id: int | None = None,
    data_inicio: str | None = None,
    data_fim: str | None = None,
    db: SessionDep = None,
    current_user: CurrentUser = None,
):
    """
    Endpoint otimizado que retorna todos os dados para a agenda:
    - Médicos disponíveis
    - Agendamentos existentes
    - Vagas/disponibilidade dos médicos
    """
    start_time = time.time()

    try:
        # Usar sempre a clínica padrão (ID 1)
        clinica_id = 1

        # Processar datas
        tz = ZoneInfo("America/Sao_Paulo")
        if data_inicio and data_fim:
            try:
                data_inicio_dt = datetime.strptime(data_inicio, "%d/%m/%Y").replace(
                    tzinfo=tz
                )
                data_fim_dt = datetime.strptime(data_fim, "%d/%m/%Y").replace(tzinfo=tz)
            except ValueError:
                # Usar semana atual
                hoje = datetime.now(tz)
                data_inicio_dt = hoje - timedelta(days=hoje.weekday())
                data_fim_dt = data_inicio_dt + timedelta(days=4)
        else:
            # Usar semana atual
            hoje = datetime.now(tz)
            data_inicio_dt = hoje - timedelta(days=hoje.weekday())
            data_fim_dt = data_inicio_dt + timedelta(days=4)

        # Buscar médicos que trabalham na clínica (através das vagas)
        medicos_query = (
            db.query(models.User)
            .options(
                joinedload(models.User.especialidade_rel),
                joinedload(models.User.tipo_conselho_rel),
                joinedload(models.User.estado_rel),
            )
            .join(
                models.Vagas,
                (
                    (models.User.id == models.Vagas.segunda)
                    | (models.User.id == models.Vagas.terca)
                    | (models.User.id == models.Vagas.quarta)
                    | (models.User.id == models.Vagas.quinta)
                    | (models.User.id == models.Vagas.sexta)
                ),
            )
            .filter(models.Vagas.clinica == clinica_id)
            .distinct()
        )

        medicos = medicos_query.all()

        # Buscar vagas da clínica com relacionamentos
        vagas = (
            db.query(models.Vagas)
            .options(
                joinedload(models.Vagas.sala_rel),
                joinedload(models.Vagas.turno_rel),
                joinedload(models.Vagas.clinica_rel),
            )
            .filter(models.Vagas.clinica == clinica_id)
            .all()
        )

        # Buscar agendamentos no período
        agendamentos_query = (
            db.query(models.Agendamentos)
            .options(
                joinedload(models.Agendamentos.paciente_rel),
                joinedload(models.Agendamentos.medico_rel),
                joinedload(models.Agendamentos.sala_rel),
                joinedload(models.Agendamentos.turno_rel),
            )
            .filter(
                models.Agendamentos.data_consulta >= data_inicio_dt,
                models.Agendamentos.data_consulta <= data_fim_dt,
            )
        )

        if medico_id:
            agendamentos_query = agendamentos_query.filter(
                models.Agendamentos.medico == medico_id
            )

        agendamentos = agendamentos_query.all()

        # Construir resposta
        medicos_data = []
        for medico in medicos:
            medico_dict = {
                "id": medico.id,
                "nome": medico.nome,
                "especialidade": medico.especialidade,
                "especialidade_nome": (
                    medico.especialidade_rel.nome if medico.especialidade_rel else None
                ),
                "tipo_conselho": medico.tipo_conselho,
                "tipo_conselho_nome": (
                    medico.tipo_conselho_rel.nome if medico.tipo_conselho_rel else None
                ),
                "uf_conselho": medico.uf_conselho,
                "uf_conselho_nome": medico.estado_rel.uf if medico.estado_rel else None,
                "numero_conselho": medico.numero_conselho,
            }
            medicos_data.append(medico_dict)

        vagas_data = []
        for vaga in vagas:
            # Mapear dias da semana
            dias_medicos = {}
            for dia in ["segunda", "terca", "quarta", "quinta", "sexta"]:
                medico_id_vaga = getattr(vaga, dia)
                if medico_id_vaga and medico_id_vaga != 0:
                    dias_medicos[dia] = medico_id_vaga

            vaga_dict = {
                "id": vaga.id,
                "sala_id": vaga.sala,
                "sala_nome": vaga.sala_rel.nome if vaga.sala_rel else None,
                "turno_id": vaga.turno,
                "turno_nome": vaga.turno_rel.nome if vaga.turno_rel else None,
                "turno_hora_inicio": (
                    vaga.turno_rel.hora_inicio if vaga.turno_rel else None
                ),
                "turno_hora_fim": vaga.turno_rel.hora_fim if vaga.turno_rel else None,
                "max_pacientes": vaga.max_pacientes,
                "pacientes_atuais": vaga.pacientes_atuais,
                "dias_medicos": dias_medicos,
            }
            vagas_data.append(vaga_dict)

        agendamentos_data = []
        for agendamento in agendamentos:
            agendamento_dict = {
                "id": agendamento.id,
                "paciente_id": agendamento.paciente,
                "paciente_nome": (
                    agendamento.paciente_rel.nome if agendamento.paciente_rel else None
                ),
                "medico_id": agendamento.medico,
                "medico_nome": (
                    agendamento.medico_rel.nome if agendamento.medico_rel else None
                ),
                "sala_id": agendamento.sala,
                "sala_nome": (
                    agendamento.sala_rel.nome if agendamento.sala_rel else None
                ),
                "turno_id": agendamento.turno,
                "turno_nome": (
                    agendamento.turno_rel.nome if agendamento.turno_rel else None
                ),
                "data_consulta": agendamento.data_consulta.strftime("%Y-%m-%d"),
                "data_consulta_br": agendamento.data_consulta.strftime("%d/%m/%Y"),
                "hora_inicio": agendamento.hora_inicio,
                "hora_fim": agendamento.hora_fim,
                "status": agendamento.status,
            }
            agendamentos_data.append(agendamento_dict)

        # Gerar datas da semana
        datas_semana = {}
        for i, dia_nome in enumerate(["segunda", "terca", "quarta", "quinta", "sexta"]):
            data_dia = data_inicio_dt + timedelta(days=i)
            datas_semana[dia_nome] = {
                "data": data_dia.strftime("%Y-%m-%d"),
                "data_br": data_dia.strftime("%d/%m/%Y"),
                "dia_semana": data_dia.strftime("%A"),
            }

        response_data = {
            "medicos": medicos_data,
            "vagas": vagas_data,
            "agendamentos": agendamentos_data,
            "datas_semana": datas_semana,
            "periodo": {
                "data_inicio": data_inicio_dt.strftime("%Y-%m-%d"),
                "data_fim": data_fim_dt.strftime("%Y-%m-%d"),
                "data_inicio_br": data_inicio_dt.strftime("%d/%m/%Y"),
                "data_fim_br": data_fim_dt.strftime("%d/%m/%Y"),
            },
        }

        print(f"DEBUG: Agenda completa carregada em {time.time() - start_time:.2f}s")
        print(
            f"DEBUG: {len(medicos_data)} médicos, {len(vagas_data)} vagas, {len(agendamentos_data)} agendamentos"
        )

        return response_data

    except Exception as e:
        print(f"Erro ao carregar agenda completa: {e}")
        raise HTTPException(status_code=500, detail=str(e))
