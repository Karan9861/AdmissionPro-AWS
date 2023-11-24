terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = "ap-south-1"
  access_key = "your_access_key"
  secret_key = "your_secret_key"
}

# Create a VPC
resource "aws_instance" "terraform-instance" {
  ami = "ami-099b3d23e336c2e83"
  instance_type = "t2.micro"
  key_name = "terraform key"
  security_groups = [ "terraform-group" ]
  user_data = "${file("data.sh")}"

  tags = {
    "Name" = "deployment-instance"
  }
}

data "aws_db_instance" "existing_database" {
  # Specify filters to identify the existing RDS instance
  db_instance_identifier = "database-1"
}
