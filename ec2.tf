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

  user_data = <<-EOF
#!/bin/bash

sudo apt-get update
sudo apt-get install -y docker.io git

sudo systemctl start docker
sudo systemctl enable docker

# Clonar o repositório do GitHub
git clone https://github.com/fabiolucasz/clinica-api.git

# Entrar no projeto
cd clinica-api

# Criar arquivo de variáveis de ambiente
cat <<ENVEOF > .env
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

# Construir a imagem
sudo docker build -t clinica-api .

# Executar o container
sudo docker run -d \
  --name clinica-api-container \
  --restart always \
  --env-file .env \
  -p 8001:8001 \
  clinica-api
EOF
}
