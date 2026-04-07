from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json

from ..deps.user import get_db
from ..models.models import User, Vagas, Clinicas, Salas

router = APIRouter(prefix="/medico-sala", tags=["medico-sala-optimized"])

@router.get("/optimized/{medico_id}")
async def get_medico_sala_optimized(
    medico_id: int,
    clinica_id: int = 1,
    db: Session = Depends(get_db)
):
    """
    Endpoint otimizado que retorna todos os dados necessários para a página
    de cadastro de médico em sala em uma única requisição.
    """
    try:
        print(f"DEBUG: Buscando médico ID {medico_id}")
        
        # Buscar médico
        medico = db.query(User).filter(User.id == medico_id).first()
        if not medico:
            print(f"DEBUG: Médico {medico_id} não encontrado")
            raise HTTPException(status_code=404, detail="Médico não encontrado")
        
        print(f"DEBUG: Médico encontrado: {medico.nome}")
        print(f"DEBUG: Buscando vagas da clínica {clinica_id}")
        
        # Buscar vagas da clínica com joins para otimizar
        vagas = db.query(Vagas).filter(Vagas.clinica == clinica_id).all()
        print(f"DEBUG: Encontradas {len(vagas)} vagas")
        
        # Coletar IDs únicos de médicos das vagas
        medicos_ids = set()
        for vaga in vagas:
            for dia in ['segunda', 'terca', 'quarta', 'quinta', 'sexta']:
                medico_id_vaga = getattr(vaga, dia)
                if medico_id_vaga and medico_id_vaga != 0:
                    medicos_ids.add(medico_id_vaga)
        
        print(f"DEBUG: Medicos IDs encontrados nas vagas: {medicos_ids}")
        
        # Buscar todos os médicos necessários em lote
        medicos_nomes = {}
        if medicos_ids:
            print(f"DEBUG: Buscando {len(medicos_ids)} médicos em lote")
            medicos_db = db.query(User).filter(User.id.in_(medicos_ids)).all()
            medicos_nomes = {med.id: med.nome for med in medicos_db}
            print(f"DEBUG: Nomes encontrados: {medicos_nomes}")
        
        # Enriquecer vagas com nomes dos médicos
        vagas_enriquecidas = []
        for vaga in vagas:
            vaga_dict = {
                'id': vaga.id,
                'sala_id': vaga.sala,
                'sala_nome': 'Sala Padrão',  # Simplificado
                'turno': vaga.turno,
                'max_pacientes': vaga.max_pacientes,
                'pacientes_atuais': vaga.pacientes_atuais,
            }
            
            # Adicionar médicos e nomes
            for dia in ['segunda', 'terca', 'quarta', 'quinta', 'sexta']:
                medico_id_vaga = getattr(vaga, dia)
                vaga_dict[dia] = medico_id_vaga if medico_id_vaga and medico_id_vaga != 0 else None
                vaga_dict[f'{dia}_nome'] = medicos_nomes.get(medico_id_vaga) if medico_id_vaga and medico_id_vaga != 0 else None
            
            vagas_enriquecidas.append(vaga_dict)
        
        print(f"DEBUG: {len(vagas_enriquecidas)} vagas enriquecidas")
        
        # Retornar resposta otimizada
        return {
            'medico': {
                'id': medico.id,
                'nome': medico.nome,
                'email': medico.email,
                'celular': medico.celular,
                'cpf': medico.cpf,
                'role': medico.role
            },
            'vagas': vagas_enriquecidas,
            'clinica': {
                'id': clinica_id,
                'nome': 'Clínica Padrão'  # Pode ser dinâmico se necessário
            },
            'total_vagas': len(vagas_enriquecidas)
        }
        
    except Exception as e:
        print(f"DEBUG: Erro no endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados otimizados: {str(e)}")
