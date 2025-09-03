resource "aws_iam_role" "cluster_iam_role" {
  name = "${local.cluster_name}-eks-node-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "eks.amazonaws.com" # or the appropriate AWS service
        },
      },
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com" # or the appropriate AWS service
        },
      },
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "s3.amazonaws.com" # or the appropriate AWS service
        },
      },
    ],
  })

  permissions_boundary = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/mcp-tenantOperator-AMI-APIG"

}

resource "aws_iam_role_policy_attachment" "container-reg" {
  role       = aws_iam_role.cluster_iam_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_role_policy_attachment" "ebscsi" {
  role       = aws_iam_role.cluster_iam_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
}
resource "aws_iam_role_policy_attachment" "eks-cni" {
  role       = aws_iam_role.cluster_iam_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}
resource "aws_iam_role_policy_attachment" "worker-node" {
  role       = aws_iam_role.cluster_iam_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}
resource "aws_iam_role_policy_attachment" "ssm-automation" {
  role       = aws_iam_role.cluster_iam_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonSSMAutomationRole"
}
resource "aws_iam_role_policy_attachment" "ssm-managed-instance" {
  role       = aws_iam_role.cluster_iam_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
resource "aws_iam_role_policy_attachment" "cloudwatch-agent" {
  role       = aws_iam_role.cluster_iam_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_role_policy_attachment" "node-policy" {
  role       = aws_iam_role.cluster_iam_role.name
  policy_arn = aws_iam_policy.custom_policy.arn
}

resource "aws_iam_policy" "custom_policy" {
  name        = "${local.cluster_name}-eks-policy" # Give a unique name to your policy
  path        = "/"                                # Optionally, specify a path for the policy
  description = "A custom policy that provides access to EC2, ECR, SNS, etc."

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "ec2:CreateTags",
            "Resource": [
                "arn:aws:ec2:*:*:volume/*",
                "arn:aws:ec2:*:*:snapshot/*"
            ],
            "Condition": {
                "StringEquals": {
                    "ec2:CreateAction": [
                        "CreateVolume",
                        "CreateSnapshot"
                    ]
                }
            }
        },
        {
                "Sid": "KMSforEKS",
                "Effect": "Allow",
                "Action": [
                    "kms:Decrypt",
                    "kms:ReEncryptTo",
                    "kms:GenerateDataKeyWithoutPlaintext",
                    "kms:DescribeKey",
                    "kms:CreateGrant",
                    "kms:ReEncryptFrom",
                    "elasticfilesystem:*"

                ],
                "Resource": "*"
        },
        {
            "Sid": "confluencebatch",
            "Effect": "Allow",
            "Action": "batch:SubmitJob",
            "Resource": [
                "arn:aws:batch:*:*:job-definition/svc*",
                "arn:aws:batch:*:*:job-queue/svc*"
            ]
        },
        {
            "Sid": "confluencesnf",
            "Effect": "Allow",
            "Action": [ 
              "batch:DescribeJobs",
              "states:ListExecutions",
              "states:ListMapRuns"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "ec2:CreateVolume",
            "Resource": "*",
            "Condition": {
                "StringLike": {
                    "aws:RequestTag/ebs.csi.aws.com/cluster": "true"
                }
            }
        },
        {
            "Sid": "VisualEditor2",
            "Effect": "Allow",
            "Action": "ec2:CreateVolume",
            "Resource": "*",
            "Condition": {
                "StringLike": {
                    "aws:RequestTag/CSIVolumeName": "*"
                }
            }
        },
        {
            "Sid": "VisualEditor3",
            "Effect": "Allow",
            "Action": "ec2:DeleteVolume",
            "Resource": "*",
            "Condition": {
                "StringLike": {
                    "ec2:ResourceTag/ebs.csi.aws.com/cluster": "true"
                }
            }
        },
        {
            "Sid": "VisualEditor4",
            "Effect": "Allow",
            "Action": "ec2:DeleteVolume",
            "Resource": "*",
            "Condition": {
                "StringLike": {
                    "ec2:ResourceTag/CSIVolumeName": "*"
                }
            }
        },
        {
            "Sid": "VisualEditor5",
            "Effect": "Allow",
            "Action": "ec2:DeleteVolume",
            "Resource": "*",
            "Condition": {
                "StringLike": {
                    "ec2:ResourceTag/kubernetes.io/created-for/pvc/name": "*"
                }
            }
        },
        {
            "Sid": "VisualEditor6",
            "Effect": "Allow",
            "Action": "ec2:DeleteSnapshot",
            "Resource": "*",
            "Condition": {
                "StringLike": {
                    "ec2:ResourceTag/CSIVolumeSnapshotName": "*"
                }
            }
        },
        {
            "Sid": "VisualEditor7",
            "Effect": "Allow",
            "Action": "ec2:DeleteSnapshot",
            "Resource": "*",
            "Condition": {
                "StringLike": {
                    "ec2:ResourceTag/ebs.csi.aws.com/cluster": "true"
                }
            }
        },
        {
            "Sid": "VisualEditor8",
            "Effect": "Allow",
            "Action": "ec2:CreateTags",
            "Resource": "arn:aws:ec2:*:*:network-interface/*"
        },
        {
            "Sid": "VisualEditor9",
            "Effect": "Allow",
            "Action": "ec2:DeleteTags",
            "Resource": [
                "arn:aws:ec2:*:*:volume/*",
                "arn:aws:ec2:*:*:snapshot/*"
            ]
        },
        {
            "Sid": "VisualEditor10",
            "Effect": "Allow",
            "Action": [
                "sns:Publish",
                "lambda:InvokeFunction",
                "ssm:GetParameter"
            ],
            "Resource": [
                "arn:aws:lambda:*:*:function:Automation*",
                "arn:aws:sns:*:*:Automation*",
                "arn:aws:ssm:*:*:parameter/AmazonCloudWatch-*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:GetRepositoryPolicy",
                "ecr:DescribeRepositories",
                "ecr:ListImages",
                "ecr:DescribeImages",
                "ecr:BatchGetImage",
                "ecr:GetLifecyclePolicy",
                "ecr:GetLifecyclePolicyPreview",
                "ecr:ListTagsForResource",
                "ecr:DescribeImageScanFindings"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor11",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "cloudwatch:PutMetricData",
                "ec2:DescribeVolumesModifications",
                "ec2:CreateImage",
                "ec2:CopyImage",
                "ssm:ListInstanceAssociations",
                "ec2:DescribeSnapshots",
                "ssm:GetParameter",
                "ssm:UpdateAssociationStatus",
                "logs:CreateLogStream",
                "cloudformation:DescribeStackEvents",
                "ec2:StartInstances",
                "ssm:UpdateInstanceInformation",
                "ec2:DescribeVolumes",
                "cloudformation:UpdateStack",
                "ec2:UnassignPrivateIpAddresses",
                "ec2:DescribeRouteTables",
                "ssm:PutComplianceItems",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetLifecyclePolicy",
                "ec2:DetachVolume",
                "sns:*",
                "ec2:ModifyVolume",
                "ecr:DescribeImageScanFindings",
                "ec2:CreateTags",
                "ec2:ModifyNetworkInterfaceAttribute",
                "ecr:GetDownloadUrlForLayer",
                "ec2:DeleteNetworkInterface",
                "ec2messages:AcknowledgeMessage",
                "ec2:RunInstances",
                "ecr:GetAuthorizationToken",
                "ssm:GetParameters",
                "ec2:StopInstances",
                "s3-object-lambda:*",
                "ec2:AssignPrivateIpAddresses",
                "logs:CreateLogGroup",
                "cloudformation:DescribeStacks",
                "ec2:CreateNetworkInterface",
                "cloudformation:DeleteStack",
                "ec2:DescribeInstanceTypes",
                "ecr:BatchGetImage",
                "ecr:DescribeImages",
                "ec2messages:SendReply",
                "eks:DescribeCluster",
                "ec2:DescribeSubnets",
                "ec2:AttachVolume",
                "ec2:DeregisterImage",
                "ec2:DeleteSnapshot",
                "ssm:DescribeDocument",
                "ec2:DeleteTags",
                "ec2messages:GetEndpoint",
                "logs:DescribeLogStreams",
                "ssmmessages:OpenControlChannel",
                "ec2messages:GetMessages",
                "ecr:ListTagsForResource",
                "ssm:PutConfigurePackageResult",
                "ecr:ListImages",
                "ssm:GetManifest",
                "ec2messages:DeleteMessage",
                "ec2:DescribeNetworkInterfaces",
                "ec2messages:FailMessage",
                "ec2:DescribeAvailabilityZones",
                "ssmmessages:OpenDataChannel",
                "ec2:CreateSnapshot",
                "ssm:GetDocument",
                "ecr:DescribeRepositories",
                "ec2:DescribeInstanceStatus",
                "ssm:DescribeAssociation",
                "ec2:TerminateInstances",
                "ec2:DetachNetworkInterface",
                "logs:DescribeLogGroups",
                "ssm:GetDeployablePatchSnapshotForInstance",
                "s3:*",
                "ec2:DescribeTags",
                "ecr:GetLifecyclePolicyPreview",
                "ssmmessages:CreateControlChannel",
                "logs:PutLogEvents",
                "ec2:DescribeSecurityGroups",
                "ssmmessages:CreateDataChannel",
                "ec2:DescribeImages",
                "ssm:PutInventory",
                "cloudformation:CreateStack",
                "ec2:DescribeVpcs",
                "ssm:*",
                "ec2:AttachNetworkInterface",
                "ssm:ListAssociations",
                "ssm:UpdateInstanceAssociationStatus",
                "ecr:GetRepositoryPolicy"
            ],
            "Resource": "*"
        },
        {
			"Sid": "StepFunctionActions",
			"Effect": "Allow",
			"Action": [
				"states:DescribeActivity",
				"states:DescribeExecution",
				"states:DescribeMapRun",
				"states:DescribeStateMachine",
				"states:DescribeStateMachineAlias",
				"states:DescribeStateMachineForExecution",
				"states:GetExecutionHistory",
				"states:RevealSecrets",
				"states:ValidateStateMachineDefinition",
				"states:StartExecution",
				"states:StartSyncExecution"
			],
			"Resource": [
				"*"
			]
		}
    ]
}
EOF
}


module "eks" {
    source = "terraform-aws-modules/eks/aws"
    version = "20.34"


    cluster_name = "cat-cluster"
    cluster_version = "1.32"

    cluster_addons = {
        coredns = {
            most_recent = true
        }
        kube-proxy = {
            most_recent = true
        }
        vpc-cni = {
            most_recent = true
        }
        aws-ebs-csi-driver = {
            most_recent = true
            configuration_values = jsonencode({
                defaultStorageClass = {
                    enabled = true
                }
            })
        }
        aws-efs-csi-driver = {
            most_recent = false
            version = "2.1.11"
            configuration_values = jsonencode({
                useFIPS = true
            })
        }
    }
    
    subnet_ids = local.private_subnet_ids
    vpc_id = local.vpc_id

    enable_cluster_creator_admin_permissions = true
    create_cluster_security_group         = true
    create_node_security_group            = true
    #cluster_additional_security_group_ids = [aws_security_group.eks_sg.id]
    create_iam_role                       = false
    enable_irsa                           = true
    iam_role_arn                          = aws_iam_role.cluster_iam_role.arn


     eks_managed_node_group_defaults = {
        instance_types = ["m6i.large", "m5.large", "m5n.large", "m5zn.large"]
        iam_role_arn   = aws_iam_role.cluster_iam_role.arn
        iam_role_additional_policies = { AmazonEBSCSIDriverPolicy = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy" }
    }
    
    eks_managed_node_groups = local.mergednodegroups

    cluster_endpoint_public_access = true
    cluster_endpoint_private_access = true

    tags = {
        terraform = "true"
        env = "dev"
    }

    /*
    node_security_group_additional_rules = {
        allow_alb_8080 = {
            description = "node worker allow alb ingress on 8080"
            protocol = "tcp"
            from_port = 8080
            to_port = 8080
            type = "ingress"
            source_security_group_id = aws_security_group.alb_sg.id
        }

        allow_alb_8443 = {
            description = "node worker allow alb ingress on 8443"
            protocol = "tcp"
            from_port = 8443
            to_port = 8443
            type = "ingress"
            source_security_group_id = aws_security_group.alb_sg.id
        }
    }
    */
}

/*
data "aws_eks_cluster_auth" "cluster_auth" {
  name = module.eks.cluster_name
}
*/

resource "aws_launch_template" "node_group_launch_template" {
  #name_prefix   = "${module.eks.cluster_name}-node"
  image_id = local.ami_id
  name     = "eks-${module.eks.cluster_name}-nodeGroup-launchTemplate"
  user_data = base64encode(<<-EOT
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="BOUNDARY"

--BOUNDARY
Content-Type: application/node.eks.aws

---
apiVersion: node.eks.aws/v1alpha1
kind: NodeConfig
spec:
  cluster:
    name: ${module.eks.cluster_name}
    apiServerEndpoint: ${module.eks.cluster_endpoint}
    certificateAuthority: ${module.eks.cluster_certificate_authority_data}
    cidr: ${module.eks.cluster_service_cidr}
--BOUNDARY--
EOT
  )
  tag_specifications {
    resource_type = "instance"
    tags = merge(local.common_tags, {
      Name      = "${local.cluster_name} Node Group Node"
      Component = "EKS EC2 Instance"
      Stack     = "EKS EC2 Instance"
    })
  }
}

# security policies needed for ports 8080 and 8443
# sg for eks
resource "aws_security_group" "eks_sg" {
    name_prefix = "cat-cluster-eks-"
    vpc_id = data.aws_ssm_parameter.vpc_id.value

    # Allow ALB to reach EKS pods
    ingress {
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        security_groups = [aws_security_group.alb_sg.id]
    }

    ingress {
        from_port = 8443
        to_port = 8443
        protocol = "tcp"
        security_groups = [aws_security_group.alb_sg.id]
    }

    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }

    tags = {
        Name = "cat-cluster-eks-sg"
    }
}

# sg for alb
resource "aws_security_group" "alb_sg" {
    name_prefix = "cat-cluster-alb-"
    vpc_id = data.aws_ssm_parameter.vpc_id.value

    ingress {
        from_port = 8080
        to_port = 8080
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port = 8443
        to_port = 8443
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }

    tags = {
        Name = "cat-cluster-alb-sg"
    }
}


output "eks_role_arn" {
    value = module.eks.eks_managed_node_groups["invenio"].iam_role_arn
}


output "cluster_iam_role_arn" {
    value = module.eks.cluster_iam_role_arn
}
