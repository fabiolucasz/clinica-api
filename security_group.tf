resource "aws_security_group" "allow_ssh_http" {
  name        = "clinica-medica-api-sg"
  description = "Allow SSH (port 22) and API (port 8001) inbound traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH Access"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Clinica API Access"
    from_port   = 8001
    to_port     = 8001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name    = "clinica-medica-api-sg"
    Project = "clinica-medica-api"
  }
}

