from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from src.database.connection import Base


# Model Calendario (tabela de datas)
class Calendario(Base):
    __tablename__ = "calendario"

    id = Column(
        Integer, primary_key=True, index=True, nullable=False, autoincrement=True
    )
    data_iso = Column(String(10), unique=True, nullable=False)  # YYYY-MM-DD
    data_br = Column(String(10), nullable=False)  # DD/MM/YYYY
    data_datetime = Column(DateTime, nullable=False)
    ano = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    dia = Column(Integer, nullable=False)
    dia_semana = Column(Integer, nullable=False)  # 0=domingo, 6=sábado
    dia_semana_nome = Column(String(20), nullable=False)
    mes_nome = Column(String(20), nullable=False)
    bimestre = Column(Integer, nullable=False)
    trimestre = Column(Integer, nullable=False)
    quadrimestre = Column(Integer, nullable=False)
    semestre = Column(Integer, nullable=False)
    semana_ano = Column(Integer, nullable=False)
    dia_util = Column(Boolean, default=True)  # True para segunda-sexta

    calendario_clinica = relationship("CalendarioClinica", back_populates="calendario")


class Turnos(Base):
    __tablename__ = "turnos"

    id = Column(
        Integer, primary_key=True, index=True, nullable=False, autoincrement=True
    )
    nome = Column(String(100), unique=True)
    hora_inicio = Column(String(5), nullable=False)
    hora_fim = Column(String(5), nullable=False)

    # Relacionamento com horários de consultas
    horarios_consultas = relationship("HorariosConsultas", back_populates="turno_rel")


class Estados(Base):
    __tablename__ = "estados"

    id = Column(
        Integer, primary_key=True, index=True, nullable=False, autoincrement=True
    )
    nome = Column(String(100), unique=True)
    uf = Column(String(2), unique=True)


class Especialidades(Base):
    __tablename__ = "especialidades"

    id = Column(
        Integer, primary_key=True, index=True, nullable=False, autoincrement=True
    )
    nome = Column(String(100), unique=True)


class Tipo_conselho(Base):
    __tablename__ = "tipo_conselho"

    id = Column(
        Integer, primary_key=True, index=True, nullable=False, autoincrement=True
    )
    nome = Column(String(100), unique=True)


# Model User (depende de Estados)
class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer, primary_key=True, index=True, nullable=False, autoincrement=True
    )
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    # Identificação
    nome = Column(String(100))
    celular = Column(String(20), unique=True)
    cpf = Column(String(14), unique=True)
    data_nascimento = Column(String(12))
    sexo = Column(String(10))
    cep = Column(String(9))

    # Endereço
    rua = Column(String(200))
    numero = Column(String(10))
    bairro = Column(String(100))
    cidade = Column(String(100))
    estado = Column(Integer, ForeignKey("estados.id"))

    # Perfil
    foto_perfil = Column(String(200), nullable=True)
    especialidade = Column(Integer, ForeignKey("especialidades.id"), nullable=True)
    rqe = Column(String(20), nullable=True, unique=True)
    valor_consulta = Column(Float, nullable=True)
    role = Column(String(20), default="paciente")

    # Documentos
    tipo_conselho = Column(Integer, ForeignKey("tipo_conselho.id"), nullable=True)
    uf_conselho = Column(Integer, ForeignKey("estados.id"), nullable=True)
    numero_conselho = Column(String(20), nullable=True, unique=True)
    upload_arquivo = Column(String(200), nullable=True)

    # Metadados
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    vagas_segunda = relationship("Vagas", foreign_keys="Vagas.segunda", back_populates="medico_segunda")
    vagas_terca = relationship("Vagas", foreign_keys="Vagas.terca", back_populates="medico_terca")
    vagas_quarta = relationship("Vagas", foreign_keys="Vagas.quarta", back_populates="medico_quarta")
    vagas_quinta = relationship("Vagas", foreign_keys="Vagas.quinta", back_populates="medico_quinta")
    vagas_sexta = relationship("Vagas", foreign_keys="Vagas.sexta", back_populates="medico_sexta")

    agendamentos_paciente = relationship(
        "Agendamentos", foreign_keys="Agendamentos.paciente", back_populates="paciente_rel"
    )
    agendamentos_medico = relationship(
        "Agendamentos", foreign_keys="Agendamentos.medico", back_populates="medico_rel"
    )
    estado_rel = relationship("Estados", foreign_keys=[estado])
    uf_conselho_rel = relationship("Estados", foreign_keys=[uf_conselho])
    especialidade_rel = relationship("Especialidades", foreign_keys=[especialidade])
    tipo_conselho_rel = relationship("Tipo_conselho", foreign_keys=[tipo_conselho])


# Model Clinicas (depende de Estados)
class Clinicas(Base):
    __tablename__ = "clinicas"

    # Identificação
    id = Column(
        Integer, primary_key=True, index=True, nullable=False, autoincrement=True
    )
    nome = Column(String(100))
    cnpj = Column(String(18), default="00.000.000/0000-00", unique=True)
    email = Column(String(100), unique=True)
    celular = Column(String(20), unique=True)
    celular2 = Column(String(20), nullable=True, unique=True)

    # Endereço
    cep = Column(String(9))
    rua = Column(String(200))
    numero = Column(String(10))
    bairro = Column(String(100))
    cidade = Column(String(100))
    estado = Column(Integer, ForeignKey("estados.id"))

    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    estado_rel = relationship("Estados")
    salas = relationship("Salas", back_populates="clinica_rel")
    vagas = relationship("Vagas", back_populates="clinica_rel")
    agendamentos = relationship("Agendamentos", back_populates="clinica_rel")
    calendario_clinica = relationship("CalendarioClinica", back_populates="clinica")


# Model Salas (depende de Clinicas)
class Salas(Base):
    __tablename__ = "salas"

    id = Column(
        Integer, primary_key=True, index=True, nullable=False, autoincrement=True
    )
    nome = Column(String(100))
    clinica = Column(Integer, ForeignKey("clinicas.id"))

    clinica_rel = relationship("Clinicas", back_populates="salas")
    vagas = relationship("Vagas", back_populates="sala_rel")
    agendamentos = relationship("Agendamentos", back_populates="sala_rel")

    __table_args__ = (UniqueConstraint("nome", "clinica", name="uq_sala_nome_clinica"),)


# Model Vagas (depende de Clinicas, Salas e User)
class Vagas(Base):
    __tablename__ = "vagas"
    id = Column(
        Integer, primary_key=True, index=True, nullable=False, autoincrement=True
    )

    clinica = Column(Integer, ForeignKey("clinicas.id"))
    sala = Column(Integer, ForeignKey("salas.id"))

    status = Column(String(10), default="disponivel")
    turno = Column(Integer, ForeignKey("turnos.id"))

    segunda = Column(Integer, ForeignKey("users.id"), nullable=True)
    terca = Column(Integer, ForeignKey("users.id"), nullable=True)
    quarta = Column(Integer, ForeignKey("users.id"), nullable=True)
    quinta = Column(Integer, ForeignKey("users.id"), nullable=True)
    sexta = Column(Integer, ForeignKey("users.id"), nullable=True)

    max_pacientes = Column(Integer, default=25)
    pacientes_atuais = Column(Integer, default=0)

    clinica_rel = relationship("Clinicas", back_populates="vagas")
    sala_rel = relationship("Salas", back_populates="vagas")
    turno_rel = relationship("Turnos")
    medico_segunda = relationship("User", foreign_keys=[segunda], back_populates="vagas_segunda")
    medico_terca = relationship("User", foreign_keys=[terca], back_populates="vagas_terca")
    medico_quarta = relationship("User", foreign_keys=[quarta], back_populates="vagas_quarta")
    medico_quinta = relationship("User", foreign_keys=[quinta], back_populates="vagas_quinta")
    medico_sexta = relationship("User", foreign_keys=[sexta], back_populates="vagas_sexta")

    __table_args__ = (UniqueConstraint("sala", "turno"),)


class CalendarioClinica(Base):
    __tablename__ = "calendario_clinica"

    id = Column(Integer, primary_key=True)
    clinica_id = Column(Integer, ForeignKey("clinicas.id"))
    data_feriado = Column(Integer, ForeignKey("calendario.id"))

    nome_feriado = Column(String(100))
    aberta = Column(Boolean, default=True)

    clinica = relationship("Clinicas", back_populates="calendario_clinica")
    calendario = relationship("Calendario", back_populates="calendario_clinica")


# Model Agendamentos (depende de todos os anteriores)
class Agendamentos(Base):
    __tablename__ = "agendamentos"

    id = Column(
        Integer, primary_key=True, index=True, nullable=False, autoincrement=True
    )

    clinica = Column(Integer, ForeignKey("clinicas.id"))
    sala = Column(Integer, ForeignKey("salas.id"))
    paciente = Column(Integer, ForeignKey("users.id"))
    medico = Column(Integer, ForeignKey("users.id"))

    data_consulta = Column(DateTime, default=datetime.now(UTC))
    turno = Column(Integer, ForeignKey("turnos.id"))
    hora_inicio = Column(String(5), nullable=False)
    hora_fim = Column(String(5), nullable=False)
    status = Column(String(10), default="agendado")

    clinica_rel = relationship("Clinicas", back_populates="agendamentos")
    sala_rel = relationship("Salas", back_populates="agendamentos")
    turno_rel = relationship("Turnos")
    paciente_rel = relationship("User", foreign_keys=[paciente], back_populates="agendamentos_paciente")
    medico_rel = relationship("User", foreign_keys=[medico], back_populates="agendamentos_medico")


# Model HorariosConsultas
class HorariosConsultas(Base):
    __tablename__ = "horarios_consultas"

    id = Column(
        Integer, primary_key=True, index=True, nullable=False, autoincrement=True
    )
    hora_inicio = Column(String(5), nullable=False)  # Formato HH:MM
    hora_fim = Column(String(5), nullable=False)  # Formato HH:MM
    turno = Column(Integer, ForeignKey("turnos.id"), nullable=False)

    # Relacionamento
    turno_rel = relationship("Turnos", back_populates="horarios_consultas")
