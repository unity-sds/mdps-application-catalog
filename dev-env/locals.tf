locals {

    raw_escaped = "" # needed if ssm parameters does not return the right subnets
    # unescaped   = replace(local.raw_escaped, "\\\"", "\"")
    subnet_map  = jsondecode(local.raw_escaped)

    #subnet_map = jsondecode(data.aws_ssm_parameter.subnet_list.value)
    public_subnet_ids = nonsensitive(local.subnet_map["public"])
    private_subnet_ids = nonsensitive(local.subnet_map["private"])
    private_subnet_cidr_values = values(data.aws_subnet.private_subnets).*.cidr_block
    public_subnet_cidr_values = values(data.aws_subnet.public_subnets).*.cidr_block
}