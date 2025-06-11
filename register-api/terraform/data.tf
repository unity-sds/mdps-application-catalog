data "aws_caller_identity" "current" {}

data "aws_vpc" "application_vpc" {
  tags = {
    "Name" : var.vpc_name
  }
}

data "aws_iam_policy" "permissions_boundary" {
  name = "mcp-tenantOperator-AMI-APIG"
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