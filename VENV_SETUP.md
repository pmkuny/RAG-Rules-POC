# Virtual Environment Setup for RAG Rules POC

This document outlines the virtual environment setup and modifications made to the RAG Rules POC project.

## 🔧 New Files Created

### Scripts
- `setup-venv.sh` - Main virtual environment setup script
- `activate.sh` - Convenience script to activate the virtual environment
- `mcp-server/run-server.sh` - MCP server wrapper that uses virtual environment

### Configuration
- `.gitignore` - Excludes virtual environment and generated files
- `requirements-dev.txt` - Development dependencies
- `VENV_SETUP.md` - This documentation file

## 📝 Modified Files

### `deploy.sh`
- Added virtual environment check and auto-setup
- Updated to use virtual environment for loading sample rules
- Updated MCP configuration output to use wrapper script

### `deploy-lambda.sh`
- Modified to use virtual environment for dependency installation
- Fixed zip file path issues
- Added proper virtual environment activation/deactivation

### `README.md`
- Added virtual environment setup instructions
- Updated step numbering (1. Setup Virtual Environment, 2. Deploy Infrastructure, etc.)
- Updated MCP configuration examples to use wrapper script
- Updated test instructions

### `mcp-config-example.json`
- Updated to use the MCP server wrapper script instead of direct Python execution

## 🚀 Usage

### Initial Setup
```bash
# Setup virtual environment and install all dependencies
./setup-venv.sh
```

### Manual Activation
```bash
# Activate virtual environment
source ./activate.sh

# Or manually
source venv/bin/activate
```

### Deployment
```bash
# Deploy (will auto-setup virtual environment if needed)
./deploy.sh
```

### MCP Server
```bash
# Run MCP server (uses virtual environment automatically)
cd mcp-server
./run-server.sh
```

## 🎯 Benefits

1. **Dependency Isolation**: Project dependencies are isolated from system Python
2. **Reproducible Environment**: Consistent Python environment across different machines
3. **Version Control**: Virtual environment excluded from git, but requirements are tracked
4. **Easy Setup**: Single command setup for new developers
5. **Automatic Management**: Deployment scripts handle virtual environment automatically

## 🔍 Virtual Environment Structure

```
rag-rules.poc/
├── venv/                    # Virtual environment (excluded from git)
│   ├── bin/
│   ├── lib/
│   └── ...
├── setup-venv.sh           # Setup script
├── activate.sh             # Activation convenience script
├── requirements-dev.txt    # Development dependencies
└── .gitignore             # Excludes venv/ and other generated files
```

## 🛠️ Troubleshooting

### Virtual Environment Not Found
```bash
# If you see "Virtual environment not found" errors:
./setup-venv.sh
```

### Permission Issues
```bash
# Make scripts executable if needed:
chmod +x setup-venv.sh activate.sh mcp-server/run-server.sh
```

### Python Version Issues
```bash
# Verify Python 3 is available:
python3 --version

# If using different Python version:
python3.11 -m venv venv  # Replace with your Python version
```

## 🧹 Cleanup

To remove the virtual environment:
```bash
rm -rf venv/
```

To recreate:
```bash
./setup-venv.sh
```
