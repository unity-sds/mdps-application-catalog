terraform {
  backend "s3" {
    bucket               = "mdps-sit-artifact-catalog"
    key                  = "terraform/terraform.tfstate"
    region               = "us-west-2"
    encrypt              = true
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_db_subnet_group" "default" {
  name       = "mdps-artficat-catalog-db-subnets"
  subnet_ids = data.aws_subnets.private_subnets.ids

  tags = {
    Name = "My DB subnet group"
  }
}


resource "random_password" "db" {
  length           = 16
  special          = true
  override_special = "_!%^"
}

resource "aws_secretsmanager_secret" "db" {
  name                    = "mdps-artficat-catalog-db-scrt"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "db" {
  secret_id     = aws_secretsmanager_secret.db.id
  secret_string = random_password.db.result
}


# RDS PostgreSQL Instance
module "db" {
  source = "terraform-aws-modules/rds/aws"
  version = "6.0.0"

  identifier = "${var.project_name}-db"

  engine            = "postgres"
  engine_version    = "14.15"
  instance_class    = var.db_instance_class
  allocated_storage = 20

  db_name  = var.db_name
  username = var.db_username
  password = aws_secretsmanager_secret_version.db.secret_string
  port     = "5432"
  manage_master_user_password = false

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name             = aws_db_subnet_group.default.name

  family = "postgres14"

  tags = var.tags
}

resource "aws_kms_key" "efs_key" {
  description             = "KMS key for EFS encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

}

resource "aws_efs_file_system" "storage" {
  encrypted      = true
  kms_key_id     = aws_kms_key.efs_key.arn
  tags = {
    Name = "ECS-EFS-FS-APP-CATALOG"
  }
}

resource "aws_efs_mount_target" "efs-mt" {
  for_each        = toset(data.aws_subnets.private_subnets.ids)
  file_system_id  = aws_efs_file_system.storage.id
  subnet_id       = each.value
  security_groups = [aws_security_group.app-catalog-efs.id, aws_security_group.ecs_tasks.id]
}

resource "aws_efs_access_point" "cwl" {
  file_system_id = aws_efs_file_system.storage.id
  root_directory {
    path = "/cwl"
    creation_info {
      owner_gid   = 0
      owner_uid   = 50000
      permissions = "0777"
    }
  }
}

resource "aws_security_group" "app-catalog-efs" {
  name        = "AppCatalogAirflowEfsSg"
  description = "Security group for the EFS used in appcatalog"
  vpc_id      = data.aws_vpc.application_vpc.id
}

resource "aws_security_group_rule" "app-catalog-efs" {
  type              = "ingress"
  from_port         = 2049
  to_port           = 2049
  protocol          = "tcp"
  security_group_id = aws_security_group.app-catalog-efs.id
  cidr_blocks       = [data.aws_vpc.application_vpc.cidr_block] # VPC CIDR to allow entire VPC. Adjust as necessary.
}

resource "aws_security_group_rule" "app-catalog-efs-from-ecs" {
  type              = "ingress"
  from_port         = 2049
  to_port           = 2049
  protocol          = "tcp"
  security_group_id = aws_security_group.app-catalog-efs.id
  source_security_group_id       = aws_security_group.ecs_tasks.id # VPC CIDR to allow entire VPC. Adjust as necessary.
}


# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"
}

# ECS Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = "${var.project_name}-task"
  network_mode            = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                     = var.task_cpu
  memory                  = var.task_memory
  execution_role_arn      = aws_iam_role.ecs_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "${var.project_name}-container"
      image     = var.container_image
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
      mountPoints = [
          {
              containerPath = "/usr/share/storage",
              sourceVolume = "efs-cwl"
          }
      ]
      environment = [
        {
          name  = "DATABASE_URL"
          value = "postgresql://${var.db_username}:${aws_secretsmanager_secret_version.db.secret_string}@${module.db.db_instance_endpoint}/${var.db_name}"
        },
        {
          name  = "SECRET_KEY"
          value = var.secret_key
        },
        {
          name  = "PYTHONPATH"
          value = "/app"
        },
        {
          name  = "DESTINATION_REGISTRY"
          value = var.container_registry
        },
        {
          name  = "STORAGE_PATH"
          value = "/usr/share/storage"
        },
        {
          name  = "ALGORITHM"
          value = "HS256"
        },
        {
          name  = "ACCESS_TOKEN_EXPIRE_MINUTES"
          value = "30"
        },
        {
          name  = "JWT_AUTH_TYPE"
          value = "COGNITO"
        },
        {
          name  = "JWT_VALIDATION_URL"
          value = "https://cognito-idp.us-west-2.amazonaws.com/${var.user_pool_id}/.well-known/jwks.json"
        },
        {
          name  = "JWT_ISSUER_URL"
          value = "https://cognito-idp.us-west-2.amazonaws.com/${var.user_pool_id}"
        },
        {
          name  = "JWT_CLIENT_ID"
          value = var.client_id
        },
        {
          name  = "JWT_GROUPS_KEY"
          value = "cognito:groups"
        }              
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.project_name}"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
  volume {
    name      = "efs-cwl"
    efs_volume_configuration {
      file_system_id = aws_efs_file_system.storage.id
      root_directory = "/"
      transit_encryption = "ENABLED"
      authorization_config {
        access_point_id = aws_efs_access_point.cwl.id
      }
    }
  }
}

# ECS Service
resource "aws_ecs_service" "app" {
  name            = "${var.project_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.service_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets          = data.aws_subnets.private_subnets.ids
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "${var.project_name}-container"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.app]
}

# Application Load Balancer
resource "aws_lb" "app" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = data.aws_subnets.public_subnets.ids

  tags = var.tags
}

resource "aws_lb_target_group" "app" {
  name        = "${var.project_name}-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.application_vpc.id
  target_type = "ip"

  health_check {
    path                = "/docs"
    healthy_threshold   = 2
    unhealthy_threshold = 10
  }
}

resource "aws_lb_listener" "app" {
  load_balancer_arn = aws_lb.app.arn
  port              = 8443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = data.aws_acm_certificate.issued.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# Security Groups
resource "aws_security_group" "alb" {
  name        = "${var.project_name}-alb-sg"
  description = "Security group for ALB"
  vpc_id      = data.aws_vpc.application_vpc.id

  ingress {
    from_port   = 8443
    to_port     = 8443
    protocol    = "tcp"
    cidr_blocks = ["128.149.0.0/16", "137.78.0.0/16", "137.79.0.0/16"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

resource "aws_security_group" "ecs_tasks" {
  name        = "${var.project_name}-ecs-tasks-sg"
  description = "Security group for ECS tasks"
  vpc_id      = data.aws_vpc.application_vpc.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds-sg"
  description = "Security group for RDS"
  vpc_id      = data.aws_vpc.application_vpc.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  tags = var.tags
}

# IAM Roles
resource "aws_iam_role" "ecs_execution_role" {
  name = "${var.project_name}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  permissions_boundary = data.aws_iam_policy.permissions_boundary.arn

}

resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task_role" {
  name = "${var.project_name}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  permissions_boundary = data.aws_iam_policy.permissions_boundary.arn

}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.project_name}"
  retention_in_days = 30
} 
