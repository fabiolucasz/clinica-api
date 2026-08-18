terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.61.0"
    }
  }
  backend "s3" {
    # Lembre de trocar o bucket para o seu, não pode ser o mesmo nome
    bucket = "clinica-api-fabiolucasz-bucket-state"
    # dynamodb_table = "terraform-locks"
    key     = "clinica-api-fabiolucasz-terraform-test.tfstate"
    region  = "us-east-1"
    encrypt = true # Ativa a criptografia
  }
}

provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = {
      Project     = "clinica-medica-api"
      Environment = "production"
      ManagedBy   = "Terraform"
    }
  }
}