variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-west-2"
}

variable "vpc_name" {
    type = string
    default = "Unity-Dev-VPC"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "mdps-artifact-catalog"
}

variable "container_registry" {
  description = "The container registry to which containers are pushed to."
  type = string
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "Name of the database"
  type        = string
  default     = "artifact_catalog"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

variable "container_image" {
  description = "Docker image for the application"
  type        = string
}

variable "task_cpu" {
  description = "CPU units for the ECS task"
  type        = number
  default     = 256
}

variable "task_memory" {
  description = "Memory for the ECS task"
  type        = number
  default     = 512
}

variable "service_desired_count" {
  description = "Number of instances of the task to run"
  type        = number
  default     = 1
}

variable "secret_key" {
  description = "Secret key for the application"
  type        = string
  sensitive   = true
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Environment = "production"
    Project     = "mdps-artifact-catalog"
  }
} 