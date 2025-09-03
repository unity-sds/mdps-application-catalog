# MDPS Application Catalog with InvenioRDM

MDPS Application Catalog is deployed using Terraform with AWS and Invenio Helm charts.

## Pre-requisites
1. [AWS](https://aws.amazon.com/cli/)
2. [Terraform](https://developer.hashicorp.com/terraform/cli)
3. [Kubernetes](https://minikube.sigs.k8s.io/docs/start/?arch=%2Fmacos%2Farm64%2Fstable%2Fbinary+download)
4. [Invenio-Helm Charts](https://github.com/inveniosoftware/helm-invenio)

## Installation

Use the aws cli to configure a profile for the aws account where invenio will be deployed on. You'll be asked to provide keys, a region, and output (json).

```bash
aws configure --profile [profile_name]
```

## Configuring Terraform Variables
`[tfvars_file_name].tfvars` file is used for customized variables
```yaml
# AWS
aws_profile = "" # profile_name
account_id = "" # aws account id if not supplied by ssm parameters

# opensearch
os_username = ""
os_password = ""
os_port = 443

# lb controller
aws_cert_arn = ""

# route53
zone_name = ""

# Postgres
db_password = ""

# RabbitMQ
rabbit_mq_username = ""
rabbit_mq_password = ""

# COMMON
namespace = "" # namespace for the application

# InvenioRDM
invenio_init = true # true to create tables, false to not create tables; recommended to do true on first creation
invenio_hostname = "" # site name
chart_path = "" # path of the custom invenio helm chart

```

## Configuring Invenio-helm Chart Values
[values.yaml](https://github.com/inveniosoftware/helm-invenio/blob/master/charts/invenio/values.yaml) is used to override the default values of the invenio helm chart.

While the configuration below is recommended, please visit the [Invenio-helm repository](https://github.com/inveniosoftware/helm-invenio) to get a better grasp of how the Invenio application is configured.
```yaml
global:
  timezone: "America/Los_Angeles"

ingress:
  annotations:
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/security-groups: "${alb_sg_id}"
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTPS": 8443}]' #'[{"HTTP": 8080}, {"HTTPS": 8443}]'
    alb.ingress.kubernetes.io/subnets: ${public_subnets}
    alb.ingress.kubernetes.io/certificate-arn: ${ingress_cert_arn}
    alb.ingress.kubernetes.io/healthcheck-path: /ping
    alb.ingress.kubernetes.io/healthcheck-port: "8080"
    alb.ingress.kubernetes.io/healthcheck-interval-seconds: '30'
    alb.ingress.kubernetes.io/healthcheck-timeout-seconds: '10'
    alb.ingress.kubernetes.io/healthy-threshold-count: '2'
    alb.ingress.kubernetes.io/unhealthy-threshold-count: '2'
  enabled: true
  class: alb
  tlsSecretNameOverride: ""

invenio:
  hostname: ${invenio_hostname}
  init: ${invenio_init}
  default_users:  # Requires invenio.init=true
    "admin": "admin" # Rob: don't do this! Change it!
  demo_data: true  # Setting invenio.demo_data=true requires also setting default_users!

extraConfig:
    INVENIO_SEARCH_HOSTS: '[{"host": "${opensearch_hostname}", "port": ${opensearch_port}, "scheme": "${opensearch_scheme}", "http_auth": ["${opensearch_username}","${opensearch_password}"], "timeout":60 }]'
    INVENIO_APP_ALLOWED_HOSTS: '["${invenio_hostname}"]'

web:
  replicas: 1
  service:
    type: ClusterIP

redisExternal:
  hostname: ${redis_hostname}

rabbitmqExternal:
  username: ${rmq_username}
  password: ${rmq_password}
  amqpPort: ${rmq_port}
  managementPort: 15672
  hostname: ${rmq_hostname}
  protocol: ${rmq_protocol}
  vhost: ${rmq_vhost}
  existingSecret: ""
  existingSecretPasswordKey: ""

postgresqlExternal:
  hostname: ${pg_host}
  port: ${pg_port}
  username: ${pg_username}
  password: ${pg_password}
  database: ${pg_db_name}
  existingSecret: ""
  existingSecretPasswordKey: ""
```

Configure any needed resources and probes. Resources will not all be the same. Configure them based on your needs. Below is only an example.
```yaml
 resources:
    requests:
      cpu: 100m
      memory: 500Mi
    limits:
      cpu: 250m
      memory: 500Mi

exec:
      command:
        - /bin/bash
        - -c
        - 'echo "Probing with host header: ${invenio_hostname}" && curl -v -f -H "Host: ${invenio_hostname}" localhost:8080/ping'
```

## Application Deployment

```bash
cd mdps-application-catalog/dev-env
terraform init -var-file="[tfvars_file_name].tfvars"
terraform plan -var-file="[tfvars_file_name].tfvars"
terraform apply -var-file="[tfvars_file_name].tfvars"
```

To destroy all resources
```bash
terraform destroy -var-file="[tfvars_file_name].tfvars"
```

## Troubleshooting

- Expired Credentials? Renew AWS keys and credentials and reapply where AWS profiles are configured
- Cannot reach kubernetes? try running `aws eks update-kubeconfig --region [aws_region] --name [cluster_name] --profile [aws_profile_name]`
- Error with helm_release install? try uninstalling the helm_release and reapplying terraform. 
```bash
helm uninstall [helm_release_package_name]
terraform apply -var-file="[tfvars_file_name].tfvars"
```