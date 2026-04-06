from fastapi import FastAPI
from src.routes.user import router as auth_user_router
from src.routes.auth_external import router as auth_external_router
from src.routes.estados import router as estados_router
from src.routes.especialidades import router as especialidades_router
from src.routes.tipo_conselho import router as tipo_conselho_router
from src.routes.clinicas import router as clinicas_router
from src.routes.salas import router as salas_router
from src.routes.vagas import router as vagas_router
from src.routes.agendamentos import router as agendamentos_router
from src.routes.calendario_clinica import router as calendario_clinica_router
from src.metrics.auth_user import metrics_endpoint
from src.database.connection import engine, Base
from src.populate_db import populate_database



app = FastAPI()

# Criar tabelas
Base.metadata.create_all(bind=engine)

# Popular banco com dados iniciais
populate_database()

@app.get("/")
async def home():
    return {
        "message": "Welcome to the Clinica API",
        "version": "1.0.0",
        "endpoints": {
            "auth": {
                "login_form": "/login/access-token",
                "login_json": "/auth/login-json",
                "validate_token": "/auth/validate-token",
                "signup": "/signup"
            },
            "user": {
                "me": "/users/me"
            },
            "monitoring": {
                "metrics": "/metrics",
                "docs": "/docs"
            }
        }
    }

@app.get("/metrics")
async def metrics():
    """Endpoint Prometheus para métricas"""
    return metrics_endpoint()

app.include_router(auth_user_router, tags=["Auth Users"])
app.include_router(auth_external_router, tags=["Auth External"])
app.include_router(estados_router, tags=["Estados"])
app.include_router(especialidades_router, tags=["Especialidades"])
app.include_router(tipo_conselho_router, tags=["Tipo Conselho"])
app.include_router(clinicas_router, tags=["Clinicas"])
app.include_router(salas_router, tags=["Salas"])
app.include_router(vagas_router, tags=["Vagas"])
app.include_router(agendamentos_router, tags=["Agendamentos"])
app.include_router(calendario_clinica_router, tags=["Calendario Clinica"])





