FROM python:3.12-slim

# Diretório de trabalho
COPY ./api /app
WORKDIR /app

# Instalar dependências Python
RUN pip install uv

RUN uv sync

# Expor porta
EXPOSE 8001

# Comando para rodar a aplicação
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
