from pydantic import BaseModel, EmailStr
from datetime import datetime

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
    cep: str
    rua: str
    numero: str
    bairro: str
    cidade: str
    estado: int = 1
    role: str = 'paciente'
    
    # Perfil (opcional)
    foto_perfil: str | None = None
    especialidade: int = 1
    rqe: str | None = None
    valor_consulta: float = 150
    
    # Documentos (opcional)
    tipo_conselho: int = 1
    uf_conselho: int = 1
    numero_conselho: str | None = None
    upload_arquivo: str | None = None

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
    especialidade: int | None = None
    rqe: str | None = None
    valor_consulta: float | None = None
    tipo_conselho: int | None = None
    uf_conselho: int | None = None
    numero_conselho: str | None = None

class User(UserBase):
    id: int
    is_active: bool
    foto_perfil: str | None = None
    especialidade: int | None = None
    rqe: str | None = None
    valor_consulta: float | None = None
    tipo_conselho: int | None = None
    uf_conselho: int | None = None
    numero_conselho: str | None = None
    upload_arquivo: str | None = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}
    
class PacienteBase(BaseModel):
    nome: str
    email: EmailStr
    celular: str
    cpf: str
    data_nascimento: str
    sexo: str
    cep: str
    rua: str
    numero: str
    bairro: str
    cidade: str
    estado: int
    role: str
    foto_perfil: str | None = None
    
class PacienteCreate(PacienteBase):
    password: str
    
class PacienteUpdate(PacienteBase):
    pass

class PacienteResponse(PacienteBase):
    id: int

    
    model_config = {"from_attributes": True}
    
class MedicoBase(BaseModel):
    nome: str
    email: EmailStr
    celular: str
    cpf: str
    data_nascimento: str
    sexo: str
    cep: str
    rua: str
    numero: str
    bairro: str
    cidade: str
    estado: int = 1
    role: str = 'medico'
    
    # Perfil profissional (opcional)
    foto_perfil: str | None = None
    especialidade: int | None = None
    rqe: str | None = None
    valor_consulta: float | None = None
    
    # Documentos (opcional)
    tipo_conselho: int | None = None
    uf_conselho: int | None = None
    numero_conselho: str | None = None
    upload_arquivo: str | None = None

class MedicoCreate(MedicoBase):
    password: str

class MedicoUpdate(MedicoBase):
    pass

class MedicoResponse(MedicoBase):
    id: int
    nome: str
    email: EmailStr
    celular: str
    cpf: str
    data_nascimento: str
    sexo: str
    cep: str
    rua: str
    numero: str
    bairro: str
    cidade: str
    estado: int
    role: str
    foto_perfil: str | None = None
    especialidade: int | None = None
    rqe: str | None = None
    valor_consulta: float | None = None
    tipo_conselho: int | None = None
    uf_conselho: int | None = None
    numero_conselho: str | None = None
    upload_arquivo: str | None = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: int | None = None
