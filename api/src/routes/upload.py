"""
Endpoints para upload de arquivos para o Supabase Storage.
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from src.storage.supabase import upload_file, validate_file, ALLOWED_IMAGE_TYPES, ALLOWED_DOCUMENT_TYPES
from src.deps import get_current_user
from src.models import models
from src.database.connection import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter(prefix="/upload", tags=["upload"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/profile-image/{user_id}")
async def upload_profile_image(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Faz upload da foto de perfil do usuário.
    Aceita: PNG, JPEG, JPG (máx 5MB)
    """
    # Verificar permissão (próprio usuário, admin, ou staff pode alterar)
    staff_roles = {'administrador', 'medico', 'atendente'}
    is_staff = current_user.role in staff_roles if current_user.role else False
    if current_user.id != user_id and not is_staff:
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    # Validar extensão do arquivo
    allowed_extensions = {'.png', '.jpg', '.jpeg'}
    file_ext = f".{file.filename.split('.')[-1].lower()}" if '.' in file.filename else ""
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Formato não permitido. Use: PNG, JPEG, JPG"
        )
    
    # Ler conteúdo do arquivo
    content = await file.read()
    
    # Validar arquivo
    is_valid, error_msg, _ = validate_file(content, ALLOWED_IMAGE_TYPES)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Fazer upload
    success, message, url = upload_file(
        file_content=content,
        user_id=user_id,
        file_type="image",
        folder="profiles"
    )
    
    if not success:
        raise HTTPException(status_code=500, detail=message)
    
    # Atualizar URL no banco de dados
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        # Remover foto antiga se existir
        if user.foto_perfil:
            from src.storage.supabase import delete_file
            delete_file(user.foto_perfil)
        
        user.foto_perfil = url
        db.commit()
    
    return JSONResponse({
        "success": True,
        "message": "Foto de perfil atualizada com sucesso",
        "url": url
    })


@router.post("/document/{user_id}")
async def upload_professional_document(
    user_id: int,
    file: UploadFile = File(...),
    document_type: str = Form(...),  # rg, cpf, diploma, certificado, etc
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Faz upload de documentos profissionais do usuário.
    Aceita: PDF (máx 10MB)
    """
    # Verificar permissão (próprio usuário, admin, ou staff pode alterar)
    staff_roles = {'administrador', 'medico', 'atendente'}
    is_staff = current_user.role in staff_roles if current_user.role else False
    if current_user.id != user_id and not is_staff:
        raise HTTPException(status_code=403, detail="Permissão negada")
    
    # Validar extensão
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400, 
            detail="Apenas arquivos PDF são permitidos"
        )
    
    # Ler conteúdo
    content = await file.read()
    
    # Validar
    is_valid, error_msg, _ = validate_file(content, ALLOWED_DOCUMENT_TYPES)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Fazer upload
    folder = f"documents/{document_type}"
    success, message, url = upload_file(
        file_content=content,
        user_id=user_id,
        file_type="document",
        folder=folder
    )
    
    if not success:
        raise HTTPException(status_code=500, detail=message)
    
    # Salvar referência no banco (tabela de documentos ou campo no usuário)
    # Aqui você pode criar uma tabela separada para documentos ou usar um campo JSON
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        # Exemplo: armazenar em um campo JSONB ou tabela relacionada
        # Por enquanto, vamos apenas retornar a URL
        pass
    
    return JSONResponse({
        "success": True,
        "message": "Documento enviado com sucesso",
        "url": url,
        "document_type": document_type
    })


@router.delete("/file")
async def delete_uploaded_file(
    file_url: str,
    current_user: models.User = Depends(get_current_user)
):
    """
    Remove um arquivo do storage.
    """
    from src.storage.supabase import delete_file
    
    success, message = delete_file(file_url)
    
    if not success:
        raise HTTPException(status_code=500, detail=message)
    
    return JSONResponse({
        "success": True,
        "message": message
    })


@router.get("/validate")
async def get_validation_info():
    """
    Retorna informações sobre tipos e tamanhos de arquivos permitidos.
    """
    return {
        "images": {
            "types": ["PNG", "JPEG", "JPG"],
            "mime_types": list(ALLOWED_IMAGE_TYPES.keys()),
            "max_size_mb": 5,
            "extensions": [".png", ".jpg", ".jpeg"]
        },
        "documents": {
            "types": ["PDF"],
            "mime_types": list(ALLOWED_DOCUMENT_TYPES.keys()),
            "max_size_mb": 10,
            "extensions": [".pdf"]
        }
    }
