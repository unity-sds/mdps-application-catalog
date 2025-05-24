terraform {
    required_providers {
        aws = {
            source  = "hashicorp/aws"
            version = "~> 4.16"
        }
    }

    required_version = ">= 1.2.0"
}

# configures a specified provider
provider "aws" {
    region = var.aws_region
}

# used to deploy packages in kubernetes
provider "helm" {
    kubernetes {
        host = module.eks.cluster_endpoint
        cluster_ca_certificate = base64decode(module.eks.cluster_ca_certificate)
        exec {
            api_version = "client.authentication.k8s.io/v1beta1"
            args        = ["eks", "get-token", "--cluster-name", data.aws_eks_cluster.cluster.name]
            command     = "aws"
        }
        # config_path = "~/.kube/config"
    }
}