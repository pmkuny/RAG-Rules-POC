output "opensearch_endpoint" {
  description = "OpenSearch domain endpoint"
  value       = aws_opensearch_domain.governance_rules.endpoint
}

output "opensearch_dashboard_endpoint" {
  description = "OpenSearch dashboard endpoint"
  value       = aws_opensearch_domain.governance_rules.dashboard_endpoint
}

# output "opensearch_username" {
#   description = "OpenSearch master username (DEPRECATED - using IAM auth now)"
#   value       = "admin"
# }

# output "opensearch_password" {
#   description = "OpenSearch master password"
#   value       = random_password.opensearch_password.result
#   sensitive   = true
# }

output "api_gateway_url" {
  description = "API Gateway URL"
  value       = "${aws_api_gateway_deployment.governance_rules_deployment.invoke_url}"
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.governance_rules_handler.function_name
}

output "project_name" {
  description = "Project name with random suffix"
  value       = local.name_prefix
}
