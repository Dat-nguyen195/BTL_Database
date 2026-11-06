"""Install the backend demo schema into a NEW database (never drops existing data)."""
import mysql.connector
import argparse
import os
from pathlib import Path
import re
import secrets
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'apps/backend'))

SQL_PATHS = [
    *sorted((ROOT / 'database/01_schema').glob('*.sql')),
    ROOT / 'database/02_constraints/01_constraints.sql',
    ROOT / 'database/03_indexes/01_indexes.sql',
    *sorted((ROOT / 'database/07_functions').glob('*.sql')),
    *sorted((ROOT / 'database/06_procedures').glob('*.sql')),
    *sorted((ROOT / 'database/08_triggers').glob('*.sql')),
    ROOT / 'database/04_seed/01_reference_data.sql',
    ROOT / 'database/04_seed/02_demo_scenarios.sql',
]


def sql_statements(text):
    delimiter = ';'
    buffered = []
    for line in text.splitlines():
        if line.strip().startswith('--') or not line.strip():
            continue
        if line.strip().upper().startswith('DELIMITER '):
            delimiter = line.strip().split()[1]
            continue
        buffered.append(line)
        if line.rstrip().endswith(delimiter):
            statement = '\n'.join(buffered).rstrip()[:-len(delimiter)].strip()
            if statement:
                yield statement
            buffered = []
    if buffered:
        raise ValueError('Unterminated SQL statement')


def initialize(conn, database, definer=None):
    if not re.fullmatch(r'[a-zA-Z0-9_]{1,64}', database):
        raise ValueError('Invalid database name')
    cur = conn.cursor()
    try:
        cur.execute(
            f'CREATE DATABASE `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs')
        cur.execute(f'USE `{database}`')
        cur.execute("SET time_zone='+07:00'")
        for file in SQL_PATHS:
            for statement in sql_statements(file.read_text(encoding='utf-8-sig')):
                if definer:
                    if not re.fullmatch(r"[a-zA-Z0-9_]{1,32}", definer):
                        raise ValueError("Invalid definer")
                    statement = re.sub(r"^CREATE (FUNCTION|PROCEDURE|TRIGGER) ",
                                       f"CREATE DEFINER=\"{definer}\"@\"%\" \\1 ", statement)
                cur.execute(statement)
                if cur.with_rows:
                    cur.fetchall()
        conn.commit()
    finally:
        cur.close()


def create_runtime_user(conn, database, username, password):
    if not re.fullmatch(r'[a-zA-Z0-9_]{1,32}', username) or not re.fullmatch(r'[a-zA-Z0-9_]{1,64}', database):
        raise ValueError('Invalid account/database identifier')
    cur = conn.cursor()
    try:
        cur.execute(f"CREATE USER %s@'%' IDENTIFIED BY %s",
                    (username, password))
        cur.execute(
            f"GRANT SELECT, EXECUTE ON `{database}`.* TO '{username}'@'%'")
        for table in ('DON_GOI_DICH_VU', 'CHI_TIET_GOI_DICH_VU', 'PHIEU_KHO', 'CHI_TIET_PHIEU_KHO'):
            cur.execute(
                f"GRANT INSERT ON `{database}`.`{table}` TO '{username}'@'%'")
    finally:
        cur.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', default='quan_net_btl2')
    parser.add_argument('--create-app-user', action='store_true')
    parser.add_argument('--p12', action='store_true',
                        help='Nạp dữ liệu minh họa P1–2 trên database mới')
    args = parser.parse_args()
    conn = mysql.connector.connect(host=os.getenv('DB_HOST', '127.0.0.1'), port=int(os.getenv(
        'DB_PORT', '3306')), user=os.getenv('DB_OWNER_USER', 'root'), password=os.getenv('DB_OWNER_PASSWORD', ''), use_pure=True)
    try:
        initialize(conn, args.database)
        if args.p12:
            from seed_demo_p12 import apply_seed
            apply_seed(conn)
        if args.create_app_user:
            password = os.environ['DB_PASSWORD']
            if not password:
                raise ValueError('DB_PASSWORD is required')
            create_runtime_user(conn, args.database, os.getenv(
                'DB_USER', 'quan_net_app'), password)
        print('Installed new database:', args.database)
    finally:
        conn.close()
