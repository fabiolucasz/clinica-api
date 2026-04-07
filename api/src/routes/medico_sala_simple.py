from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import json

from ..deps.user import get_db
from ..models.models import User, Vagas

router = APIRouter(prefix="/medico-sala-simple", tags=["medico-sala-simple"])

@router.get("/simple/{medico_id}")
async def get_medico_sala_simple(
    medico_id: int,
    db: Session = Depends(get_db)
):
    """
    Endpoint simplificado para teste - sem relacionamentos complexos
    """
    try:
        print(f"DEBUG SIMPLES: Buscando médico ID {medico_id}")
        
        # Buscar médico
        medico = db.query(User).filter(User.id == medico_id).first()
        if not medico:
            print(f"DEBUG SIMPLES: Médico {medico_id} não encontrado")
            raise HTTPException(status_code=404, detail="Médico não encontrado")
        
        print(f"DEBUG SIMPLES: Médico encontrado: {medico.nome}")
        
        # Buscar vagas da clínica padrão (ID 1)
        vagas = db.query(Vagas).filter(Vagas.clinica == 1).all()
        print(f"DEBUG SIMPLES: Encontradas {len(vagas)} vagas")
        
        # Processar vagas de forma simples
        vagas_simples = []
        for vaga in vagas:
            vaga_dict = {
                'id': vaga.id,
                'sala': vaga.sala,
                'sala_nome': vaga.sala_rel.nome if vaga.sala_rel else 'Sala não encontrada',
                'turno': vaga.turno,
                'segunda': vaga.segunda,
                'terca': vaga.terca,
                'quarta': vaga.quarta,
                'quinta': vaga.quinta,
                'sexta': vaga.sexta,
            }
            vagas_simples.append(vaga_dict)
        
        resultado = {
            'medico': {
                'id': medico.id,
                'nome': medico.nome,
                'email': medico.email,
            },
            'vagas': vagas_simples,
            'total_vagas': len(vagas_simples)
        }
        
        print(f"DEBUG SIMPLES: Retornando resultado")
        return resultado
        
    except Exception as e:
        print(f"DEBUG SIMPLES: Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")
