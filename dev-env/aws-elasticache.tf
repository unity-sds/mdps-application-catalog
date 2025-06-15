resource "aws_elasticache_subnet_group" "redis_subnet_group" {
    name = "redis-subnet-group"
    subnet_ids = data.aws_subnets.public.ids
}

resource "aws_security_group" "redis_sg" {
    name = "redis-sg"
    description = "Allow Redis Access"
    vpc_id = data.aws_vpc.selected.id

    ingress {
        from_port = 6379
        to_port = 6379
        protocol = "tcp"
        cidr_blocks = [data.aws_vpc.selected.cidr_block]
    }

    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = [data.aws_vpc.selected.cidr_block]
    }
}

resource "aws_elasticache_replication_group" "redis" {
    replication_group_id =  "cat-redis-group"
    description = "Catalog Redis Replication Group"
    engine = "redis"
    engine_version = "6.x"
    node_type = "cache.t3.micro"
    num_cache_clusters = 1
    automatic_failover_enabled = false
    port = 6379
    parameter_group_name = "default.redis6.x"
    subnet_group_name = aws_elasticache_subnet_group.redis_subnet_group.name
    security_group_ids = [aws_security_group.redis_sg.id]

    depends_on = [data.aws_vpc.selected]
}

output "redis_endpoint" {
    value = aws_elasticache_replication_group.redis.primary_endpoint_address
}