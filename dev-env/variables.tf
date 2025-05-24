# AWS RDS 
variable "aws_region" {
    type        = string
    description = "aws region"
    default     = "us-west-2"
}

# Postgres
variable "db_password" {
    type        = string
    description = "db password"
    sensitive   = true
}

# RabbitMQ
variable "rabbit_mq_username" {
    type        = string
    description = "RabbitMQ Username"
    sensitive   = true
}

variable "rabbit_mq_password" {
    type        = string
    description = "RabbitMQ password"
    sensitive   = true
}