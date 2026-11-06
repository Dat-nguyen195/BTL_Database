"""Nạp seed P1–2 một lần; không ghi đè dữ liệu hiện hữu."""
from bootstrap_backend import sql_statements
import mysql.connector
from dotenv import load_dotenv
import os
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'apps/backend'), str(ROOT / 'scripts')]


def apply_seed(conn):
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT COUNT(*) FROM DON_GOI_DICH_VU WHERE MaDonHang IN ('DH_P12_01','DH_P12_02')")
        existing = cur.fetchone()[0]
        if existing == 2:
            expected = {
                'MAY_TRAM': ('MaMay', ['M04', 'M05', 'M06']),
                'DICH_VU': ('MaDichVu', ['DV03', 'DV04', 'DV05', 'DV06']),
                'NGUOI_CHOI': ('MaTaiKhoan', ['TK09', 'TK10']),
                'CA_TRUC': ('MaCa', ['CA02', 'CA03']),
                'PHIEN_SU_DUNG': ('MaPhien', ['PH_P12_01']),
                'BIEN_LAI_TIEN_MAY': ('MaBienLai', ['BL_P12_01'])}
            for table, (key, ids) in expected.items():
                cur.execute(
                    f"SELECT COUNT(*) FROM `{table}` WHERE `{key}` IN ({','.join(['%s'] * len(ids))})", ids)
                if cur.fetchone()[0] != len(ids):
                    raise RuntimeError(
                        'Seed P1–2 chưa đầy đủ; dùng database mới, không ghi đè dữ liệu.')
            print('Dữ liệu P1–2 đã tồn tại; giữ nguyên dữ liệu.')
            return False
        cur.execute("SELECT COUNT(*) FROM MAY_TRAM WHERE MaMay='M04'")
        if existing or cur.fetchone()[0]:
            raise RuntimeError(
                'Seed P1–2 chưa đầy đủ hoặc trùng mã. Hãy dùng database mới; không ghi đè dữ liệu.')
        if not conn.in_transaction:
            conn.start_transaction()
        try:
            for stmt in sql_statements((ROOT / 'database/04_seed/03_p12_demo_seed.sql').read_text(encoding='utf-8-sig')):
                cur.execute(stmt)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        return True
    finally:
        cur.close()


def seed_demo_p12(database=None):
    load_dotenv(ROOT / '.env')
    conn = mysql.connector.connect(host=os.getenv('DB_HOST', '127.0.0.1'), port=int(os.getenv('DB_PORT', '13307')), user=os.getenv('DB_OWNER_USER', 'root'), password=os.getenv(
        'DB_OWNER_PASSWORD') or os.environ['MYSQL_ROOT_PASSWORD'], database=database or os.getenv('DB_NAME', 'quan_net_btl2'), use_pure=True, autocommit=True)
    try:
        apply_seed(conn)
    finally:
        conn.close()


if __name__ == '__main__':
    seed_demo_p12()
