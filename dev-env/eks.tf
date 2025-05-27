module "eks" {
    source = "terraform-aws-modules/eks/aws"
    version = "20.36.0"

    cluster_name = "cat-cluster"
    cluster_version = "1.27"
    subnet_ids = module.vpc.private_subnets
    vpc_id = module.vpc.vpc_id
    control_plane_subnet_ids = module.vpc.private_subnets

    providers = {
        aws = provider.aws.aws_region
    }

    cluster_endpoint_public_access = true

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
    
    eks_managed_node_group_defaults = {
        instance_types = []
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
}