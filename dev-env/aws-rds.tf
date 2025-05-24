# resource "resource type" "resource name"
# module VPC -> resource subnet group and label ->  resource db instance -> resource db parameter group
# catalog is the resource name placeholder

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
    identifier = "catalog"
    instance_class = "db.t3.micro"
    allocated_storage = 2
    engine = "postgres"
    engine_version = "14.17"

    #creds for root user
    username = "invenio"
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