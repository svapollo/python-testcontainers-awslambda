import os
from dotenv import load_dotenv
import pymysql
import pytest
from testcontainers.mysql import MySqlContainer
import lambda_function as lf

load_dotenv()


def setup_database(conn):
    with conn.cursor() as cur:
        cur.execute("CREATE DATABASE IF NOT EXISTS test;")
        cur.execute("USE test;")
        cur.execute("CREATE TABLE IF NOT EXISTS customer "
                    "(cust_id INT PRIMARY KEY,"
                    " name VARCHAR(255));")
        conn.commit()


def teardown_database(conn):
    with conn.cursor() as cur:
        cur.execute("USE test;")
        cur.execute("DROP TABLE customer;")
        conn.commit()


@pytest.fixture(scope="function")
def db_setup():
    with MySqlContainer('mysql:5.7').with_bind_ports(3306, None) as mysql:
        host_port = mysql.get_exposed_port(3306)

        os.environ['RDS_PROXY_HOST'] = mysql.get_container_host_ip()
        os.environ['RDS_PROXY_PORT'] = str(host_port)

        conn = pymysql.connect(host=os.environ['RDS_PROXY_HOST'],
                               port=int(os.environ['RDS_PROXY_PORT']),
                               user=os.environ['USER_NAME'],
                               password=os.environ['PASSWORD'],
                               db=os.environ['DB_NAME'])

        setup_database(conn)

        yield conn

        teardown_database(conn)


def test_insert_data_into_empty_table_should_return_one(db_setup):
    conn = db_setup
    event = {
        'Records': [
            {
                'body': '{"cust_id": 1, "name": "test"}'
            }
        ]
    }
    message = event['Records'][0]['body']
    result = lf.insert_data(conn, message)
    assert result == 'Added 1 items to RDS for MySQL table'


def test_insert_data_into_not_empty_table_should_return_one(db_setup):
    conn = db_setup
    event_one = {
        'Records': [
            {
                'body': '{"cust_id": 1, "name": "test1"}'
            }
        ]
    }
    message_one = event_one['Records'][0]['body']
    result_one = lf.insert_data(conn, message_one)
    assert result_one == 'Added 1 items to RDS for MySQL table'

    event_two = {
        'Records': [
            {
                'body': '{"cust_id": 2, "name": "test2"}'
            }
        ]
    }
    message_two = event_two['Records'][0]['body']
    result_two = lf.insert_data(conn, message_two)
    assert result_two == 'Added 1 items to RDS for MySQL table'
