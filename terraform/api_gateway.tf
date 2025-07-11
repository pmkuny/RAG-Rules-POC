# API Gateway REST API
resource "aws_api_gateway_rest_api" "governance_rules_api" {
  name        = "${local.name_prefix}-governance-rules-api"
  description = "API for AI Governance Rules RAG System"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = local.common_tags
}

# API Gateway Resource - /rules
resource "aws_api_gateway_resource" "rules" {
  rest_api_id = aws_api_gateway_rest_api.governance_rules_api.id
  parent_id   = aws_api_gateway_rest_api.governance_rules_api.root_resource_id
  path_part   = "rules"
}

# API Gateway Resource - /rules/query
resource "aws_api_gateway_resource" "rules_query" {
  rest_api_id = aws_api_gateway_rest_api.governance_rules_api.id
  parent_id   = aws_api_gateway_resource.rules.id
  path_part   = "query"
}

# POST method for /rules (load rules)
resource "aws_api_gateway_method" "rules_post" {
  rest_api_id   = aws_api_gateway_rest_api.governance_rules_api.id
  resource_id   = aws_api_gateway_resource.rules.id
  http_method   = "POST"
  authorization = "NONE"
}

# GET method for /rules (list all rules)
resource "aws_api_gateway_method" "rules_get" {
  rest_api_id   = aws_api_gateway_rest_api.governance_rules_api.id
  resource_id   = aws_api_gateway_resource.rules.id
  http_method   = "GET"
  authorization = "NONE"
}

# POST method for /rules/query (query rules)
resource "aws_api_gateway_method" "rules_query_post" {
  rest_api_id   = aws_api_gateway_rest_api.governance_rules_api.id
  resource_id   = aws_api_gateway_resource.rules_query.id
  http_method   = "POST"
  authorization = "NONE"
}

# Integration for POST /rules
resource "aws_api_gateway_integration" "rules_post_integration" {
  rest_api_id = aws_api_gateway_rest_api.governance_rules_api.id
  resource_id = aws_api_gateway_resource.rules.id
  http_method = aws_api_gateway_method.rules_post.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.governance_rules_handler.invoke_arn
}

# Integration for GET /rules
resource "aws_api_gateway_integration" "rules_get_integration" {
  rest_api_id = aws_api_gateway_rest_api.governance_rules_api.id
  resource_id = aws_api_gateway_resource.rules.id
  http_method = aws_api_gateway_method.rules_get.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.governance_rules_handler.invoke_arn
}

# Integration for POST /rules/query
resource "aws_api_gateway_integration" "rules_query_post_integration" {
  rest_api_id = aws_api_gateway_rest_api.governance_rules_api.id
  resource_id = aws_api_gateway_resource.rules_query.id
  http_method = aws_api_gateway_method.rules_query_post.http_method

  integration_http_method = "POST"
  type                   = "AWS_PROXY"
  uri                    = aws_lambda_function.governance_rules_handler.invoke_arn
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "governance_rules_deployment" {
  depends_on = [
    aws_api_gateway_integration.rules_post_integration,
    aws_api_gateway_integration.rules_get_integration,
    aws_api_gateway_integration.rules_query_post_integration,
  ]

  rest_api_id = aws_api_gateway_rest_api.governance_rules_api.id
  stage_name  = var.environment

  lifecycle {
    create_before_destroy = true
  }
}

# Enable CORS for all methods
resource "aws_api_gateway_method" "rules_options" {
  rest_api_id   = aws_api_gateway_rest_api.governance_rules_api.id
  resource_id   = aws_api_gateway_resource.rules.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_method_response" "rules_options_200" {
  rest_api_id = aws_api_gateway_rest_api.governance_rules_api.id
  resource_id = aws_api_gateway_resource.rules.id
  http_method = aws_api_gateway_method.rules_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration" "rules_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.governance_rules_api.id
  resource_id = aws_api_gateway_resource.rules.id
  http_method = aws_api_gateway_method.rules_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_integration_response" "rules_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.governance_rules_api.id
  resource_id = aws_api_gateway_resource.rules.id
  http_method = aws_api_gateway_method.rules_options.http_method
  status_code = aws_api_gateway_method_response.rules_options_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS,POST,PUT'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}
