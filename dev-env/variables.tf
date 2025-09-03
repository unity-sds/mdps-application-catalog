
variable "vpc_name" {
    type = string
    default = "Unity-Dev-VPC"
}

# AWS OpenSearch
variable os_username {
    type = string
    sensitive = true
}

variable os_port {
    type = number
}

variable "aws_cert_arn" {
    type = string
}

variable "aws_region" {
    type = string
    default = "us-west-2"
}

# AWS Route53
variable "zone_name" {
    type = string
    description = "route53 zone name"
}


# RabbitMQ
variable "rabbit_mq_username" {
    type        = string
    description = "RabbitMQ Username"
    sensitive   = true
}

# COMMON
variable "namespace" {
    type = string
    description = "namespace for app and ingress"
}

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