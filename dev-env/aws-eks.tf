module "eks" {
    source = "terraform-aws-modules/eks/aws"
    version = "20.36.0"

    cluster_name = "cat-cluster"
    cluster_version = "1.27"
    subnet_ids = data.aws_subnets.private.ids
    vpc_id = data.aws_vpc.selected.id
    control_plane_subnet_ids = data.aws_subnets.private.ids

    cluster_endpoint_public_access = true
    cluster_endpoint_private_access = true
    enable_cluster_creator_admin_permissions = true

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

    eks_managed_node_group_defaults = {
        create_iam_role = true
        iam_role_name = "app-catalog-dev-EKSClusterRole" # temp. to do: move to config file
        iam_role_permissions_boundary = "arn:aws:iam::${var.account_id}:policy/mcp-tenantOperator-AMI-APIG" # temp. to do: move to config file
    }
    
    eks_managed_node_groups = {
        default = {
            min_size = 1
            max_size = 3
            desired_size = 1

            instance_types = ["t3.medium"]
            capacity_type = "SPOT" #ON_DEMAND for prod?
        }
    }

    tags = {
        terraform = "true"
        env = "dev"
    }

    depends_on = [data.aws_vpc.selected]
}

data "aws_ami" "eks_worker" {
    owners = ["amazon"]
    most_recent = true

    filter {
        name   = "name"
        values = ["amazon-eks-node-*-v1.27-*"] #v1.27 is the cluster version
    }
}

output "ami_id" {
    value = data.aws_ami.eks_worker.id
}

output "ami_name" {
    value = data.aws_ami.eks_worker.name
}