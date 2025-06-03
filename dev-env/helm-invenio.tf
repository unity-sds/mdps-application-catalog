resource "helm_release" "invenio" {
    name        = "invenio"
    repository  = "https://inveniosoftware.github.io/helm-invenio/"
    version     = "0.7.0"
    chart       = "invenio"

    namespace = "app-catalog-dev"
    create_namespace = true

    depends_on = [data.aws_vpc.selected, module.eks]
}

output "kube_namespace" {
    value = helm_release.invenio.namespace
}