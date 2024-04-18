import pytest
import subprocess
import pymysql
import json
import lambda_function as lf
import time


def start_database():
    subprocess.run(["podman-compose", "up", "-d"], check=True)
    time.sleep(30)


def stop_database():
    subprocess.run(["podman-compose", "down"], check=True)


@pytest.fixture(scope="module", autouse=True)
def setup_teardown():
    start_database()
    yield
    stop_database()


def test_insert_data():
    conn = pymysql.connect(host='localhost',
                           port=3306,
                           user='root',
                           password='password',
                           db='db_test')
    message = json.dumps({'cust_id': 1, 'name': 'Test'})
    lf.insert_data(conn, message)
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM db_test.customer WHERE cust_id = 1")
        result = cur.fetchone()
    assert result[1] == 'Test'
