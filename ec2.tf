data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  owners = ["099720109477"] # Canonical
}

resource "aws_instance" "clinica-api" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.allow_ssh_http.id]
  user_data_replace_on_change = true

  tags = {
    Name    = "clinica-medica-api-ec2"
    Project = "clinica-medica-api"
  }

  user_data_base64 = base64encode(<<-EOF
#!/bin/bash
exec > >(tee /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1
echo "Starting Cloud-Init setup for Clinica API..."

# 1. Atualizar pacotes do sistema e instalar dependências (Docker e Git)
sudo apt-get update -y
sudo apt-get install -y docker.io git

# 2. Iniciar e habilitar o serviço Docker
sudo systemctl start docker
sudo systemctl enable docker

# 3. Clonar o repositório do GitHub na pasta raiz
git clone https://github.com/fabiolucasz/clinica-api.git

# 4. Criar o arquivo .env com as variáveis de ambiente passadas pelo Terraform / GitHub Actions
cat <<ENVEOF > clinica-api/.env
SECRET_KEY=${var.secret_key}
ALGORITHM=${var.algorithm}
ACCESS_TOKEN_EXPIRE_MINUTES=${var.access_token_expire_minutes}
DOMAIN=${var.domain}
ENVIRONMENT=${var.environment}
DATABASE_URL=${var.database_url}
SUPABASE_STORAGE_URL=${var.supabase_storage_url}
SUPABASE_S3_ENDPOINT=${var.supabase_s3_endpoint}
SUPABASE_ACCESS_KEY=${var.supabase_access_key}
SUPABASE_SECRET_KEY=${var.supabase_secret_key}
SUPABASE_REGION=${var.supabase_region}
SUPABASE_BUCKET=${var.supabase_bucket}
AI_API_KEY=${var.ai_api_key}
ENVEOF

# 5. Entrar na pasta do projeto, construir a imagem Docker e rodar o container na porta 8001
cd clinica-api
sudo docker build -t clinica-api .
sudo docker rm -f clinica-api-container || true
sudo docker run -d --name clinica-api-container --restart always --env-file ./clinica-api/.env -p 8001:8001 clinica-api

echo "Clinica API deployment completed successfully!"
EOF
  )
}
