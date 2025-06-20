#VPC
variable "vpc_id" {
    type = string
    description = "vpc id"
    sensitive = true
}

# AWS OpenSearch
variable os_username {
    type = string
    sensitive = true
}

variable os_password {
    type = string
    sensitive = true
}

# AWS EKS
variable "account_id" {
    type = string
    description = "aws account id"
    sensitive = true
}
variable "ami_id" {
    type = string
    description = "ami id"
    sensitive = true
}

# AWS RDS 
variable "aws_region" {
    type        = string
    description = "aws region"
    default     = "us-west-2"
}

variable "aws_profile" {
    type = string
    description = "aws credentials profile"
    default = "mdps-venue-dev"
}

# Postgres
variable "db_password" {
    type        = string
    description = "db password"
    sensitive   = true
    default = "inveniopostgres"
}

# RabbitMQ
variable "rabbit_mq_username" {
    type        = string
    description = "RabbitMQ Username"
    sensitive   = true
    default = "inveniorabbitmq"
}

variable "rabbit_mq_password" {
    type        = string
    description = "RabbitMQ password"
    sensitive   = true
    default = "inveniorabbitpq"
}

# COMMON
variable "namespace" {
    type = string
    description = "namespace for app and ingress"
    default = "app-catalog-dev"
}