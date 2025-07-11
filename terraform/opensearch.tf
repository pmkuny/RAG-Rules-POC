# OpenSearch Domain
resource "aws_opensearch_domain" "governance_rules" {
  domain_name    = local.name_prefix
  engine_version = "OpenSearch_2.11"

  cluster_config {
    instance_type  = var.opensearch_instance_type
    instance_count = var.opensearch_instance_count
  }

  ebs_options {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = var.opensearch_volume_size
  }

  encrypt_at_rest {
    enabled = true
  }

  node_to_node_encryption {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https = true
  }

  advanced_security_options {
    enabled                        = true
    anonymous_auth_enabled         = false
    internal_user_database_enabled = false
    master_user_options {
      master_user_arn = aws_iam_role.lambda_role.arn
    }
  }

  tags = local.common_tags
}

# Random password for OpenSearch master user (DEPRECATED - using IAM auth now)
# resource "random_password" "opensearch_password" {
#   length  = 16
#   special = true
# }

# OpenSearch access policy - Allow broader access for IAM authentication
resource "aws_opensearch_domain_policy" "governance_rules_policy" {
  domain_name = aws_opensearch_domain.governance_rules.domain_name

  access_policies = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = "*"
        Action   = "es:*"
        Resource = "${aws_opensearch_domain.governance_rules.arn}/*"
      }
    ]
  })
}
