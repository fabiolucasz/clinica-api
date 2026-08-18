data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  owners = ["099720109477"] # Canonical
}

resource "aws_instance" "clinica-api" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.allow_ssh_http.id]

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
git clone https://github.com/fabiolucasz/clinica-api.git /app

# Construir e executar o contêiner Docker na porta 8001
cd /app
sudo docker build -t clinica-api .
sudo docker run -d -p 8001:8001 clinica-api
EOF
}