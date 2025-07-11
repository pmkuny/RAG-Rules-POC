# RAG Rules POC - AI Governance Rules System

This proof-of-concept provides RAG (Retrieval-Augmented Generation) functionality in OpenSearch on AWS for AI governance rules that can be retrieved by AI assistants pre-inference.

## 🏗️ Architecture

- **OpenSearch Domain**: Vector database for storing governance rules with embeddings
- **API Gateway**: REST API for rule management and querying
- **Lambda Functions**: Backend logic for rule operations and vector search
- **MCP Server**: Model Context Protocol server for Q CLI integration
- **Bedrock**: Amazon Titan embeddings for semantic search

## 📁 Project Structure

```
rag-rules.poc/
├── terraform/           # Infrastructure as Code
│   ├── main.tf         # Main Terraform configuration
│   ├── variables.tf    # Input variables
│   ├── opensearch.tf   # OpenSearch domain setup
│   ├── lambda.tf       # Lambda function configuration
│   ├── api_gateway.tf  # API Gateway setup
│   ├── iam.tf          # IAM roles and policies
│   └── outputs.tf      # Output values
├── lambda/             # Lambda function code
│   ├── handler.py      # Main Lambda handler
│   └── requirements.txt # Python dependencies
├── mcp-server/         # MCP server implementation
│   ├── server.py       # MCP server code
│   └── requirements.txt # Python dependencies
├── sample-rules/       # Example governance rules
│   ├── privacy_rules.json
│   ├── safety_rules.json
│   └── ethics_rules.json
├── deploy.sh           # Full deployment script
├── deploy-lambda.sh    # Lambda deployment script
├── load_sample_rules.py # Sample data loader
└── mcp-config-example.json # Q CLI configuration example
```

## 🚀 Quick Start

### Prerequisites

- AWS CLI configured with appropriate permissions
- Terraform >= 1.0
- Python 3.11+
- Q CLI (for MCP integration)

### 1. Setup Virtual Environment

```bash
# Clone or navigate to the project directory
cd rag-rules.poc

# Setup Python virtual environment and install dependencies
./setup-venv.sh
```

### 2. Deploy Infrastructure

```bash
# Clone or navigate to the project directory
cd rag-rules.poc

# Run the full deployment (virtual environment will be set up automatically if needed)
./deploy.sh
```

This will:
- Build the Lambda deployment package
- Deploy AWS infrastructure with Terraform
- Load sample governance rules
- Configure the MCP server

### 3. Configure Q CLI

Add the MCP server to your Q CLI configuration:

```json
{
  "mcpServers": {
    "governance-rules": {
      "command": "/path/to/rag-rules.poc/mcp-server/run-server.sh",
      "args": [],
      "env": {
        "API_GATEWAY_URL": "https://your-api-gateway-url.amazonaws.com/dev"
      }
    }
  }
}
```

### 4. Test the System

```bash
# Test MCP server directly
cd mcp-server
./run-server.sh

# Or use Q CLI with MCP integration
q chat
# Then use the governance rules tools in your conversation
```

## 🛠️ Usage

### MCP Tools Available

1. **load-governance-rule**: Add new governance rules
   ```json
   {
     "title": "Data Privacy Rule",
     "description": "Guidelines for handling personal data",
     "rule_text": "Never store PII without encryption...",
     "category": "privacy",
     "priority": 8,
     "tags": ["pii", "encryption"]
   }
   ```

2. **query-governance-rules**: Search rules by context
   ```json
   {
     "query": "handling personal information",
     "category": "privacy",
     "limit": 5
   }
   ```

3. **list-all-rules**: List all available rules
   ```json
   {
     "limit": 100
   }
   ```

### Rule JSON Structure

When loading governance rules, use the following JSON structure:

```json
{
  "title": "Rule Title",
  "description": "Brief description of the rule's purpose",
  "rule_text": "Detailed rule content used for semantic search and retrieval",
  "category": "privacy|safety|ethics|security|legal|general",
  "priority": 1,
  "tags": ["tag1", "tag2", "tag3"]
}
```

**Field Descriptions:**
- `title` (required): Short, descriptive name for the rule
- `description` (optional): Brief explanation of what the rule covers
- `rule_text` (required): The actual rule content that will be semantically searched
- `category` (optional): Classification category (defaults to "general")
- `priority` (optional): Integer from 1-10, where 10 is highest priority (defaults to 5)
- `tags` (optional): Array of strings for additional categorization and filtering

**Auto-generated fields:**
- `rule_id`: Unique identifier (12-character hex string)
- `created_at`: ISO timestamp when rule was created
- `updated_at`: ISO timestamp when rule was last modified
- Vector embeddings are automatically generated for semantic search

### Direct API Usage

```bash
# Load a rule
curl -X POST https://your-api-gateway-url.amazonaws.com/dev/rules \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Example Rule",
    "rule_text": "This is an example governance rule",
    "category": "general"
  }'

# Query rules
curl -X POST https://your-api-gateway-url.amazonaws.com/dev/rules/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "data privacy",
    "limit": 5
  }'

# List all rules
curl https://your-api-gateway-url.amazonaws.com/dev/rules
```

## 📊 Sample Rules Included

The system comes with sample governance rules in three categories:

- **Privacy Rules**: Data protection, retention, sharing guidelines
- **Safety Rules**: Harmful content prevention, misinformation, child safety
- **Ethics Rules**: Bias prevention, transparency, human autonomy

## 🔧 Configuration

### Environment Variables

- `API_GATEWAY_URL`: URL of the deployed API Gateway
- `OPENSEARCH_ENDPOINT`: OpenSearch domain endpoint (auto-configured)
- `OPENSEARCH_USERNAME`: OpenSearch username (default: admin)
- `OPENSEARCH_PASSWORD`: OpenSearch password (auto-generated)

### Terraform Variables

```hcl
variable "aws_region" {
  default = "us-east-1"
}

variable "environment" {
  default = "dev"
}

variable "opensearch_instance_type" {
  default = "t3.small.search"
}
```

## 🔍 Monitoring

### CloudWatch Metrics
- Lambda function performance and errors
- API Gateway request metrics
- OpenSearch cluster health

### Logs
- Lambda function logs in CloudWatch
- API Gateway access logs
- OpenSearch slow query logs

## 🛡️ Security

- OpenSearch domain with authentication enabled
- IAM roles with minimal required permissions
- Encryption at rest and in transit
- HTTPS-only API endpoints

## 💰 Cost Estimation

Approximate monthly costs for the POC:
- OpenSearch t3.small.search: ~$25
- Lambda: <$1 (for typical POC usage)
- API Gateway: <$1 (for typical POC usage)
- Bedrock embeddings: Variable based on usage

## 🧹 Cleanup

### Complete Infrastructure Destruction

To destroy all AWS resources and avoid ongoing charges:

```bash
# Navigate to terraform directory
cd terraform

# Review what will be destroyed (recommended)
terraform plan -destroy

# Destroy all resources
terraform destroy
```

### Cleanup Checklist

Before destroying, consider:

1. **Backup Important Data**: Export any governance rules you want to keep
2. **Check Dependencies**: Ensure no other systems depend on these resources
3. **Verify Destruction**: Check AWS Console to confirm all resources are deleted

### Manual Cleanup (if needed)

If `terraform destroy` fails, manually delete these resources in order:

1. **API Gateway**: Delete the REST API
2. **Lambda Function**: Delete the function and any versions
3. **OpenSearch Domain**: Delete the domain (this may take 10-15 minutes)
4. **IAM Roles**: Delete custom IAM roles and policies
5. **CloudWatch Logs**: Delete log groups if desired

### Cost Verification

After cleanup:
- Check your AWS billing dashboard
- Verify no OpenSearch domains are running
- Confirm Lambda functions are deleted

**⚠️ Warning**: Destroying the OpenSearch domain will permanently delete all governance rules. This action cannot be undone.

## 📚 Documentation

- [Architecture Documentation](ARCHITECTURE.md) - Detailed system design
- [API Documentation](API.md) - REST API reference
- [MCP Integration Guide](MCP.md) - Model Context Protocol details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **pip command not found**: This project uses `python3 -m pip` for package installation to ensure compatibility across different Python installations
2. **Lambda deployment fails**: Ensure Python dependencies are correctly packaged
2. **OpenSearch access denied**: Check IAM roles and security groups
3. **MCP server connection issues**: Verify API Gateway URL and network connectivity
4. **Embedding generation fails**: Ensure Bedrock access in the deployment region

### MCP Integration Issues

**Known Issue**: Q CLI MCP tool validation may fail with error: `Tool validation failed: The tool, "governance-rules___list-all-rules" is supplied with incorrect name`

**Workaround**: Use the direct CLI interface while the MCP issue is resolved:

```bash
# List all rules
./gr list --limit 10

# Query rules by context
./gr query "data privacy" --limit 5

# Query rules by category
./gr query "safety" --category safety --limit 3

# Load a new rule
./gr load "My Rule" "Rule content here" --category general --priority 5 --tags tag1 tag2
```

**Direct Python Usage**:
```bash
# Using the virtual environment directly
venv/bin/python governance-rules-cli.py list --limit 5
venv/bin/python governance-rules-cli.py query "personal data" --category privacy
```

### Getting Help

- Check CloudWatch logs for detailed error messages
- Verify AWS credentials and permissions
- Test API endpoints directly before using MCP integration
- Review Terraform state for resource configuration issues
