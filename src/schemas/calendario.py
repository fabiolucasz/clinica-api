from datetime import datetime

from pydantic import BaseModel


class Calendario(BaseModel):
    id: int
    data_iso: str
    data_br: str
    data_datetime: datetime
    ano: int
    mes: int
    dia: int
    dia_semana: int
    dia_semana_nome: str
    mes_nome: str
    bimestre: int
    trimestre: int
    quadrimestre: int
    semestre: int
    semana_ano: int

    model_config = {"from_attributes": True}
