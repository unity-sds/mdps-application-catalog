# aws mq - aws mq instance with rabbitmq as the engine

# do i need one for rds and one for rabbitmq?
# module vpc
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

# aws mq broker
resource "aws_mq_broker" "rabbitmq_broker" {

}

# aws mq config
resource "aws_mq_configuration" "rabbitmq_broker_config" {
    
}