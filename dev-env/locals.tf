locals {


    common_tags  = {}

    public_subnet_ids = data.aws_subnets.public_subnets.ids
    private_subnet_ids = data.aws_subnets.private_subnets.ids
    
    resource_name_prefix = "cat-cluster-%s"
    
    private_subnet_cidr_values =  [
        for subnet_id in local.private_subnet_ids :
        data.aws_subnet.private_details[subnet_id].cidr_block
    ]

    public_subnet_cidr_values =  [
        for subnet_id in local.public_subnet_ids :
        data.aws_subnet.public_details[subnet_id].cidr_block
    ]

    cluster_name = "cat-cluster"

}