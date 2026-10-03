from datetime import datetime

from pydantic import BaseModel, EmailStr

# User schemas


class UserBase(BaseModel):

    email: EmailStr


class UserCreate(UserBase):
    password: str

    # Identificação
    nome: str
    celular: str
    cpf: str
    data_nascimento: str
    sexo: str
    cep: str | None = None

    # Endereço
    rua: str | None = None
    numero: str | None = None
    bairro: str | None = None
    cidade: str | None = None
    estado: int = 19

    foto_perfil: str
    role: str = "paciente"


class UserUpdate(BaseModel):

    nome: str | None = None

    celular: str | None = None

    data_nascimento: str | None = None

    sexo: str | None = None

    cep: str | None = None

    rua: str | None = None

    numero: str | None = None

    bairro: str | None = None

    cidade: str | None = None

    estado: int | None = None

    foto_perfil: str | None = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    nome: str | None = None
    celular: str | None = None
    cpf: str | None = None
    data_nascimento: str | None = None
    sexo: str | None = None
    cep: str | None = None
    rua: str | None = None
    numero: str | None = None
    bairro: str | None = None
    cidade: str | None = None
    estado: int | None = None
    role: str | None = None
    foto_perfil: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_config = {"from_attributes": True}


class MedicoCreate(UserBase):
    password: str
    # Identificação
    nome: str
    celular: str
    cpf: str
    data_nascimento: str
    sexo: str
    cep: str | None = None
    # Endereço
    rua: str | None = None
    numero: str | None = None
    bairro: str | None = None
    cidade: str | None = None
    estado: int = 19
    # Perfil
    especialidade: int = 1
    rqe: str
    valor_consulta: float
    role: str = "medico"
    foto_perfil: str | None = None
    # Documentos
    tipo_conselho: int = 1
    uf_conselho: int = 19
    numero_conselho: str
    upload_arquivo: str | None = None


class MedicoUpdate(UserUpdate):
    especialidade: int | None = None
    rqe: str | None = None
    valor_consulta: float | None = None
    role: str = "medico"

    tipo_conselho: int | None = None
    uf_conselho: int | None = None
    numero_conselho: int | None = None
    upload_arquivo: str | None = None


class MedicoResponse(UserBase):
    id: int
    is_active: bool
    nome: str | None = None
    celular: str | None = None
    cpf: str | None = None
    data_nascimento: str | None = None
    sexo: str | None = None
    cep: str | None = None
    rua: str | None = None
    numero: str | None = None
    bairro: str | None = None
    cidade: str | None = None
    estado: int | None = None
    role: str | None = None
    foto_perfil: str | None = None
    especialidade: int | None = None
    rqe: str | None = None
    valor_consulta: float | None = None
    tipo_conselho: int | None = None
    uf_conselho: int | None = None
    numero_conselho: str | None = None
    upload_arquivo: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_config = {"from_attributes": True}


class Token(BaseModel):

    access_token: str

    token_type: str = "bearer"


class TokenPayload(BaseModel):

    sub: int | None = None
