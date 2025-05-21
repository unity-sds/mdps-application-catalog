variable "rabbit_mq_username" {
    type        = string
    description = "RabbitMQ Username"
    senstive    = true
}

variable "rabbit_mq_password" {
    type        = string
    description = "RabbitMQ password"
    sensitive   = true
}