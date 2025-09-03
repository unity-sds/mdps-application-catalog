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