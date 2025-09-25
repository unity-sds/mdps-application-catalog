### EFS
resource "aws_kms_key" "efs_key" {
  description             = "KMS key for EFS encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = merge(local.common_tags, {
    Name      = "cat-cluster-EfsKmsKey"
    Component = "airflow"
    Stack     = "airflow"
  })
}

resource "aws_kms_alias" "efs_key_alias" {
  name          = "alias/cat-cluster-efs-key"
  target_key_id = aws_kms_key.efs_key.key_id
}

resource "aws_efs_file_system" "efs" {
  creation_token = "cat-cluster-AirflowEfs"
  encrypted      = true
  kms_key_id     = aws_kms_key.efs_key.arn

  tags = merge(local.common_tags, {
    Name      = "cat-cluster-AirflowEfs"
    Component = "airflow"
    Stack     = "airflow"
  })
}

# EFS-SC

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
    name = "shared-data"
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

resource "kubernetes_storage_class" "ebs" {
  metadata {
    name = "auto-ebs-sc"
    annotations = {
       "storageclass.kubernetes.io/is-default-class" =  "true"
    }
  }
  storage_provisioner = "ebs.csi.eks.amazonaws.com"
  volume_binding_mode =  "WaitForFirstConsumer"
  parameters = {
    "type"="gp3"
    "encrypted"="true"
  }


}
