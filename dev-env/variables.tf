#VPC
# variable "vpc_id" {
#     type = string
#     description = "vpc id"
#     sensitive = true
# }

# AWS OpenSearch
variable os_username {
    type = string
    sensitive = true
}

variable os_password {
    type = string
    sensitive = true
}

variable os_port {
    type = number
}

# AWS EKS
variable "account_id" {
    type = string
    description = "aws account id"
    sensitive = true
}
# variable "ami_id" {
#     type = string
#     description = "ami id"
#     sensitive = true
# }

# AWS RDS 
variable "aws_region" {
    type        = string
    description = "aws region"
    default     = "us-west-2"
}

variable "aws_profile" {
    type = string
    description = "aws credentials profile"
}

# AWS LB Controller
# variable "irsa_name" {
#     type = string
# }
# variable "irsa_arn" {
#     type = string
# }
variable "aws_cert_arn" {
    type = string
}

# AWS Route53
variable "zone_name" {
    type = string
    description = "route53 zone name"
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

# COMMON
variable "namespace" {
    type = string
    description = "namespace for app and ingress"
}
# variable "app_hostname" {
#     type = string
#     description = "invenio hostname"
# }

# InvenioRDM
variable "invenio_init" {
    type = bool
    description = "initialize components for invenio - true if first time install"
    default = false
}

variable "invenio_hostname" {
    type = string
    description = "Invenio Hostname"
}

variable "chart_path" {
    type = string
    description = "path to local invenio chart"
}