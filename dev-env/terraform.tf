terraform {
    required_providers {
        aws = {
            source  = "hashicorp/aws"
            version = ">= 5.79.0"
        }
        helm = {
            source = "hashicorp/helm"
            version = "~> 2.12"
        }
        kubernetes = {
            source = "hashicorp/kubernetes"
            version = "~> 2.24"
        }
    }

    required_version = ">= 1.2.0"
}

# configures a specified provider
provider "aws" {
    region = var.aws_region
    profile = var.aws_profile
}

# used to deploy packages in kubernetes
provider "helm" {
    kubernetes {
        host = module.eks.cluster_endpoint
        cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
        exec {
            api_version = "client.authentication.k8s.io/v1beta1"
            args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
            command     = "aws"
        }
        # config_path = "~/.kube/config"
    }
}

provider "kubernetes" {
    host = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    exec {
        api_version = "client.authentication.k8s.io/v1beta1"
        args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
        command     = "aws"
    }
}