resource "aws_security_group" "opensearch_sg" {
    name = "opensearch-sg"
    description = "Allow EKS to talk to OpenSearch"
    vpc_id = data.aws_vpc.selected.id

    ingress {
        from_port = 443
        to_port = 443
        protocol = "tcp"
        cidr_blocks = [data.aws_vpc.selected.cidr_block]
    }

    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_opensearch_domain" "invenio_opensearch" {
    domain_name = "invenio-domain"
    engine_version = "OpenSearch_2.19"
    access_policies = templatefile("${path.module}/opensearch-access-policy.json.tmpl", {
        account_id = var.account_id
        domain_name = "invenio-domain"
        aws_region = var.aws_region
        #eks_cluster_role_arn = module.eks.eks_managed_node_groups["invenio"].iam_role_arn
    })

    advanced_security_options {
      enabled = true
      internal_user_database_enabled = true
      master_user_options {
        master_user_name = var.os_username
        # The master user password must contain at least one uppercase letter, one lowercase letter, one number, and one special character.
        master_user_password = var.os_password
      }
    }

    vpc_options {
        subnet_ids = data.aws_subnets.private.ids
        security_group_ids = [aws_security_group.opensearch_sg.id]
    }

    node_to_node_encryption {
        enabled = true
    }

    encrypt_at_rest {
        enabled = true
    }

    domain_endpoint_options {
        enforce_https = true
    }

    cluster_config {
        instance_type = "t3.small.search"
        instance_count = 2
        zone_awareness_enabled = true

        zone_awareness_config {
            availability_zone_count = 2
        }
    }

    ebs_options {
      ebs_enabled = true
      volume_size = 10 #in gb
      volume_type = "gp3"
    }

    advanced_options = {
      "rest.action.multi.allow_explicit_index" = "true"
    }

    depends_on = [ data.aws_vpc.selected, module.eks ]
}

output "opensearch_hostname" {
    value = aws_opensearch_domain.invenio_opensearch.endpoint
}