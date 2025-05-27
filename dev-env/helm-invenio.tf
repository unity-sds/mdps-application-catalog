resource "helm_release" "invenio" {
    name        = "helm-invenio/invenio"
    repository  = "https://inveniosoftware.github.io/helm-invenio/"
    version     = "0.7.0"
    chart       = "invenio"

    depends_on = [module.eks]
}