# aws mq - aws mq instance with rabbitmq as the engine

# aws mq broker
resource "aws_mq_broker" "rabbitmq_broker" {
    broker_name = "rabbitmq_broker"
    engine_type = "RabbitMQ"
    engine_version = "3.13.7"
    host_instance_type = "mq.t3.micro"
    deployment_mode = "SINGLE_INSTANCE"
    subnet_ids = [module.vpc.public_subnets]
    publicly_accessible =  false
    configuration {
        id = aws_mq_configuration.rabbitmq_broker_config.id
        revision = aws_mq_configuration.rabbitmq_broker_config.latest_revision
    }
    user {
        username = var.rabbit_mq_username
        password = var.rabbit_mq_password
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
    engine_version = "3.13.7"
    data = <<-DATA
        # default mq delivery acknowledgement timeout is 30 minutes in milliseconds
        consumer_timeout = 1800000
    DATA
}