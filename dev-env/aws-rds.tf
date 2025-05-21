# resource "resource type" "resource name"
# module VPC -> resource subnet group and label ->  resource db instance -> resource db parameter group
# catalog is the resource name placeholder

# VPC
module "vpc" {
    source = ""
    version = ""

    name = "catalog"
    cidr = ""
    azs = ""
    public_submets = []
    enable_dns_hostnames = true
    enable_dns_support = true
}

# subnet group and label
resource "aws_db_subnet_group" "catalog" {
    name = "catalog"
    subnet_ids = module.vpc.public_subnets

    tags = {
        Name = "Catalog"
    }
}

# db instance postgres
resource "aws_db_instance" "catalog" {
    identifier = ""
    instance_class = ""
    allocated_storage = ""
    engine = ""
    engine_version = ""

    #creds for root user
    username = ""
    password = var.db_password

    db_subnet_group_name = aws_db_subnet_group.catalog.name
    vpc_security_group_ids = [aws_security_group.rds.id]
    parameter_group_name = aws_db_parameter_group.catalog.name

    # false for prod systems
    publicly_accessible = false

    # true = disable taking a final back up when the db is destroyed
    skip_final_snapshot = false
}

# db parameter group
resource "aws_db_parameter_group" "catalog" {
    name = "catalog"

    # must correspond with the engine version of the rds instance
    family = "postgres14"

    # custom parameter groups optional
    # parameter {
        # name = "log"
        # value = "1"
    # }
}