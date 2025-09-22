data "aws_caller_identity" "current" {}

data "aws_vpc" "application_vpc" {
  tags = {
    "Name" : var.vpc_name
  }
}

data "aws_subnets" "public_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.application_vpc.id]
  }
  filter {
    name   = "tag:Name"
    values = ["*pub*"]
  }
}

data "aws_eks_cluster" "cluster" {
  name = "cat-cluster"
}

data "aws_eks_cluster_auth" "cluster" {
  name = "cat-cluster"
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
    values = ["*priv*"]
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
