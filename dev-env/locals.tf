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

    ami_id = "ami-0b5844d5df7e37795"
    cluster_name = "cat-cluster"
    vpc_id = data.aws_ssm_parameter.vpc_id.value
    mergednodegroups = {
        invenio = {

            min_size = 1
            max_size = 5
            desired_size = 2
            use_name_prefix            = false
            create_iam_role            = false
            create_launch_template     = false
            use_custom_launch_template = true
            enable_bootstrap_user_data = true
            /*pre_bootstrap_user_data = <<-EOT
                sudo sed -i 's/^net.ipv4.ip_forward = 0/net.ipv4.ip_forward = 1/' /etc/sysctl.conf && sudo sysctl -p |true
            EOT*/
            ami_id = "ami-0b5844d5df7e37795"
            iam_role_additional_policies = { AmazonEBSCSIDriverPolicy = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy" }
            iam_role_arn = aws_iam_role.cluster_iam_role.arn
            instance_types = ["m5.large"] # t3.medium
            subnet_ids = local.private_subnet_ids
            capacity_type = "ON_DEMAND" #ON_DEMAND|SPOT for prod?
            block_device_mappings = {
                device_name = "/dev/xvda"

                ebs = {
                    volume_size           = 20
                    volume_type           = "gp3"
                    delete_on_termination = true
                    encrypted             = true
                }
            }
            
            launch_template_id = aws_launch_template.node_group_launch_template.id
            #launch_template_id = aws_launch_template.node_group_launch_template.id
            additional_security_group_ids = [aws_security_group.eks_sg.id]
            openidc_provider_domain_name = trimprefix(module.eks.cluster_oidc_issuer_url, "https://")

        }
    }

}