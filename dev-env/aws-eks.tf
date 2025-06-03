module "eks" {
    source = "terraform-aws-modules/eks/aws"
    version = "20.36.0"

    cluster_name = "cat-cluster"
    cluster_version = "1.31"
    subnet_ids = data.aws_subnets.private.ids
    vpc_id = data.aws_vpc.selected.id

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
    
    enable_irsa = true
    create_iam_role = true
    iam_role_name = "app-catalog-dev-EKSClusterRole" # temp. to do: move to config file
    iam_role_permissions_boundary = "arn:aws:iam::${var.account_id}:policy/mcp-tenantOperator-AMI-APIG" # temp. to do: move to config file

    cluster_endpoint_public_access = true
    cluster_endpoint_private_access = true
    enable_cluster_creator_admin_permissions = true

    eks_managed_node_group_defaults = {
        ami_id = var.ami_id
        create_iam_role = true
        iam_role_name = "app-catalog-dev-EKSNodeRole" # temp. to do: move to config file
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
            instance_types = ["t3.medium"]
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
        }
    }

    tags = {
        terraform = "true"
        env = "dev"
    }

    depends_on = [data.aws_vpc.selected]
}