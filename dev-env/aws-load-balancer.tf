resource "helm_release" "aws_load_balancer_controller" {
    name = "aws-load-balancer-controller"
    namespace = "aws-lb"
    create_namespace = true
    repository = "https://aws.github.io/eks-charts"
    chart = "aws-load-balancer-controller"
    version = "1.13.2"
    timeout = 600

    values = [templatefile("aws-load-balancer-controller.yaml", {
        lb_role_name = "aws-load-balancer-controller" # points to kubernetes service account
        lb_role_arn = aws_iam_role.invenio_lb_role.arn
        cluster_name = module.eks.cluster_name
        aws_region = var.aws_region
        vpc_id = data.aws_ssm_parameter.vpc_id.value
    })]

    depends_on = [module.eks, aws_iam_role.invenio_lb_role, aws_iam_role_policy_attachment.lb_controller_attach ]
}

data "aws_iam_openid_connect_provider" "this" {
    url = module.eks.cluster_oidc_issuer_url

    depends_on = [ module.eks ]
}

locals {
    oidc_url = replace(module.eks.cluster_oidc_issuer_url, "https://", "")
    depends_on = [ module.eks ]
}

resource "aws_iam_role" "invenio_lb_role" {
    name = "invenio-aws-lb-controller-role"
    assume_role_policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Principal" : {
            "Federated" : data.aws_iam_openid_connect_provider.this.arn
          },
          "Action" : "sts:AssumeRoleWithWebIdentity",
          "Condition" : {
            "StringEquals" : {
              "${local.oidc_url}:sub" : "system:serviceaccount:aws-lb:aws-load-balancer-controller"
            }
          }
        }
      ]
    }
    )
    permissions_boundary = "arn:aws:iam::${var.account_id}:policy/mcp-tenantOperator-AMI-APIG"
    depends_on = [ module.eks ]
}

resource "aws_iam_policy" "lb_controller_policy" {
    name   = "AWSLoadBalancerControllerIAMPolicyInvenio"
    policy = file("aws-lb-controller-policy.json")
}

resource "aws_iam_role_policy_attachment" "lb_controller_attach" {
    role       = aws_iam_role.invenio_lb_role.name
    policy_arn = aws_iam_policy.lb_controller_policy.arn

    depends_on = [ aws_iam_role.invenio_lb_role, aws_iam_policy.lb_controller_policy ]
}

resource "kubernetes_service_account" "aws_lb_sa" {
    metadata {
        name = "aws-load-balancer-controller"
        namespace = "aws-lb"

        annotations = {
          "eks.amazonaws.com/role-arn" = aws_iam_role.invenio_lb_role.arn
        }
    }

    depends_on = [ aws_iam_role.invenio_lb_role ]
}

data "kubernetes_ingress_v1" "invenio" {
    metadata {
        name = "invenio"
        namespace = var.namespace
    }

    depends_on = [ helm_release.invenio ]
}

output "invenio_alb_hostname" {
    value = try(data.kubernetes_ingress_v1.invenio.status[0].load_balancer[0].ingress[0].hostname, "not-ready") #data.kubernetes_ingress_v1.invenio.status[0].load_balancer[0].ingress[0].hostname

    depends_on = [data.kubernetes_ingress_v1.invenio]
}