module "eks" {
    source = "terraform-aws-modules/eks/aws"
    version = "20.36.0"

    cluster_name = "cat-cluster"
    cluster_version = "1.31"
    subnet_ids = local.private_subnet_ids
    control_plane_subnet_ids = local.private_subnet_ids
    vpc_id = data.aws_ssm_parameter.vpc_id.value

    cluster_addons = {
        coredns = {
            most_recent = true
        }
        kube-proxy = {
            most_recent = true
        }
        vpc-cni = {
            most_recent = true
        }
    }
    
    #ensures the cluster has the needed eks security policy
    cluster_additional_security_group_ids = [aws_security_group.eks_sg.id]
    node_security_group_additional_rules = {
        allow_alb_8080 = {
            description = "node worker allow alb ingress on 8080"
            protocol = "tcp"
            from_port = 8080
            to_port = 8080
            type = "ingress"
            source_security_group_id = aws_security_group.alb_sg.id
        }

        allow_alb_8443 = {
            description = "node worker allow alb ingress on 8443"
            protocol = "tcp"
            from_port = 8443
            to_port = 8443
            type = "ingress"
            source_security_group_id = aws_security_group.alb_sg.id
        }
    }

    enable_irsa = true
    create_iam_role = true
    iam_role_name = "${var.namespace}-EKSClusterRole" # temp. to do: move to config file
    iam_role_permissions_boundary = "arn:aws:iam::${var.account_id}:policy/mcp-tenantOperator-AMI-APIG" # temp. to do: move to config file

    cluster_endpoint_public_access = true
    cluster_endpoint_private_access = true
    enable_cluster_creator_admin_permissions = true
    
    eks_managed_node_group_defaults = {
        #attach_cluster_primary_security_group = true
        #additional_security_group_ids = [ aws_security_group.alb_sg.id ]

        ami_id = data.aws_ssm_parameter.ami_id.value
        create_iam_role = true
        iam_role_name = "${var.namespace}-EKSNodeRole" # temp. to do: move to config file
        iam_role_permissions_boundary = "arn:aws:iam::${var.account_id}:policy/mcp-tenantOperator-AMI-APIG" # temp. to do: move to config file

        # required for MCP EKS ami images -> EKS Cluster
        enable_bootstrap_user_data = true
        pre_bootstrap_user_data = <<-EOT
            sudo sed -i 's/^net.ipv4.ip_forward = 0/net.ipv4.ip_forward = 1/' /etc/sysctl.conf && sudo sysctl -p |true
        EOT
    }

    eks_managed_node_groups = {
        invenio = {
            min_size = 1
            max_size = 3
            desired_size = 2

            ami_type = "AL2_x86_64"
            instance_types = ["t3.large"] # t3.medium
            subnet_ids = local.private_subnet_ids
            capacity_type = "SPOT" #ON_DEMAND for prod?
            block_device_mappings = {
                device_name = "/dev/xvda"

                ebs = {
                    volume_size           = 20
                    volume_type           = "gp3"
                    delete_on_termination = true
                    encrypted             = true
                }
            }

            #ensures nodes have the alb security policy
            additional_security_group_ids = [aws_security_group.eks_sg.id]
        }
    }

    depends_on = [ aws_security_group.alb_sg, aws_security_group.eks_sg ]

    tags = {
        terraform = "true"
        env = "dev"
    }
}

# security policies needed for ports 8080 and 8443
# sg for eks
resource "aws_security_group" "eks_sg" {
    name_prefix = "cat-cluster-eks-"
    vpc_id = data.aws_ssm_parameter.vpc_id.value

    # Allow ALB to reach EKS pods
    ingress {
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        security_groups = [aws_security_group.alb_sg.id]
    }

    ingress {
        from_port = 8443
        to_port = 8443
        protocol = "tcp"
        security_groups = [aws_security_group.alb_sg.id]
    }

    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }

    depends_on = [ aws_security_group.alb_sg ]

    tags = {
        Name = "cat-cluster-eks-sg"
    }
}

# sg for alb
resource "aws_security_group" "alb_sg" {
    name_prefix = "cat-cluster-alb-"
    vpc_id = data.aws_ssm_parameter.vpc_id.value

    ingress {
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port = 8443
        to_port = 8443
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }

    tags = {
        Name = "cat-cluster-alb-sg"
    }
}

output "eks_role_arn" {
    value = module.eks.eks_managed_node_groups["invenio"].iam_role_arn
}

output "cluster_iam_role_arn" {
    value = module.eks.cluster_iam_role_arn
}

data "aws_eks_cluster" "main" {
    name = module.eks.cluster_name

    depends_on = [ module.eks ]
}

data "aws_eks_cluster_auth" "main" {
    name = module.eks.cluster_name

    depends_on = [ module.eks ]
}