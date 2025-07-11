#!/usr/bin/env python3
"""
Direct CLI interface for Governance Rules API
Workaround for Q CLI MCP tool validation issues
"""

import argparse
import json
import requests
import sys
from typing import Dict, List, Optional

# API Gateway URL
API_GATEWAY_URL = "https://t9rfu4e2s7.execute-api.us-east-1.amazonaws.com/dev"

def list_all_rules(limit: int = 100) -> Dict:
    """List all governance rules"""
    try:
        response = requests.get(f"{API_GATEWAY_URL}/rules")
        response.raise_for_status()
        data = response.json()
        
        if limit and limit < len(data.get('rules', [])):
            data['rules'] = data['rules'][:limit]
            
        return data
    except Exception as e:
        return {"error": str(e)}

def query_rules(query: str, category: Optional[str] = None, limit: int = 10) -> Dict:
    """Query governance rules by context"""
    try:
        payload = {
            "query": query,
            "limit": limit
        }
        if category:
            payload["category"] = category
            
        response = requests.post(f"{API_GATEWAY_URL}/rules/query", json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def load_rule(title: str, rule_text: str, description: str = "", 
              category: str = "general", priority: int = 5, tags: List[str] = None) -> Dict:
    """Load a new governance rule"""
    try:
        payload = {
            "title": title,
            "rule_text": rule_text,
            "description": description,
            "category": category,
            "priority": priority,
            "tags": tags or []
        }
        
        response = requests.post(f"{API_GATEWAY_URL}/rules", json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Governance Rules CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all governance rules')
    list_parser.add_argument('--limit', type=int, default=100, help='Maximum number of rules to return')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query governance rules')
    query_parser.add_argument('query', help='Query text')
    query_parser.add_argument('--category', help='Optional category filter')
    query_parser.add_argument('--limit', type=int, default=10, help='Maximum number of rules to return')
    
    # Load command
    load_parser = subparsers.add_parser('load', help='Load a new governance rule')
    load_parser.add_argument('title', help='Rule title')
    load_parser.add_argument('rule_text', help='Rule content')
    load_parser.add_argument('--description', default='', help='Rule description')
    load_parser.add_argument('--category', default='general', help='Rule category')
    load_parser.add_argument('--priority', type=int, default=5, help='Rule priority (1-10)')
    load_parser.add_argument('--tags', nargs='*', default=[], help='Rule tags')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'list':
        result = list_all_rules(args.limit)
    elif args.command == 'query':
        result = query_rules(args.query, args.category, args.limit)
    elif args.command == 'load':
        result = load_rule(args.title, args.rule_text, args.description, 
                          args.category, args.priority, args.tags)
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
