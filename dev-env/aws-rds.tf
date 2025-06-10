# resource "resource type" "resource name"
# module VPC -> resource subnet group and label ->  resource db instance -> resource db parameter group
# catalog is the resource name placeholder

# security group
resource "aws_security_group" "rds_sg" {
    name = "rds_sg"
    description = "PostgresSQL access"
    vpc_id = data.aws_vpc.selected.id

    #inbound
    ingress {
        description = "allow PostgresSQL from trusted IP"
        from_port = 5432
        to_port = 5432
        protocol = "tcp"
        cidr_blocks = ["10.0.0.0/16"]
    }

    #outbound
    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["10.0.0.0/16"]
    }
}

# subnet group and label
resource "aws_db_subnet_group" "catalog" {
    name = "catalog"
    subnet_ids = data.aws_subnets.public.ids

    tags = {
        Name = "Catalog"
    }
}

# db instance postgres
resource "aws_db_instance" "catalog" {
    db_name = "invenio"
    identifier = "catalog"
    instance_class = "db.t3.micro"
    storage_type = "gp2"
    allocated_storage = 20 # minimum 20(gb) for postgres gp2
    engine = "postgres"
    engine_version = "14.17"

    #creds for root user
    username = "invenio"
    password = var.db_password

    db_subnet_group_name = aws_db_subnet_group.catalog.name
    vpc_security_group_ids = [aws_security_group.rds_sg.id]
    parameter_group_name = aws_db_parameter_group.catalog.name

    # false for prod systems
    publicly_accessible = false

    # true = disable taking a final back up when the db is destroyed
    skip_final_snapshot = true
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

output "pg_endpoint" {
    value = aws_db_instance.catalog.endpoint
}