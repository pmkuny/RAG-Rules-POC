import json
import os
import boto3
import logging
from typing import Dict, List, Any, Optional
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import hashlib
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
OPENSEARCH_ENDPOINT = os.environ['OPENSEARCH_ENDPOINT']
INDEX_NAME = os.environ['INDEX_NAME']
AWS_REGION = os.environ.get('AWS_REGION', os.environ.get('AWS_DEFAULT_REGION', 'us-east-1'))

# Initialize AWS clients
bedrock_runtime = boto3.client('bedrock-runtime', region_name=AWS_REGION)
session = boto3.Session()
credentials = session.get_credentials()

class OpenSearchClient:
    def __init__(self):
        logger.info(f"Initializing OpenSearch client for endpoint: {OPENSEARCH_ENDPOINT}")
        logger.info("Using IAM authentication with AWS request signing")
        
        # Create AWS V4 signer for authentication
        auth = AWSV4SignerAuth(credentials, AWS_REGION, 'es')
        
        # Initialize OpenSearch client with IAM authentication
        self.client = OpenSearch(
            hosts=[{'host': OPENSEARCH_ENDPOINT, 'port': 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=30
        )
        
        # Test connection first
        try:
            logger.info("Testing OpenSearch connection...")
            health = self.client.cluster.health()
            logger.info(f"OpenSearch cluster health: {health}")
        except Exception as e:
            logger.error(f"Failed to connect to OpenSearch: {str(e)}")
            raise
        
        # Try to ensure index exists, but don't fail if it doesn't work
        try:
            self._ensure_index_exists()
        except Exception as e:
            logger.warning(f"Could not ensure index exists during initialization: {str(e)}. Will continue anyway.")
    
    def _ensure_index_exists(self):
        """Create the index if it doesn't exist"""
        try:
            # Try to check if index exists
            if self.client.indices.exists(index=INDEX_NAME):
                logger.info(f"Index {INDEX_NAME} already exists")
                return
        except Exception as e:
            logger.warning(f"Could not check index existence: {str(e)}. Will attempt to create index.")
        
        # Try to create the index
        try:
            index_body = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "index": {
                        "knn": True,
                        "knn.algo_param.ef_search": 100
                    }
                },
                "mappings": {
                    "properties": {
                        "rule_id": {"type": "keyword"},
                        "title": {"type": "text"},
                        "description": {"type": "text"},
                        "category": {"type": "keyword"},
                        "priority": {"type": "integer"},
                        "tags": {"type": "keyword"},
                        "rule_text": {"type": "text"},
                        "embedding": {
                            "type": "knn_vector",
                            "dimension": 1536,
                            "method": {
                                "name": "hnsw",
                                "space_type": "cosinesimil",
                                "engine": "nmslib"
                            }
                        },
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"}
                    }
                }
            }
            self.client.indices.create(index=INDEX_NAME, body=index_body)
            logger.info(f"Created index: {INDEX_NAME}")
        except Exception as e:
            # If index creation fails, it might already exist
            logger.warning(f"Could not create index {INDEX_NAME}: {str(e)}. Index might already exist.")

def get_embedding(text: str) -> List[float]:
    """Generate embedding using Amazon Bedrock Titan Embeddings"""
    try:
        body = json.dumps({
            "inputText": text
        })
        
        response = bedrock_runtime.invoke_model(
            modelId="amazon.titan-embed-text-v1",
            body=body,
            contentType="application/json",
            accept="application/json"
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['embedding']
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        # Return a dummy embedding for development
        return [0.0] * 1536

def generate_rule_id(rule_text: str) -> str:
    """Generate a unique rule ID based on rule content"""
    return hashlib.md5(rule_text.encode()).hexdigest()[:12]

def load_rule(opensearch_client: OpenSearchClient, rule_data: Dict[str, Any]) -> Dict[str, Any]:
    """Load a governance rule into OpenSearch"""
    try:
        # Extract rule information
        rule_text = rule_data.get('rule_text', '')
        title = rule_data.get('title', '')
        description = rule_data.get('description', '')
        category = rule_data.get('category', 'general')
        priority = rule_data.get('priority', 1)
        tags = rule_data.get('tags', [])
        
        # Generate embedding for the rule
        embedding_text = f"{title} {description} {rule_text}"
        embedding = get_embedding(embedding_text)
        
        # Generate rule ID
        rule_id = generate_rule_id(rule_text)
        
        # Prepare document
        doc = {
            'rule_id': rule_id,
            'title': title,
            'description': description,
            'category': category,
            'priority': priority,
            'tags': tags,
            'rule_text': rule_text,
            'embedding': embedding,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Index the document
        response = opensearch_client.client.index(
            index=INDEX_NAME,
            id=rule_id,
            body=doc
        )
        
        logger.info(f"Loaded rule: {rule_id}")
        return {
            'success': True,
            'rule_id': rule_id,
            'message': 'Rule loaded successfully'
        }
        
    except Exception as e:
        logger.error(f"Error loading rule: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def query_rules(opensearch_client: OpenSearchClient, query_text: str, category: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
    """Query governance rules using vector similarity"""
    try:
        # Generate embedding for query
        query_embedding = get_embedding(query_text)
        
        # Build search query
        search_body = {
            "size": limit,
            "query": {
                "bool": {
                    "must": [
                        {
                            "knn": {
                                "embedding": {
                                    "vector": query_embedding,
                                    "k": limit
                                }
                            }
                        }
                    ]
                }
            },
            "_source": {
                "excludes": ["embedding"]
            }
        }
        
        # Add category filter if specified
        if category:
            search_body["query"]["bool"]["filter"] = [
                {"term": {"category": category}}
            ]
        
        # Execute search
        response = opensearch_client.client.search(
            index=INDEX_NAME,
            body=search_body
        )
        
        # Format results
        rules = []
        for hit in response['hits']['hits']:
            rule = hit['_source']
            rule['score'] = hit['_score']
            rules.append(rule)
        
        return {
            'success': True,
            'rules': rules,
            'total': response['hits']['total']['value']
        }
        
    except Exception as e:
        logger.error(f"Error querying rules: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def list_all_rules(opensearch_client: OpenSearchClient, limit: int = 100) -> Dict[str, Any]:
    """List all governance rules"""
    try:
        search_body = {
            "size": limit,
            "query": {"match_all": {}},
            "_source": {
                "excludes": ["embedding"]
            },
            "sort": [
                {"priority": {"order": "desc"}},
                {"created_at": {"order": "desc"}}
            ]
        }
        
        response = opensearch_client.client.search(
            index=INDEX_NAME,
            body=search_body
        )
        
        rules = [hit['_source'] for hit in response['hits']['hits']]
        
        return {
            'success': True,
            'rules': rules,
            'total': response['hits']['total']['value']
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error listing rules: {error_msg}")
        
        # If index doesn't exist, return empty results instead of error
        if "index_not_found_exception" in error_msg.lower() or "no such index" in error_msg.lower():
            logger.info(f"Index {INDEX_NAME} does not exist yet. Returning empty results.")
            return {
                'success': True,
                'rules': [],
                'total': 0
            }
        
        return {
            'success': False,
            'error': error_msg
        }

def lambda_handler(event, context):
    """Main Lambda handler"""
    try:
        # Initialize OpenSearch client
        opensearch_client = OpenSearchClient()
        
        # Parse request
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        body = event.get('body', '{}')
        
        if body:
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                body = {}
        
        # Route requests
        if http_method == 'POST' and path == '/rules':
            # Load rule
            result = load_rule(opensearch_client, body)
        elif http_method == 'GET' and path == '/rules':
            # List all rules
            query_params = event.get('queryStringParameters') or {}
            limit = int(query_params.get('limit', 100))
            result = list_all_rules(opensearch_client, limit)
        elif http_method == 'POST' and path == '/rules/query':
            # Query rules
            query_text = body.get('query', '')
            category = body.get('category')
            limit = body.get('limit', 10)
            result = query_rules(opensearch_client, query_text, category, limit)
        else:
            result = {
                'success': False,
                'error': f'Unsupported method/path: {http_method} {path}'
            }
        
        # Return response
        return {
            'statusCode': 200 if result.get('success') else 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error'
            })
        }
