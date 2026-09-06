# EdgeShield Mesh - Multi-Cloud Infrastructure as Code (Terraform)
# Provisions secure Edge IoT Gateway clusters across AWS, Azure, and GCP

terraform {
  required_version = ">= 1.5.0"
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

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "cluster_name" {
  type    = string
  default = "edgeshield-mesh-prod"
}

resource "aws_iot_thing_type" "edgeshield_gateway" {
  name = "EdgeShield_Gateway_V2"
  properties {
    description = "EdgeShield Mesh Autonomous Agentic Cybersecurity IoT Gateway"
  }
}

resource "aws_iot_thing" "mesh_gateway" {
  name            = "${var.cluster_name}-gw-01"
  thing_type_name = aws_iot_thing_type.edgeshield_gateway.name
  attributes = {
    pqc_enabled       = "true"
    consensus_role    = "raft_leader"
    satellite_enabled = "true"
  }
}

output "gateway_arn" {
  value       = aws_iot_thing.mesh_gateway.arn
  description = "The Amazon Resource Name of the deployed EdgeShield Gateway Thing"
}
