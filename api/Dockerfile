FROM python:3.12-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivo de dependências
COPY pyproject.toml ./

# Instalar dependências Python
RUN pip install --no-cache-dir -e .

# Copiar código fonte
COPY src/ ./src/

# Criar diretório para o banco de dados
RUN mkdir -p /app/src

# Expor porta
EXPOSE 8001

# Comando para rodar a aplicação
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
