terraform {
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
    region = var.aws_region
    profile = var.aws_profile
}

provider "kubernetes" {
    host = data.aws_eks_cluster.main.endpoint #module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.main.certificate_authority[0].data) #base64decode(module.eks.cluster_certificate_authority_data)
    # mutually exclusive with exec
    token = data.aws_eks_cluster_auth.main.token
    exec {
        api_version = "client.authentication.k8s.io/v1beta1"
        command     = "aws"
        args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name, "--output", "json"]
    }
    config_path = "~/.kube/config"
}

# used to deploy packages in kubernetes
provider "helm" {
    kubernetes {
        host = data.aws_eks_cluster.main.endpoint #module.eks.cluster_endpoint
        cluster_ca_certificate = base64decode(data.aws_eks_cluster.main.certificate_authority[0].data) #base64decode(module.eks.cluster_certificate_authority_data)
        # mutually exclusive with exec
        token = data.aws_eks_cluster_auth.main.token
        exec {
            api_version = "client.authentication.k8s.io/v1beta1"
            command     = "aws"
            args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name, "--output", "json"]
        }
        config_path = "~/.kube/config"
    }
}

