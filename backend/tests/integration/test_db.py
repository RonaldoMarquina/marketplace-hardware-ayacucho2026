import os

import pytest

pytestmark = pytest.mark.integration
import pymysql
from dotenv import load_dotenv


@pytest.mark.integration
def test_conexion_mysql_configurada():
    if os.getenv("RUN_INTEGRATION_TESTS") != "1":
        pytest.skip("Prueba de integracion desactivada.")

    load_dotenv()
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        pytest.skip("DATABASE_URL no esta configurada.")

    parts = database_url.replace("mysql+pymysql://", "").split("@")
    user_pass = parts[0].split(":")
    host_db = parts[1].split("/")
    host_port = host_db[0].split(":")

    connection = pymysql.connect(
        host=host_port[0],
        user=user_pass[0],
        password=user_pass[1] if len(user_pass) > 1 else "",
        port=int(host_port[1]) if len(host_port) > 1 else 3306,
        database=host_db[1] if len(host_db) > 1 else "",
        cursorclass=pymysql.cursors.DictCursor,
    )

    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 AS ok")
        result = cursor.fetchone()

    connection.close()
    assert result["ok"] == 1

