# configures a specified provider
provider "aws" {
    region = "us-west-2"
}

# resource "resource type" "resource name"
# ec2 instance with ami id image and instance type
resource "aws_instance" "app_server" {
    ami = ""
    instance_type = ""

    tags = {
        Name = ""
    }
}