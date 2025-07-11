#!/usr/bin/env python3
"""
MCP Server for AI Governance Rules RAG System

This server provides tools for interacting with the governance rules API:
- load-governance-rule: Load a new governance rule
- query-governance-rules: Query rules by context/topic
- list-all-rules: List all available rules
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional
import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    TextContent,
    Tool,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_GATEWAY_URL = os.environ.get('API_GATEWAY_URL', 'https://your-api-gateway-url.amazonaws.com/dev')

class GovernanceRulesServer:
    def __init__(self):
        self.server = Server("governance-rules")
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Register handlers
        self.server.list_tools = self.list_tools
        self.server.call_tool = self.call_tool
    
    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        """List available tools"""
        return [
            Tool(
                name="load-governance-rule",
                description="Load a new AI governance rule into the system",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Title of the governance rule"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of what the rule governs"
                        },
                        "rule_text": {
                            "type": "string",
                            "description": "The actual rule text/content"
                        },
                        "category": {
                            "type": "string",
                            "description": "Category of the rule (e.g., 'privacy', 'safety', 'ethics')",
                            "default": "general"
                        },
                        "priority": {
                            "type": "integer",
                            "description": "Priority level (1-10, higher is more important)",
                            "default": 1
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags for categorizing the rule",
                            "default": []
                        }
                    },
                    "required": ["title", "rule_text"]
                }
            ),
            Tool(
                name="query-governance-rules",
                description="Query governance rules by context or topic using semantic search",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Query text describing the context or topic"
                        },
                        "category": {
                            "type": "string",
                            "description": "Optional category filter"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of rules to return",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="list-all-rules",
                description="List all available governance rules",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of rules to return",
                            "default": 100
                        }
                    }
                }
            )
        ]
    
    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Handle tool calls"""
        try:
            if request.params.name == "load-governance-rule":
                return await self._load_governance_rule(request.params.arguments)
            elif request.params.name == "query-governance-rules":
                return await self._query_governance_rules(request.params.arguments)
            elif request.params.name == "list-all-rules":
                return await self._list_all_rules(request.params.arguments)
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Unknown tool: {request.params.name}")]
                )
        except Exception as e:
            logger.error(f"Error calling tool {request.params.name}: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")]
            )
    
    async def _load_governance_rule(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Load a governance rule"""
        try:
            # Prepare rule data
            rule_data = {
                "title": arguments.get("title"),
                "description": arguments.get("description", ""),
                "rule_text": arguments.get("rule_text"),
                "category": arguments.get("category", "general"),
                "priority": arguments.get("priority", 1),
                "tags": arguments.get("tags", [])
            }
            
            # Make API request
            response = await self.http_client.post(
                f"{API_GATEWAY_URL}/rules",
                json=rule_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"✅ Successfully loaded governance rule '{rule_data['title']}' with ID: {result.get('rule_id')}"
                        )]
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"❌ Failed to load rule: {result.get('error', 'Unknown error')}"
                        )]
                    )
            else:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"❌ API request failed with status {response.status_code}: {response.text}"
                    )]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error loading rule: {str(e)}")]
            )
    
    async def _query_governance_rules(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Query governance rules"""
        try:
            query_data = {
                "query": arguments.get("query"),
                "category": arguments.get("category"),
                "limit": arguments.get("limit", 10)
            }
            
            # Remove None values
            query_data = {k: v for k, v in query_data.items() if v is not None}
            
            # Make API request
            response = await self.http_client.post(
                f"{API_GATEWAY_URL}/rules/query",
                json=query_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    rules = result.get("rules", [])
                    total = result.get("total", 0)
                    
                    if not rules:
                        return CallToolResult(
                            content=[TextContent(
                                type="text",
                                text=f"No governance rules found for query: '{arguments.get('query')}'"
                            )]
                        )
                    
                    # Format results
                    output = f"Found {len(rules)} governance rules (total: {total}):\n\n"
                    for i, rule in enumerate(rules, 1):
                        output += f"{i}. **{rule.get('title', 'Untitled')}**\n"
                        output += f"   Category: {rule.get('category', 'N/A')}\n"
                        output += f"   Priority: {rule.get('priority', 'N/A')}\n"
                        if rule.get('description'):
                            output += f"   Description: {rule['description']}\n"
                        output += f"   Rule: {rule.get('rule_text', 'N/A')}\n"
                        if rule.get('tags'):
                            output += f"   Tags: {', '.join(rule['tags'])}\n"
                        output += f"   Score: {rule.get('score', 'N/A'):.3f}\n\n"
                    
                    return CallToolResult(
                        content=[TextContent(type="text", text=output)]
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"❌ Query failed: {result.get('error', 'Unknown error')}"
                        )]
                    )
            else:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"❌ API request failed with status {response.status_code}: {response.text}"
                    )]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error querying rules: {str(e)}")]
            )
    
    async def _list_all_rules(self, arguments: Dict[str, Any]) -> CallToolResult:
        """List all governance rules"""
        try:
            limit = arguments.get("limit", 100)
            
            # Make API request
            response = await self.http_client.get(
                f"{API_GATEWAY_URL}/rules?limit={limit}"
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    rules = result.get("rules", [])
                    total = result.get("total", 0)
                    
                    if not rules:
                        return CallToolResult(
                            content=[TextContent(
                                type="text",
                                text="No governance rules found in the system."
                            )]
                        )
                    
                    # Format results
                    output = f"All Governance Rules ({len(rules)} of {total}):\n\n"
                    for i, rule in enumerate(rules, 1):
                        output += f"{i}. **{rule.get('title', 'Untitled')}**\n"
                        output += f"   ID: {rule.get('rule_id', 'N/A')}\n"
                        output += f"   Category: {rule.get('category', 'N/A')}\n"
                        output += f"   Priority: {rule.get('priority', 'N/A')}\n"
                        if rule.get('description'):
                            output += f"   Description: {rule['description']}\n"
                        output += f"   Rule: {rule.get('rule_text', 'N/A')}\n"
                        if rule.get('tags'):
                            output += f"   Tags: {', '.join(rule['tags'])}\n"
                        output += f"   Created: {rule.get('created_at', 'N/A')}\n\n"
                    
                    return CallToolResult(
                        content=[TextContent(type="text", text=output)]
                    )
                else:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"❌ Failed to list rules: {result.get('error', 'Unknown error')}"
                        )]
                    )
            else:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"❌ API request failed with status {response.status_code}: {response.text}"
                    )]
                )
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"❌ Error listing rules: {str(e)}")]
            )
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="governance-rules",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )

async def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("AI Governance Rules MCP Server")
        print("Usage: python server.py")
        print("\nEnvironment Variables:")
        print("  API_GATEWAY_URL - URL of the API Gateway endpoint")
        return
    
    server = GovernanceRulesServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
