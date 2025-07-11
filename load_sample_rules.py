#!/usr/bin/env python3
"""
Load sample governance rules into the RAG system
"""

import json
import sys
import requests
import time
from pathlib import Path

def load_rules_from_file(api_url: str, file_path: str):
    """Load rules from a JSON file"""
    try:
        with open(file_path, 'r') as f:
            rules = json.load(f)
        
        print(f"📁 Loading {len(rules)} rules from {file_path}...")
        
        for rule in rules:
            response = requests.post(
                f"{api_url}/rules",
                json=rule,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"  ✅ Loaded: {rule['title']}")
                else:
                    print(f"  ❌ Failed to load {rule['title']}: {result.get('error')}")
            else:
                print(f"  ❌ HTTP {response.status_code} for {rule['title']}: {response.text}")
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.5)
            
    except Exception as e:
        print(f"❌ Error loading rules from {file_path}: {str(e)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 load_sample_rules.py <API_GATEWAY_URL>")
        sys.exit(1)
    
    api_url = sys.argv[1].rstrip('/')
    sample_rules_dir = Path("sample-rules")
    
    if not sample_rules_dir.exists():
        print("❌ sample-rules directory not found")
        sys.exit(1)
    
    print(f"🚀 Loading sample governance rules to {api_url}...")
    
    # Load all JSON files in the sample-rules directory
    for json_file in sample_rules_dir.glob("*.json"):
        load_rules_from_file(api_url, json_file)
    
    print("✅ Sample rules loading completed!")
    
    # Test query
    print("\n🔍 Testing rule query...")
    try:
        response = requests.post(
            f"{api_url}/rules/query",
            json={"query": "personal data privacy", "limit": 3},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                rules = result.get("rules", [])
                print(f"Found {len(rules)} relevant rules for 'personal data privacy':")
                for rule in rules[:3]:
                    print(f"  • {rule.get('title')} (score: {rule.get('score', 0):.3f})")
            else:
                print(f"❌ Query failed: {result.get('error')}")
        else:
            print(f"❌ Query HTTP {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing query: {str(e)}")

if __name__ == "__main__":
    main()
