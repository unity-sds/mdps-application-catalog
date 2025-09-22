# aws mq - aws mq instance with rabbitmq as the engine

resource "aws_security_group" "rabbitmq_sg" {
    name = "rabbitmq-sg"
    vpc_id = data.aws_vpc.application_vpc.id

    ingress {
        from_port   = 5671  # AMQP over TLS
        to_port     = 5671  # AMQP
        protocol    = "tcp"
        cidr_blocks = local.private_subnet_cidr_values # Or your application CIDR
    }

    ingress {
        from_port   = 15672  # RabbitMQ Web UI
        to_port     = 15672
        protocol    = "tcp"
        cidr_blocks = local.private_subnet_cidr_values  # Be specific for security
    }

    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

# aws mq broker
resource "aws_mq_broker" "rabbitmq_broker" {
    broker_name = "rabbitmq_broker"
    engine_type = "RabbitMQ"
    engine_version = "3.13"
    host_instance_type = "mq.t3.micro"
    deployment_mode = "SINGLE_INSTANCE"
    
    # only a single subnet allowed in single_instance deployment
    subnet_ids = [local.private_subnet_ids[0]]
    
    security_groups = [aws_security_group.rabbitmq_sg.id]
    publicly_accessible =  false
    configuration {
        id = aws_mq_configuration.rabbitmq_broker_config.id
        revision = aws_mq_configuration.rabbitmq_broker_config.latest_revision
    }
    user {
        username = var.rabbit_mq_username
        password = random_password.rabbitmq_password.result
    }

    auto_minor_version_upgrade = true
    # maintenance_window_start_time {
    #     day_of_week = 
    #     time_of_day = 
    #     time_zone = 
    # }
    
    apply_immediately = true
}

# aws mq config
resource "aws_mq_configuration" "rabbitmq_broker_config" {
    description = "RabbitMQ Config"
    name = "rabbitmq-broker"
    engine_type = "RabbitMQ"
    engine_version = "3.13"
    data = <<-DATA
        # default mq delivery acknowledgement timeout is 30 minutes in milliseconds
        consumer_timeout = 1800000
    DATA
}

output "rabbitmq_hostname" {
    value = aws_mq_broker.rabbitmq_broker.instances[0].endpoints[0]
}