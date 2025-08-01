# data "aws_route53_zone" "main" {
#     name = var.zone_name
# }

# data "aws_lb" "invenio" {
#   tags = {
#     "elbv2.k8s.aws/cluster" = module.eks.cluster_name
#     "ingress.k8s.aws/resource" = "LoadBalancer"
#     "ingress.k8s.aws/stack" = "${var.namespace}/invenio"
#   }

#   depends_on = [ data.kubernetes_ingress_v1.invenio ]
# }

# resource "aws_route53_record" "invenio_dns" {
#     zone_id = data.aws_route53_zone.main.zone_id
#     name = var.invenio_hostname
#     type = "A"

#     alias {
#         #ingress dns
#         name = "dualstack.${data.kubernetes_ingress_v1.invenio.status[0].load_balancer[0].ingress[0].hostname}"
#         zone_id = try(data.aws_lb.invenio.zone_id, "")
#         evaluate_target_health = true
#     }

#     depends_on = [ 
#         helm_release.aws_load_balancer_controller, 
#         helm_release.invenio,
#         data.aws_route53_zone.main,
#         data.kubernetes_ingress_v1.invenio
#     ]
# }

# Too many grid-locking dependencies to enable...