# terraform module

<!-- TFDOCS START -->
```
module <terraform> {
  source = "https://github.com/unity-sds/mdps-application-catalog.git//register-api/terraform?ref=<TAG>"
  aws_region = <STRING>               # AWS region to deploy resources
  container_image = <STRING>          # Docker image for the application
  db_instance_class = <STRING>        # RDS instance class
  db_name = <STRING>                  # Name of the database
  db_password = <STRING>              # Database master password
  db_username = <STRING>              # Database master username
  project_name = <STRING>             # Name of the project
  secret_key = <STRING>               # Secret key for the application
  service_desired_count = <NUMBER>    # Number of instances of the task to run
  tags = <MAP(STRING)>                # Tags to apply to all resources
  task_cpu = <NUMBER>                 # CPU units for the ECS task
  task_memory = <NUMBER>              # Memory for the ECS task
  vpc_name = <STRING>                 # No description provided
}
```
<!-- TFDOCS END -->
