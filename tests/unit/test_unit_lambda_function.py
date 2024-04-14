import lambda_function as lf
from moto import mock_aws
import boto3


@mock_aws
def test_get_secret():
    conn = boto3.client("secretsmanager", region_name="sa-east-1")
    conn.create_secret(Name="db_teste", SecretString='{"username": "test", "password": "test"}')
    secrets = lf.get_secrets(secret_names=["db_teste"])
    assert secrets == {"db_teste": {"username": "test", "password": "test"}}
