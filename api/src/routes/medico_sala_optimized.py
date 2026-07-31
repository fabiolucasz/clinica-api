from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..deps.user import CurrentUser, get_db
from ..models.models import Salas, User, Vagas

router = APIRouter(prefix="/medico-sala", tags=["medico-sala-optimized"])


@router.get("/optimized/{medico_id}")
async def get_medico_sala_optimized(
    medico_id: int,
    current_user: CurrentUser,
    clinica_id: int = 1,
    db: Session = Depends(get_db),
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

        # Coletar IDs únicos de médicos e salas das vagas
        medicos_ids = set()
        salas_ids = set()
        for vaga in vagas:
            if vaga.sala and vaga.sala != 0:
                salas_ids.add(vaga.sala)
            for dia in ["segunda", "terca", "quarta", "quinta", "sexta"]:
                medico_id_vaga = getattr(vaga, dia)
                if medico_id_vaga and medico_id_vaga != 0:
                    medicos_ids.add(medico_id_vaga)

        print(f"DEBUG: Medicos IDs encontrados nas vagas: {medicos_ids}")
        print(f"DEBUG: Salas IDs encontrados nas vagas: {salas_ids}")

        # Buscar todos os médicos necessários em lote
        medicos_nomes = {}
        if medicos_ids:
            print(f"DEBUG: Buscando {len(medicos_ids)} médicos em lote")
            medicos_db = db.query(User).filter(User.id.in_(medicos_ids)).all()
            medicos_nomes = {med.id: med.nome for med in medicos_db}
            print(f"DEBUG: Nomes de médicos encontrados: {medicos_nomes}")

        # Buscar todos os nomes das salas em lote
        salas_nomes = {}
        if salas_ids:
            print(f"DEBUG: Buscando {len(salas_ids)} salas em lote")
            salas_db = db.query(Salas).filter(Salas.id.in_(salas_ids)).all()
            salas_nomes = {sala.id: sala.nome for sala in salas_db}
            print(f"DEBUG: Nomes de salas encontrados: {salas_nomes}")

        # Enriquecer vagas com nomes dos médicos
        vagas_enriquecidas = []
        for vaga in vagas:
            vaga_dict = {
                "id": vaga.id,
                "sala_id": vaga.sala,
                "sala_nome": salas_nomes.get(vaga.sala, f"Sala {vaga.sala}"),
                "turno": vaga.turno,
                "max_pacientes": vaga.max_pacientes,
                "pacientes_atuais": vaga.pacientes_atuais,
            }

            # Adicionar médicos e nomes
            for dia in ["segunda", "terca", "quarta", "quinta", "sexta"]:
                medico_id_vaga = getattr(vaga, dia)
                vaga_dict[dia] = (
                    medico_id_vaga if medico_id_vaga and medico_id_vaga != 0 else None
                )
                vaga_dict[f"{dia}_nome"] = (
                    medicos_nomes.get(medico_id_vaga)
                    if medico_id_vaga and medico_id_vaga != 0
                    else None
                )

            vagas_enriquecidas.append(vaga_dict)

        print(f"DEBUG: {len(vagas_enriquecidas)} vagas enriquecidas")

        # Retornar resposta otimizada
        return {
            "medico": {
                "id": medico.id,
                "nome": medico.nome,
                "email": medico.email,
                "celular": medico.celular,
                "cpf": medico.cpf,
                "role": medico.role,
            },
            "vagas": vagas_enriquecidas,
            "clinica": {
                "id": clinica_id,
                "nome": "Clínica Padrão",  # Pode ser dinâmico se necessário
            },
            "total_vagas": len(vagas_enriquecidas),
        }

    except Exception as e:
        print(f"DEBUG: Erro no endpoint: {e!s}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Erro ao buscar dados otimizados: {e!s}"
        )
