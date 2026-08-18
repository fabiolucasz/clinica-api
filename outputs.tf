output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.clinica-api.public_ip
}

output "instance_public_dns" {
  description = "Public DNS of the EC2 instance"
  value       = aws_instance.clinica-api.public_dns
}

output "vpc_id" {
  description = "ID of the created VPC"
  value       = aws_vpc.main.id
}
