"""
Módulo de integração com Supabase Storage para upload de arquivos.
"""
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
import os
from typing import Optional
import filetype
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# Configuração do Supabase S3
SUPABASE_STORAGE_URL = os.environ.get("SUPABASE_STORAGE_URL")
SUPABASE_S3_ENDPOINT = os.environ.get("SUPABASE_S3_ENDPOINT")
SUPABASE_ACCESS_KEY = os.environ.get("SUPABASE_ACCESS_KEY")
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY")
SUPABASE_REGION = os.environ.get("SUPABASE_REGION")
BUCKET_NAME = os.environ.get("SUPABASE_BUCKET")


# Limites de tamanho
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_PDF_SIZE = 10 * 1024 * 1024   # 10MB

# Tipos MIME permitidos
ALLOWED_IMAGE_TYPES = {
    'image/png': '.png',
    'image/jpeg': '.jpg',
    'image/jpg': '.jpg',
}

ALLOWED_DOCUMENT_TYPES = {
    'application/pdf': '.pdf',
}

ALLOWED_TYPES = {**ALLOWED_IMAGE_TYPES, **ALLOWED_DOCUMENT_TYPES}


def get_s3_client():
    """Retorna cliente S3 configurado para Supabase Storage."""
    return boto3.client(
        's3',
        endpoint_url=SUPABASE_S3_ENDPOINT,
        aws_access_key_id=SUPABASE_ACCESS_KEY,
        aws_secret_access_key=SUPABASE_SECRET_KEY,
        region_name=SUPABASE_REGION,
        config=Config(signature_version='s3v4')
    )


def validate_file(file_content: bytes, allowed_types: Optional[dict] = None) -> tuple[bool, str, str]:
    """
    Valida o arquivo verificando tipo e tamanho.
    
    Returns:
        tuple: (is_valid, error_message, file_extension)
    """
    if allowed_types is None:
        allowed_types = ALLOWED_TYPES
    
    # Detectar tipo MIME
    kind = filetype.guess(file_content)
    mime_type = kind.mime if kind else None
    
    if not mime_type or mime_type not in allowed_types:
        allowed_list = ", ".join(allowed_types.keys())
        return False, f"Tipo de arquivo não permitido. Tipos aceitos: {allowed_list}", ""
    
    # Verificar tamanho
    file_size = len(file_content)
    extension = allowed_types[mime_type]
    
    if mime_type in ALLOWED_IMAGE_TYPES and file_size > MAX_IMAGE_SIZE:
        return False, f"Imagem muito grande. Tamanho máximo: 5MB", extension
    
    if mime_type in ALLOWED_DOCUMENT_TYPES and file_size > MAX_PDF_SIZE:
        return False, f"PDF muito grande. Tamanho máximo: 10MB", extension
    
    return True, "", extension


def upload_file(
    file_content: bytes, 
    user_id: int, 
    file_type: str = "image",
    folder: str = "profiles"
) -> tuple[bool, str, Optional[str]]:
    """
    Faz upload de arquivo para o Supabase Storage.
    
    Args:
        file_content: Conteúdo do arquivo em bytes
        user_id: ID do usuário para criar pasta estruturada
        file_type: "image" ou "document"
        folder: Pasta base (profiles, documents, etc)
    
    Returns:
        tuple: (success, message, file_url)
    """
    try:
        # Validar arquivo
        if file_type == "image":
            is_valid, error_msg, extension = validate_file(file_content, ALLOWED_IMAGE_TYPES)
        else:
            is_valid, error_msg, extension = validate_file(file_content, ALLOWED_DOCUMENT_TYPES)
        
        if not is_valid:
            return False, error_msg, None
        
        # Criar caminho estruturado: user_{id}/{folder}/{timestamp}_{random}.{ext}
        import time
        import uuid
        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{unique_id}{extension}"
        key = f"user_{user_id}/{folder}/{filename}"
        
        # Upload para Supabase
        s3 = get_s3_client()
        kind = filetype.guess(file_content)
        mime_type = kind.mime if kind else 'application/octet-stream'
        
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=file_content,
            ContentType=mime_type,
        )
        
        # Construir URL pública
        file_url = f"{SUPABASE_STORAGE_URL}/storage/v1/object/public/{BUCKET_NAME}/{key}"
        
        return True, "Upload realizado com sucesso", file_url
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        return False, f"Erro no upload: {error_code} - {error_msg}", None
    except Exception as e:
        return False, f"Erro inesperado: {str(e)}", None


def delete_file(file_url: str) -> tuple[bool, str]:
    """
    Remove arquivo do Supabase Storage.
    
    Args:
        file_url: URL completa do arquivo
    
    Returns:
        tuple: (success, message)
    """
    try:
        # Extrair key da URL
        base_url = f"{SUPABASE_STORAGE_URL}/storage/v1/object/public/{BUCKET_NAME}/"
        key = file_url.replace(base_url, "")
        
        s3 = get_s3_client()
        s3.delete_object(Bucket=BUCKET_NAME, Key=key)
        
        return True, "Arquivo removido com sucesso"
        
    except ClientError as e:
        return False, f"Erro ao remover: {str(e)}"
    except Exception as e:
        return False, f"Erro inesperado: {str(e)}"
