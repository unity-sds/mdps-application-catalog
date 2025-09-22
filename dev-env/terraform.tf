terraform {
    backend "s3" {
    bucket = "catalya-app-catalog"
    key    = "terraform/rdm/terraform.tfstate"
    region = "us-west-2"
  }
    required_providers {
        aws = {
            source  = "hashicorp/aws"
            version = "5.100.0"
        }
        helm = {
            source = "hashicorp/helm"
            version = "~> 2.16.1"
        }
        kubernetes = {
            source = "hashicorp/kubernetes"
            version = ">= 2.0.0"
        }
    }
    #required_version = ">= 1.2.0"
}

# configures a specified provider
provider "aws" {
    region = "us-west-2"
    // need to define the FIPS endpoints for EFS
    endpoints {
        efs = "https://elasticfilesystem-fips.us-west-2.amazonaws.com"
      }
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  token                  = data.aws_eks_cluster_auth.cluster.token
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
  config_path = "~/.kube/config"
}

provider "helm" {
  debug                  = true
  kubernetes {
    host                   = data.aws_eks_cluster.cluster.endpoint
    token                  = data.aws_eks_cluster_auth.cluster.token
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
    config_path = "~/.kube/config"
  }
}

/*
provider "kubernetes" {
    host = data.aws_eks_cluster.cluster.cluster_endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.cluster_certificate_authority_data)
    # mutually exclusive with exec
    token = data.aws_eks_cluster_auth.cluster_auth.token
    exec {
        api_version = "client.authentication.k8s.io/v1beta1"
        command     = "aws"
        args        = ["eks", "get-token", "--cluster-name", data.aws_eks_cluster.cluster.cluster_name, "--output", "json"]
    }
}

# used to deploy packages in kubernetes
provider "helm" {
    kubernetes {
        host = data.aws_eks_cluster.cluster.cluster_endpoint #module.eks.cluster_endpoint
        cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.cluster_certificate_authority_data) #base64decode(module.eks.cluster_endpoint.certificate_authority[0].data) #base64decode(module.eks.cluster_certificate_authority_data)
        # mutually exclusive with exec
        token = data.aws_eks_cluster_auth.cluster_auth.token
        exec {
            api_version = "client.authentication.k8s.io/v1beta1"
            command     = "aws"
            args        = ["eks", "get-token", "--cluster-name", data.aws_eks_cluster.cluster.cluster_name, "--output", "json"]
        }
    }
}*/

# RabbitMQ Secret
resource "random_password" "rabbitmq_password" {
  length  = 16
  special = true
  upper   = true
  lower   = true
  numeric = true
}

# Store the password in SSM Parameter Store
resource "aws_ssm_parameter" "rabbitmq_password" {
  name  = "/rdm/deployment/rabbitmq_password"
  type  = "SecureString"
  value = random_password.rabbitmq_password.result
}


# OpenSearch Secret
resource "random_password" "opensearch_password" {
  length  = 16
  special = true
  upper   = true
  lower   = true
  numeric = true
}

# Store the password in SSM Parameter Store
resource "aws_ssm_parameter" "opensearch_password" {
  name  = "/rdm/deployment/opensearch_password"
  type  = "SecureString"
  value = random_password.opensearch_password.result
}


# PostGRES Secret
resource "random_password" "postgres_password" {
  length  = 16
  special = true
  upper   = true
  lower   = true
  numeric = true
}

# Store the password in SSM Parameter Store
resource "aws_ssm_parameter" "postgres_password" {
  name  = "/rdm/deployment/postgres_password"
  type  = "SecureString"
  value = random_password.postgres_password.result
}
