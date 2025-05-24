module "eks" {
    source = "terraform-aws-modules/eks/aws"
    version = "~> 19.0"

    cluster_name = "cat-cluster"
    cluster_version = "1.27"

    providers = {
        aws = aws.region
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

    # vpc_id = 
    # subnet_ids =
    # control_plane_subnet_ids =

    # eks_managed_node_group_defaults = {
        
    # }

    # eks_managed_node_groups = {

    # }

    # tags = {
    #     terraform = "true"
    #     env = "dev"
    # }
}