
# https://github.com/unity-sds/unity-sps/tree/develop/terraform-unity/modules/terraform-unity-sps-airflow

resource "helm_release" "invenio" {
    name        = "invenio"
    repository  = "https://inveniosoftware.github.io/helm-invenio/"
    version     = "0.7.0"
    chart       = "invenio"
    timeout     = 900

    namespace = var.namespace
    cleanup_on_fail = true
    create_namespace = true

    values = [templatefile("invenio-values.yaml", {
        pg_db_name = aws_db_instance.catalog.db_name
        pg_username = aws_db_instance.catalog.username
        pg_password = aws_db_instance.catalog.password
        pg_port = aws_db_instance.catalog.port
        pg_endpoint = aws_db_instance.catalog.endpoint
        
        rmq_username = var.rabbit_mq_username
        rmq_password = var.rabbit_mq_password
        rmq_hostname = regex("^amqps://([^:]+)", aws_mq_broker.rabbitmq_broker.instances[0].endpoints[0])[0]
        rmq_port = 5671
        rmq_protocol = "AMQPS"
        rmq_vhost = "/"

        invenio_hostname = data.kubernetes_service.ingress-nginx.status[0].load_balancer[0].ingress[0].hostname
        
        redis_hostname = aws_elasticache_replication_group.redis.primary_endpoint_address
    })]
    depends_on = [
        data.aws_vpc.selected, 
        module.eks, 
        aws_mq_broker.rabbitmq_broker, 
        aws_db_instance.catalog, 
        helm_release.ingress-nginx,
        aws_elasticache_replication_group.redis
    ]
}