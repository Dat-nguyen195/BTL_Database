"""Prepare an isolated local MySQL demo, then serve Flask and the prepaid worker.
Run with apps/backend/.venv/bin/python scripts/start_backend_demo.py.
Creates .env only if absent; never replaces credentials or drops an existing DB.
"""
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'apps/backend'),str(ROOT/'scripts')]
from dotenv import load_dotenv
import mysql.connector
from bootstrap_backend import initialize,create_runtime_user

def prepare():
    envfile=ROOT/'.env'
    if not envfile.exists():
        values={
            'DB_HOST':'127.0.0.1','DB_PORT':'13307','DB_NAME':'quan_net_btl2',
            'DB_USER':'quan_net_app','DB_PASSWORD':secrets.token_hex(24),
            'DB_OWNER_USER':'quan_net_owner','DB_OWNER_PASSWORD':secrets.token_hex(24),
            'MYSQL_ROOT_PASSWORD':secrets.token_hex(24),'SECRET_KEY':secrets.token_hex(32),
            'BACKEND_HOST':'127.0.0.1','BACKEND_PORT':'5000','SESSION_COOKIE_SECURE':'false',
        }
        fd=os.open(envfile,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w') as f:
            f.write('# Local generated demo credentials; excluded from version control.\n')
            f.write('\n'.join(f'{k}={v}' for k,v in values.items())+'\n')
    load_dotenv(envfile)
    for key in ('MYSQL_ROOT_PASSWORD','DB_OWNER_PASSWORD','DB_PASSWORD','SECRET_KEY'):
        if not os.getenv(key):raise RuntimeError(f'{key} must be set in local .env')
    subprocess.run(['docker','compose','--env-file',str(envfile),'-f',str(ROOT/'infrastructure/compose.backend.yaml'),'up','-d'],cwd=ROOT,check=True)
    root=None
    for _ in range(60):
        try:
            root=mysql.connector.connect(host=os.getenv('DB_HOST','127.0.0.1'),port=int(os.getenv('DB_PORT','13307')),user='root',password=os.environ['MYSQL_ROOT_PASSWORD'],use_pure=True,connection_timeout=2,autocommit=True)
            break
        except mysql.connector.Error:time.sleep(1)
    if root is None:raise RuntimeError('Local MySQL did not become ready')
    database=os.getenv('DB_NAME','quan_net_btl2')
    owner_name=os.getenv('DB_OWNER_USER','quan_net_owner')
    import re
    if not re.fullmatch(r'[A-Za-z0-9_]{1,64}',database) or not re.fullmatch(r'[A-Za-z0-9_]{1,32}',owner_name):raise ValueError('Invalid identifiers')
    cur=root.cursor()
    try:
        cur.execute('SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME=%s',(database,))
        exists=cur.fetchone() is not None
        if not exists:
            cur.execute("CREATE USER IF NOT EXISTS %s@'%' IDENTIFIED BY %s",(owner_name,os.environ['DB_OWNER_PASSWORD']))
            cur.execute(f"GRANT ALL PRIVILEGES ON `{database}`.* TO '{owner_name}'@'%'")
            initialize(root,database,definer=owner_name)
            from seed_demo_p12 import apply_seed
            apply_seed(root)
            create_runtime_user(root,database,os.getenv('DB_USER','quan_net_app'),os.environ['DB_PASSWORD'])
            print('Created local demo schema and restricted runtime account.',flush=True)
        else:
            print('Using existing local database; no reset performed.',flush=True)
    finally:
        cur.close();root.close()

if __name__=='__main__':
    prepare()
    from src.app import create_app
    from src.config import Config
    from src.services.worker import start_worker,stop_worker
    start_worker()
    try:
        print(f'Open http://{Config.BACKEND_HOST}:{Config.BACKEND_PORT}',flush=True)
        create_app().run(host=Config.BACKEND_HOST,port=Config.BACKEND_PORT,debug=False)
    finally:stop_worker()
