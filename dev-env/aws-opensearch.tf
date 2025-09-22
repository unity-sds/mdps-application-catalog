resource "aws_security_group" "opensearch_sg" {
    name = "opensearch-sg"
    description = "Allow EKS to talk to OpenSearch"
    vpc_id = data.aws_vpc.application_vpc.id

    ingress {
        from_port = var.os_port
        to_port = var.os_port
        protocol = "tcp"
        cidr_blocks = local.private_subnet_cidr_values
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
        account_id = data.aws_caller_identity.current.account_id
        domain_name = "invenio-domain"
        aws_region = var.aws_region
    })

    advanced_security_options {
      enabled = true
      internal_user_database_enabled = true
      master_user_options {
        master_user_name = var.os_username
        # The master user password must contain at least one uppercase letter, one lowercase letter, one number, and one special character.
        master_user_password = random_password.opensearch_password.result
      }
    }

    vpc_options {
        subnet_ids = [
            local.private_subnet_ids[0],
            local.private_subnet_ids[1]
        ]
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
        # It's critical that we DO NOT use the opensearch optimized instance types. They are set to a default re-index latency of 10s,
        # and Invenio hard codes 5s into a number of their index templates. Defaults for non-optimized instances are 1s.
        instance_type = "c6g.large.search"
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
}

output "opensearch_hostname" {
    value = aws_opensearch_domain.invenio_opensearch.endpoint
}
