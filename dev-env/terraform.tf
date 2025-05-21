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
    region = "us-west-2"
}

# used to deploy packages in kubernetes
provider "helm" {
    kubernetes = {
        config_path = ""
    }
}