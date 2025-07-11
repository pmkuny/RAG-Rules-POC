# Lambda function for governance rules
resource "aws_lambda_function" "governance_rules_handler" {
  filename         = "../lambda/governance_rules_handler.zip"
  function_name    = "${local.name_prefix}-governance-rules-handler"
  role            = aws_iam_role.lambda_role.arn
  handler         = "handler.lambda_handler"
  runtime         = "python3.11"
  timeout         = 30
  memory_size     = 512

  environment {
    variables = {
      OPENSEARCH_ENDPOINT = aws_opensearch_domain.governance_rules.endpoint
      INDEX_NAME         = "governance-rules"
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic,
    aws_iam_role_policy.lambda_opensearch_policy,
  ]

  tags = local.common_tags
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gateway_invoke" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.governance_rules_handler.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.governance_rules_api.execution_arn}/*/*"
}
