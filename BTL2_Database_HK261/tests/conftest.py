"""Real MySQL integration fixtures. Never emulate SQL or routine side effects."""
import os
from pathlib import Path
import secrets
import sys
from uuid import uuid4
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'apps/backend'),str(ROOT/'scripts'),str(ROOT/'tests')]
from src.app import create_app
from src.config import Config
import mysql.connector
from bootstrap_backend import initialize, create_runtime_user

@pytest.fixture
def db_conn(monkeypatch):
    port=os.getenv('TD_TEST_DB_PORT')
    if not port:
        pytest.skip('Set TD_TEST_DB_PORT to run actual MySQL integration tests')
    suffix=uuid4().hex[:12]
    database='quan_net_test_'+suffix
    username='td_test_'+suffix
    password=secrets.token_hex(24)
    owner=mysql.connector.connect(host=os.getenv('TD_TEST_DB_HOST','127.0.0.1'),port=int(port),user=os.getenv('TD_TEST_DB_OWNER','root'),password=os.getenv('TD_TEST_DB_PASSWORD',''),use_pure=True,autocommit=True)
    try:
        initialize(owner,database)
        create_runtime_user(owner,database,username,password)
        for key,value in {'DB_HOST':os.getenv('TD_TEST_DB_HOST','127.0.0.1'),'DB_PORT':int(port),'DB_NAME':database,'DB_USER':username,'DB_PASSWORD':password}.items():
            monkeypatch.setattr(Config,key,value)
        yield owner
    finally:
        owner.rollback()
        cur=owner.cursor()
        try:
            cur.execute(f'DROP DATABASE IF EXISTS `{database}`')
            cur.execute(f"DROP USER IF EXISTS '{username}'@'%'")
        finally:
            cur.close()
            owner.close()

@pytest.fixture
def app(db_conn):
    return create_app({'TESTING':True,'SECRET_KEY':secrets.token_hex(32)})

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def sql(db_conn):
    def query(statement,args=()):
        cur=db_conn.cursor(dictionary=True)
        try:
            cur.execute(statement,args)
            return cur.fetchall() if cur.with_rows else cur.rowcount
        finally:
            cur.close()
    return query
