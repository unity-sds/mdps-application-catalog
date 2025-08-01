// get vpc_id
data "aws_ssm_parameter" "vpc_id" {
    name = "/unity/shared-services/network/vpc_id"
}

// get subnet list
// public: [], private: []
data "aws_ssm_parameter" "subnet_list" {
    name = "/unity/shared-services/network/subnet_list"
}

data "aws_ssm_parameter" "ami_id" {
    name = "/mcp/amis/aml2-eks-1-31"
}

# // mcp_operator_policy
# data "aws_iam_policy" "mcp_operator_policy" {
#     name = "mcp-tenantOperator-AMI-APIG"
# }

// get private cidrs
data "aws_subnet" "private_subnets" {
    for_each = "${toset(local.private_subnet_ids)}"
    id       = "${each.value}"
}

// get public cidrs
data "aws_subnet" "public_subnets" {
    for_each = "${toset(local.public_subnet_ids)}"
    id       = "${each.value}"
}