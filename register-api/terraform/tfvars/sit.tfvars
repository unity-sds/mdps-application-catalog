aws_region            = "us-west-2"
container_image       = "237868187491.dkr.ecr.us-west-2.amazonaws.com/mdps/register-api:latest"
container_registry    = "237868187491.dkr.ecr.us-west-2.amazonaws.com"
db_instance_class     = "db.t3.micro"
db_name               = "mdps_catalog"
db_username           = "postgres"
project_name          = "mdps-artifact-catalog"
secret_key            = ""
service_desired_count = 1
tags = {
  "Environment": "sit",
  "Project": "mdps-artifact-catalog"
}
task_cpu    = 256
task_memory = 512
vpc_name    = "Unity-Dev-VPC"
client_id = "40c2s0ulbhp9i0fmaph3su9jch"
user_pool_id = "us-west-2_yaOw3yj0z"
cert_domain = "*.dev.mdps.mcp.nasa.gov"