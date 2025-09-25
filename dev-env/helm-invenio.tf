
/*
# https://github.com/unity-sds/unity-sps/tree/develop/terraform-unity/modules/terraform-unity-sps-airflow
resource "helm_release" "invenio" {
    name        = "invenio"
    #repository  = "https://inveniosoftware.github.io/helm-invenio/"
    #version     = "0.7.0"

    # var.chart_path is the location of the custom packaged invenio chart version 0.7.0
    # changes:
    #   - changed web service port from 80 to 8080
    #   - changed 
    chart       = var.chart_path
    timeout     = 450

    namespace = var.namespace
    cleanup_on_fail = true
    create_namespace = true

    values = [templatefile("invenio-values.yaml", {
        pg_db_name = aws_db_instance.catalog.db_name
        pg_username = aws_db_instance.catalog.username
        pg_password = aws_db_instance.catalog.password
        pg_port = aws_db_instance.catalog.port
        pg_host = aws_db_instance.catalog.address
        # "postgresql+psycopg2://${aws_db_instance.catalog.username}:${aws_db_instance.catalog.password}@${aws_db_instance.catalog.address}:${aws_db_instance.catalog.port}/${aws_db_instance.catalog.db_name}"
        
        rmq_username = var.rabbit_mq_username
        rmq_password = random_password.rabbitmq_password.result
        rmq_hostname = regex("^amqps://([^:]+)", aws_mq_broker.rabbitmq_broker.instances[0].endpoints[0])[0]
        rmq_port = 5671
        rmq_protocol = "AMQPS"
        rmq_vhost = "/"

        #invenio_hostname = data.kubernetes_service.ingress-nginx.status[0].load_balancer[0].ingress[0].hostname
        invenio_hostname = var.invenio_hostname
        
        redis_hostname = aws_elasticache_replication_group.redis.primary_endpoint_address

        opensearch_hostname = aws_opensearch_domain.invenio_opensearch.endpoint
        opensearch_port = var.os_port
        opensearch_scheme = "https"
        opensearch_username = var.os_username
        opensearch_password = random_password.opensearch_password.result

        invenio_init = var.invenio_init
        public_subnets = join(",", local.public_subnet_ids)
        ingress_cert_arn = var.aws_cert_arn
        alb_sg_id = aws_security_group.alb_sg.id
    })]
    depends_on = [ 
        module.eks, 
        aws_mq_broker.rabbitmq_broker, 
        aws_db_instance.catalog,
        helm_release.aws-load-balancer-controller,
        aws_security_group.alb_sg,
        #helm_release.ingress-nginx,
        aws_elasticache_replication_group.redis,
        aws_opensearch_domain.invenio_opensearch
    ]
}

output "output_opensearch_hostname" {
    value = format("%s%s:%s", "https://", aws_opensearch_domain.invenio_opensearch.endpoint, var.os_port)
}
*/

