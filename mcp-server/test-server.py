#!/usr/bin/env python3
"""
Minimal MCP Server for testing Q CLI integration
"""

import asyncio
import logging
from typing import Any, Dict, List
from mcp.server import Server
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

class TestMCPServer:
    def __init__(self):
        self.server = Server("test-server")
        
        # Register handlers
        self.server.list_tools = self.list_tools
        self.server.call_tool = self.call_tool
    
    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        """List available tools"""
        return [
            Tool(
                name="hello-world",
                description="A simple test tool that returns a greeting",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name to greet",
                            "default": "World"
                        }
                    }
                }
            )
        ]
    
    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Handle tool calls"""
        try:
            if request.params.name == "hello-world":
                name = request.params.arguments.get("name", "World")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Hello, {name}!")]
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Unknown tool: {request.params.name}")]
                )
        except Exception as e:
            logger.error(f"Error calling tool {request.params.name}: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")]
            )
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

async def main():
    """Main entry point"""
    server = TestMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
