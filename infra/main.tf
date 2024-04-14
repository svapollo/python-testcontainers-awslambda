resource "aws_iam_role" "lambda_role" {
  name = "lambda_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "lambda_policy"
  role = aws_iam_role.lambda_role.id

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "rds:DescribeDBInstances",
        "rds:Connect"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_lambda_function" "lambda_testcontainers" {
  function_name = "lambda_testcontainers"

  filename = "lambda_testcontainers.zip"
  source_code_hash = filebase64sha256("lambda_testcontainers.zip")
  handler = "lambda_function.lambda_handler"
  runtime = "python3.8"

  role = aws_iam_role.lambda_role.arn
}
