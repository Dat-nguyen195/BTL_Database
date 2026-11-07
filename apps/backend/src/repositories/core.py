"""Small cursor helpers. Repositories never own transaction boundaries."""
from src.errors import InternalError

def one(conn, sql, args=()):
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, args)
        return cur.fetchone()
    finally:
        cur.close()

def all_rows(conn, sql, args=()):
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, args)
        return cur.fetchall()
    finally:
        cur.close()

def execute(conn, sql, args=()):
    cur = conn.cursor()
    try:
        cur.execute(sql, args)
        return cur.rowcount
    finally:
        cur.close()

def call(conn, name, args):
    cur = conn.cursor()
    try:
        cur.callproc(name, args)
        results = []
        for result in cur.stored_results():
            results.append(result.fetchall())
        if len(results) != 1 or len(results[0]) != 1 or len(results[0][0]) != 2:
            raise InternalError("Routine trả kết quả không đúng hợp đồng.")
        key, replay = results[0][0]
        if replay not in (0, 1):
            raise InternalError("Routine trả cờ replay không hợp lệ.")
        return key, bool(replay)
    finally:
        cur.close()


def lock_row(conn, table, key):
    # Definer helper grants locking without direct UPDATE/DELETE/LOCK TABLES.
    if table not in {'NGUOI_CHOI','MAY_TRAM','PHIEN_SU_DUNG','DON_GOI_DICH_VU','PHIEU_KHO','DICH_VU'}:
        raise ValueError('Unsupported lock target')
    cur=conn.cursor(dictionary=True)
    try:
        cur.callproc('sp_khoa_dong',(table,key))
        sets=[result.fetchall() for result in cur.stored_results()]
        if len(sets)!=1 or len(sets[0])>1:
            raise InternalError('Lock helper returned invalid results')
        return sets[0][0] if sets[0] else None
    finally:
        cur.close()
