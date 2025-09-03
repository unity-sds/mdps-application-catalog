data "aws_caller_identity" "current" {}

data "aws_vpc" "application_vpc" {
  tags = {
    "Name" : var.vpc_name
  }
}

// get vpc_id
data "aws_ssm_parameter" "vpc_id" {
    name = "/unity/shared-services/network/vpc_id"
}

data "aws_subnets" "public_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.application_vpc.id]
  }
  filter {
    name   = "tag:Name"
    values = ["*Pub*"]
  }
}

data "aws_eks_cluster" "cluster" {
  name = "cat-cluster"
  depends_on = [module.eks]
}

data "aws_eks_cluster_auth" "cluster" {
  name = "cat-cluster"
  depends_on = [module.eks]
}

data "aws_iam_policy" "aws-managed-load-balancer-policy" {
  arn = "arn:aws:iam::aws:policy/ElasticLoadBalancingFullAccess"
}

data "aws_subnets" "private_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.application_vpc.id]
  }
  filter {
    name   = "tag:Name"
    values = ["*Priv*"]
  }
}

data "aws_subnet" "private_details" {
  for_each = toset(data.aws_subnets.private_subnets.ids)
  id       = each.value
}

data "aws_subnet" "public_details" {
  for_each = toset(data.aws_subnets.public_subnets.ids)
  id       = each.value
}

data "aws_ssm_parameter" "ami_id" {
    name = "/mcp/amis/aml2023-eks-1-32"
}
