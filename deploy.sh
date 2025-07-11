#!/bin/bash

# Full deployment script for RAG Rules POC
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_ROOT/venv"

echo "🚀 Deploying RAG Rules POC..."

# Check prerequisites
echo "📋 Checking prerequisites..."
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform is required but not installed."
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is required but not installed."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "🐍 Virtual environment not found. Setting up..."
    ./setup-venv.sh
fi

# Build Lambda package
echo "📦 Building Lambda deployment package..."
./deploy-lambda.sh

# Deploy infrastructure
echo "🏗️  Deploying infrastructure with Terraform..."
cd terraform
terraform init
terraform plan
read -p "Do you want to apply these changes? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    terraform apply -auto-approve
    
    # Get outputs
    echo "📝 Getting deployment outputs..."
    API_GATEWAY_URL=$(terraform output -raw api_gateway_url)
    OPENSEARCH_ENDPOINT=$(terraform output -raw opensearch_endpoint)
    OPENSEARCH_PASSWORD=$(terraform output -raw opensearch_password)
    
    echo "✅ Infrastructure deployed successfully!"
    echo "📊 Deployment Information:"
    echo "   API Gateway URL: $API_GATEWAY_URL"
    echo "   OpenSearch Endpoint: $OPENSEARCH_ENDPOINT"
    echo "   OpenSearch Username: admin"
    echo "   OpenSearch Password: $OPENSEARCH_PASSWORD"
    
    # Update MCP server configuration
    cd ../mcp-server
    echo "export API_GATEWAY_URL='$API_GATEWAY_URL'" > .env
    echo "🔧 MCP server configuration updated"
    
    # Load sample rules
    echo "📚 Loading sample governance rules..."
    cd ..
    
    # Activate virtual environment for loading sample rules
    source "$VENV_DIR/bin/activate"
    python load_sample_rules.py "$API_GATEWAY_URL"
    deactivate
    
    echo "🎉 Deployment completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Configure Q CLI to use the MCP server:"
    echo "   Add the following to your Q CLI configuration:"
    echo "   {"
    echo "     \"mcpServers\": {"
    echo "       \"governance-rules\": {"
    echo "         \"command\": \"$(pwd)/mcp-server/run-server.sh\","
    echo "         \"args\": [],"
    echo "         \"env\": {"
    echo "           \"API_GATEWAY_URL\": \"$API_GATEWAY_URL\""
    echo "         }"
    echo "       }"
    echo "     }"
    echo "   }"
    echo ""
    echo "2. Test the MCP server:"
    echo "   cd mcp-server && ./run-server.sh"
    
else
    echo "❌ Deployment cancelled."
    exit 1
fi
