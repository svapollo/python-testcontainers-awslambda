import base64
import logging
import pymysql
import json
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_secrets(secret_names):
    region_name = "sa-east-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    secrets = {}
    for secret_name in secret_names:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)

        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(get_secret_value_response['SecretBinary'])

        secrets[secret_name] = json.loads(secret)

    return secrets


def connect_to_database():
    secrets = get_secrets(['RDS_PROXY_HOST', 'RDS_PROXY_PORT', 'USER_NAME', 'PASSWORD', 'DB_NAME'])
    try:
        conn = pymysql.connect(host=secrets['RDS_PROXY_HOST'],
                               port=int(secrets['RDS_PROXY_PORT']),
                               user=secrets['USER_NAME'],
                               password=secrets['PASSWORD'],
                               db=secrets['DB_NAME'])
        logger.info("SUCCESS: Connection to RDS for MySQL instance succeeded")
        return conn
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        raise e


def lambda_handler(event, context):
    conn = connect_to_database()
    try:
        message = event['Records'][0]['body']
        insert_data(conn, message)
    except Exception as e:
        raise e
    finally:
        conn.close()


def insert_data(conn, message):
    data = json.loads(message)
    cust_id = data['cust_id']
    name = data['name']

    sql_string = "insert into customer (cust_id, Name) values(%s, %s)"

    with conn.cursor() as cur:
        cur.execute(sql_string, (cust_id, name))
        item_count = cur.rowcount
    conn.commit()

    return "Added %d items to RDS for MySQL table" %(item_count)
