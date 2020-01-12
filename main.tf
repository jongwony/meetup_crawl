variable "region" {
  default = "ap-northeast-2"
}

variable "function_name" {
  default = "test_func"
}

provider "archive" {}

data "archive_file" "dotfiles" {
  type = "zip"
  source_dir = "attendees/"
  output_path= "lambda.zip"
}

provider "aws" {
  region = var.region
}

data "aws_lambda_function" "existing" {
  function_name = var.function_name

}

resource "aws_lambda_function" "test_lambda" {
  filename = "lambda.zip"
  function_name = var.function_name
  handler = "lambda_function.lambda_handler"
  role = "service-role/test_func-role-pq3293cl"
  runtime = "python3.8"
}

