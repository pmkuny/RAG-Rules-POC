terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Random suffix for unique naming
resource "random_id" "suffix" {
  byte_length = 4
}

locals {
  name_prefix = "rag-rules-${random_id.suffix.hex}"
  common_tags = {
    Project     = "RAG-Rules-POC"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
