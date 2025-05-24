# AWS RDS
# AWS MQ RabbitMQ
module "vpc" {
    source = "terraform-aws-modules/vpc/aws"
    version = "2.77.0"

    name = "aws_vpc"
    cidr = "10.0.0.0/16"
    azs = ["us-west-2a", "us-west-2b"]
    public_subnets = []
    private_subnets = []
    enable_dns_hostnames = true
    enable_dns_support = true

    public_subnet_tags = {
        "kubernetes.io/role/elb" = 1
    }

    private_subnet_tags = {
        "kubernetes.io/role/internal-elb" = 1
    }

    tags = {
        Terraform = "true"
        Environment = "dev"
    }
}