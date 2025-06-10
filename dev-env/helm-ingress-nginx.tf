resource "helm_release" "ingress-nginx" {
    name = "ingress-nginx"
    namespace = "ingress"
    create_namespace = true
    chart = "ingress-nginx"
    version = "4.12.3"
    repository = "https://kubernetes.github.io/ingress-nginx"
    
    depends_on = [module.eks]
    values = [file("${path.module}/nginx-values.yaml")]
}

data "kubernetes_service" "ingress-nginx" {
  metadata {
    name = "ingress-nginx-controller"
    namespace = helm_release.ingress-nginx.metadata[0].namespace
  }
}

output "load-balancer-hostname" {
  value = data.kubernetes_service.ingress-nginx.status[0].load_balancer[0].ingress[0].hostname
}