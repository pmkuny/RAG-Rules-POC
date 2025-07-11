# RAG Rules POC - Architecture Documentation

## Overview

This proof-of-concept implements a RAG (Retrieval-Augmented Generation) system for AI governance rules using AWS services. The system allows AI assistants to query and retrieve relevant governance rules before processing user requests.

## Architecture Components

### 1. OpenSearch Domain
- **Purpose**: Vector database for storing governance rules with embeddings
- **Features**: 
  - Full-text search capabilities
  - Vector similarity search using k-NN
  - Secure access with authentication
- **Index Structure**:
  - `rule_id`: Unique identifier
  - `title`: Rule title
  - `description`: Rule description
  - `category`: Rule category (privacy, safety, ethics, etc.)
  - `priority`: Priority level (1-10)
  - `tags`: Searchable tags
  - `rule_text`: Full rule content
  - `embedding`: 1536-dimensional vector (Titan embeddings)
  - `created_at`/`updated_at`: Timestamps

### 2. Lambda Function
- **Purpose**: Backend logic for rule management
- **Runtime**: Python 3.11
- **Key Functions**:
  - `load_rule()`: Store new governance rules
  - `query_rules()`: Semantic search using embeddings
  - `list_all_rules()`: Retrieve all rules
- **Dependencies**:
  - `opensearch-py`: OpenSearch client
  - `boto3`: AWS SDK for Bedrock embeddings
  - `aws-requests-auth`: Authentication

### 3. API Gateway
- **Purpose**: REST API interface
- **Endpoints**:
  - `POST /rules`: Load new rules
  - `GET /rules`: List all rules
  - `POST /rules/query`: Query rules by semantic similarity
- **Features**:
  - CORS enabled
  - Regional endpoint
  - Lambda proxy integration

### 4. MCP Server
- **Purpose**: Model Context Protocol server for Q CLI integration
- **Tools Provided**:
  - `load-governance-rule`: Add new rules
  - `query-governance-rules`: Search rules by context
  - `list-all-rules`: List all available rules
- **Protocol**: Stdio-based MCP communication

## Data Flow

1. **Rule Loading**:
   ```
   MCP Client → MCP Server → API Gateway → Lambda → OpenSearch
   ```

2. **Rule Querying**:
   ```
   MCP Client → MCP Server → API Gateway → Lambda → Bedrock (embeddings) → OpenSearch → Results
   ```

3. **Vector Search Process**:
   - User query converted to embedding via Bedrock Titan
   - k-NN search in OpenSearch using cosine similarity
   - Results ranked by relevance score
   - Metadata returned (excluding embeddings for efficiency)

## Security

### Authentication & Authorization
- OpenSearch: Internal user database with admin credentials
- Lambda: IAM role with minimal required permissions
- API Gateway: Open endpoints (can be secured with API keys if needed)

### Data Protection
- OpenSearch: Encryption at rest and in transit
- Lambda: Environment variables for sensitive configuration
- Network: VPC deployment optional (currently public for simplicity)

## Scalability Considerations

### Current Limitations
- Single OpenSearch instance (t3.small.search)
- No auto-scaling configured
- Basic error handling

### Scaling Options
- Multi-AZ OpenSearch deployment
- Lambda concurrency limits
- API Gateway throttling
- CloudFront for caching

## Cost Optimization

### Current Configuration
- OpenSearch: t3.small.search instance (~$25/month)
- Lambda: Pay-per-request (minimal cost for POC)
- API Gateway: Pay-per-request
- Bedrock: Pay-per-token for embeddings

### Optimization Strategies
- Use OpenSearch Serverless for variable workloads
- Implement embedding caching
- Batch rule loading operations

## Monitoring & Observability

### Available Metrics
- Lambda: Duration, errors, invocations
- API Gateway: Request count, latency, errors
- OpenSearch: Cluster health, search performance

### Recommended Monitoring
- CloudWatch dashboards
- X-Ray tracing for Lambda
- OpenSearch slow query logs
- Custom metrics for rule usage patterns

## Development Workflow

1. **Infrastructure Changes**: Modify Terraform files
2. **Lambda Updates**: Update code and run `./deploy-lambda.sh`
3. **MCP Server Changes**: Update Python code directly
4. **Rule Management**: Use MCP tools or direct API calls

## Testing Strategy

### Unit Tests
- Lambda function logic
- MCP server tool implementations
- Rule validation and formatting

### Integration Tests
- End-to-end API workflows
- OpenSearch indexing and querying
- MCP protocol communication

### Performance Tests
- Query response times
- Concurrent request handling
- Large rule set performance

## Future Enhancements

### Short Term
- Rule versioning and history
- Bulk rule import/export
- Enhanced error handling and logging
- API authentication

### Long Term
- Multi-tenant support
- Rule conflict detection
- Advanced analytics and reporting
- Integration with other AI governance tools
- Real-time rule updates and notifications
