from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, extract
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from src.deps.user import CurrentUser, SessionDep
from src.models import models

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/resumo")
async def get_dashboard_resumo(current_user: CurrentUser, db: SessionDep):
    """
    Retorna resumo consolidado do dashboard com:
    - Contagens (pacientes, médicos, clínicas, consultas)
    - Consultas do dia
    - Últimos pacientes cadastrados
    - Estatísticas por status
    - Dados para gráfico mensal
    """
    # Verificar se é administrador
    if current_user.role != "administrador":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores.")
    
    try:
        hoje = date.today()
        inicio_mes = hoje.replace(day=1)
        
        # 1. Contagens principais
        total_pacientes = db.query(models.User).filter(models.User.role == "paciente").count()
        total_medicos = db.query(models.User).filter(models.User.role == "medico").count()
        total_clinicas = db.query(models.Clinicas).count()
        
        # 2. Consultas de hoje (usando strftime para compatibilidade com SQLite)
        hoje_str = hoje.strftime('%Y-%m-%d')
        consultas_hoje = db.query(models.Agendamentos).filter(
            func.strftime('%Y-%m-%d', models.Agendamentos.data_consulta) == hoje_str
        ).count()
        
        # 3. Consultas pendentes (aguardando confirmação)
        consultas_pendentes = db.query(models.Agendamentos).filter(
            models.Agendamentos.status == "aguardando"
        ).count()
        
        # 4. Consultas do mês atual
        consultas_mes = db.query(models.Agendamentos).filter(
            models.Agendamentos.data_consulta >= inicio_mes
        ).count()
        
        # 5. Consultas do dia (próximas 5)
        ultimas_consultas = db.query(models.Agendamentos).filter(
            func.strftime('%Y-%m-%d', models.Agendamentos.data_consulta) >= hoje_str
        ).options(
            joinedload(models.Agendamentos.paciente_rel),
            joinedload(models.Agendamentos.medico_rel),
            joinedload(models.Agendamentos.clinica_rel)
        ).order_by(
            models.Agendamentos.data_consulta
        ).limit(5).all()
        
        consultas_formatadas = []
        for consulta in ultimas_consultas:
            paciente_nome = consulta.paciente_rel.nome if consulta.paciente_rel else "N/A"
            medico_nome = consulta.medico_rel.nome if consulta.medico_rel else "N/A"
            clinica_nome = consulta.clinica_rel.nome if consulta.clinica_rel else "N/A"
            
            consultas_formatadas.append({
                "id": consulta.id,
                "paciente": paciente_nome,
                "medico": medico_nome,
                "clinica": clinica_nome,
                "data_hora": consulta.data_consulta.isoformat() if consulta.data_consulta else None,
                "status": consulta.status
            })
        
        # 6. Últimos 5 pacientes cadastrados
        ultimos_pacientes = db.query(models.User).filter(
            models.User.role == "paciente"
        ).order_by(
            models.User.created_at.desc()
        ).limit(5).all()
        
        pacientes_formatados = []
        for paciente in ultimos_pacientes:
            pacientes_formatados.append({
                "id": paciente.id,
                "nome": paciente.nome,
                "email": paciente.email,
                "celular": paciente.celular,
                "data_cadastro": paciente.created_at.isoformat() if paciente.created_at else None
            })
        
        # 7. Estatísticas por status
        status_counts = db.query(
            models.Agendamentos.status,
            func.count(models.Agendamentos.id)
        ).group_by(models.Agendamentos.status).all()
        
        estatisticas_status = {
            "agendada": 0,
            "confirmada": 0,
            "cancelada": 0,
            "realizada": 0,
            "aguardando": 0
        }
        for status, count in status_counts:
            if status in estatisticas_status:
                estatisticas_status[status] = count
        
        # 8. Dados para gráfico mensal (últimos 6 meses)
        grafico_mensal = []
        for i in range(5, -1, -1):
            mes_data = hoje.replace(day=1) - timedelta(days=i*30)
            mes_fim = (mes_data.replace(day=28) + timedelta(days=4)).replace(day=1)
            
            count = db.query(models.Agendamentos).filter(
                models.Agendamentos.data_consulta >= mes_data,
                models.Agendamentos.data_consulta < mes_fim
            ).count()
            
            grafico_mensal.append({
                "mes": mes_data.strftime("%b/%Y"),
                "quantidade": count
            })
        
        return {
            "total_pacientes": total_pacientes,
            "total_medicos": total_medicos,
            "total_clinicas": total_clinicas,
            "consultas_hoje": consultas_hoje,
            "consultas_pendentes": consultas_pendentes,
            "consultas_mes": consultas_mes,
            "ultimas_consultas": consultas_formatadas,
            "ultimos_pacientes": pacientes_formatados,
            "estatisticas_status": estatisticas_status,
            "grafico_mensal": grafico_mensal,
            "atualizado_em": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao gerar resumo do dashboard: {str(e)}"
        )
