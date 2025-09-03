
/*
# https://github.com/unity-sds/unity-sps/tree/develop/terraform-unity/modules/terraform-unity-sps-airflow
resource "helm_release" "invenio" {
    name        = "invenio"
    #repository  = "https://inveniosoftware.github.io/helm-invenio/"
    #version     = "0.7.0"

    # var.chart_path is the location of the custom packaged invenio chart version 0.7.0
    # changes:
    #   - changed web service port from 80 to 8080
    #   - changed 
    chart       = var.chart_path
    timeout     = 450

    namespace = var.namespace
    cleanup_on_fail = true
    create_namespace = true

    values = [templatefile("invenio-values.yaml", {
        pg_db_name = aws_db_instance.catalog.db_name
        pg_username = aws_db_instance.catalog.username
        pg_password = aws_db_instance.catalog.password
        pg_port = aws_db_instance.catalog.port
        pg_host = aws_db_instance.catalog.address
        # "postgresql+psycopg2://${aws_db_instance.catalog.username}:${aws_db_instance.catalog.password}@${aws_db_instance.catalog.address}:${aws_db_instance.catalog.port}/${aws_db_instance.catalog.db_name}"
        
        rmq_username = var.rabbit_mq_username
        rmq_password = random_password.rabbitmq_password.result
        rmq_hostname = regex("^amqps://([^:]+)", aws_mq_broker.rabbitmq_broker.instances[0].endpoints[0])[0]
        rmq_port = 5671
        rmq_protocol = "AMQPS"
        rmq_vhost = "/"

        #invenio_hostname = data.kubernetes_service.ingress-nginx.status[0].load_balancer[0].ingress[0].hostname
        invenio_hostname = var.invenio_hostname
        
        redis_hostname = aws_elasticache_replication_group.redis.primary_endpoint_address

        opensearch_hostname = aws_opensearch_domain.invenio_opensearch.endpoint
        opensearch_port = var.os_port
        opensearch_scheme = "https"
        opensearch_username = var.os_username
        opensearch_password = random_password.opensearch_password.result

        invenio_init = var.invenio_init
        public_subnets = join(",", local.public_subnet_ids)
        ingress_cert_arn = var.aws_cert_arn
        alb_sg_id = aws_security_group.alb_sg.id
    })]
    depends_on = [ 
        module.eks, 
        aws_mq_broker.rabbitmq_broker, 
        aws_db_instance.catalog,
        helm_release.aws-load-balancer-controller,
        aws_security_group.alb_sg,
        #helm_release.ingress-nginx,
        aws_elasticache_replication_group.redis,
        aws_opensearch_domain.invenio_opensearch
    ]
}

output "output_opensearch_hostname" {
    value = format("%s%s:%s", "https://", aws_opensearch_domain.invenio_opensearch.endpoint, var.os_port)
}
*/

/*
#EFS Usage

# https://github.com/hashicorp/terraform-provider-kubernetes/issues/864
resource "kubernetes_storage_class" "efs" {
  metadata {
    name = "filestore"
  }
  reclaim_policy      = "Retain"
  storage_provisioner = "efs.csi.aws.com"
}

resource "aws_security_group" "airflow_efs" {
  name        = format(local.resource_name_prefix, "AirflowEfsSg")
  description = "Security group for the EFS used in Airflow"
  vpc_id      = data.aws_eks_cluster.cluster.vpc_config[0].vpc_id
  tags = merge(local.common_tags, {
    Name      = format(local.resource_name_prefix, "AirflowEfsSg")
    Component = "airflow"
    Stack     = "airflow"
  })
}

resource "aws_security_group_rule" "airflow_efs" {
  type              = "ingress"
  from_port         = 2049
  to_port           = 2049
  protocol          = "tcp"
  security_group_id = aws_security_group.airflow_efs.id
  cidr_blocks       = [data.aws_vpc.application_vpc.cidr_block] # VPC CIDR to allow entire VPC. Adjust as necessary.
}

resource "aws_efs_mount_target" "airflow" {
  for_each        = toset(data.aws_subnets.private_subnets.ids)
  file_system_id  = aws_efs_file_system.efs.id
  subnet_id       = each.value
  security_groups = [aws_security_group.airflow_efs.id]
}

resource "aws_efs_access_point" "shared_data" {
  file_system_id = aws_efs_file_system.efs.id
  posix_user {
    gid = 0
    uid = 50000
  }
  root_directory {
    path = "/rdm-shared-data"
    creation_info {
      owner_gid   = 0
      owner_uid   = 50000
      permissions = "0755"
    }
  }
  tags = merge(local.common_tags, {
    Name      = format(local.resource_name_prefix, "EfsAirflowSharedData")
    Component = "airflow"
    Stack     = "airflow"
  })
}

resource "time_sleep" "wait_for_efs_mount_target_dns_propagation" {
  # AWS recommends that you wait 90 seconds after creating a mount target before
  # you mount your file system. This wait lets the DNS records propagate fully
  # in the AWS Region where the file system is.
  depends_on      = [aws_efs_mount_target.airflow]
  create_duration = "120s"
}

resource "kubernetes_persistent_volume" "shared_data" {
  metadata {
    name = "rdm-shared-data"
  }
  spec {
    capacity = {
      storage = "5Gi"
    }
    access_modes                     = ["ReadWriteMany"]
    persistent_volume_reclaim_policy = "Retain"
    persistent_volume_source {
      csi {
        driver        = "efs.csi.aws.com"
        volume_handle = "${aws_efs_file_system.efs.id}::${aws_efs_access_point.shared_data.id}"
      }
    }
    storage_class_name = kubernetes_storage_class.efs.metadata[0].name
  }
}

resource "kubernetes_persistent_volume_claim" "shared_data" {
  metadata {
    name      = "shared-data"
    namespace = "rdm"
  }
  spec {
    access_modes = ["ReadWriteMany"]
    resources {
      requests = {
        storage = "5Gi"
      }
    }
    volume_name        = kubernetes_persistent_volume.shared_data.metadata[0].name
    storage_class_name = kubernetes_storage_class.efs.metadata[0].name
  }
}

*/