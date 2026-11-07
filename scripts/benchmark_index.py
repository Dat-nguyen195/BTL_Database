"""Đo Q-P12-02 trên database tạm; lưu kế hoạch và số đo thực tế."""
import json,os,secrets,time,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'apps/backend'))
from dotenv import load_dotenv
import mysql.connector
from submission_queries import queries

def run_benchmark(connection=None,on_step=None):
    load_dotenv(ROOT/'.env')
    own=connection is None
    conn=connection or mysql.connector.connect(host=os.getenv('TD_TEST_DB_HOST',os.getenv('DB_HOST','127.0.0.1')),port=int(os.getenv('TD_TEST_DB_PORT',os.getenv('DB_PORT','13307'))),user=os.getenv('TD_TEST_DB_OWNER','root'),password=os.getenv('TD_TEST_DB_PASSWORD') or os.environ['MYSQL_ROOT_PASSWORD'],use_pure=True,autocommit=True)
    previous=conn.database;cur=conn.cursor();db='btl2_benchmark_'+secrets.token_hex(6)
    try:
        cur.execute(f'CREATE DATABASE `{db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_as_cs');cur.execute(f'USE `{db}`')
        for statement in ["CREATE TABLE NHOM_DICH_VU(MaNhomDV VARCHAR(10) PRIMARY KEY,TenNhomDV VARCHAR(50))", "CREATE TABLE DON_VI_TINH(MaDonVi VARCHAR(10) PRIMARY KEY,TenDonVi VARCHAR(30))", "CREATE TABLE DICH_VU(MaDichVu VARCHAR(10) PRIMARY KEY,TenDichVu VARCHAR(100),GiaBanHienHanh DECIMAL(10,0),SoLuongTon INT,TrangThaiKinhDoanh VARCHAR(20),MaNhomDV VARCHAR(10),MaDonVi VARCHAR(10),FOREIGN KEY(MaNhomDV) REFERENCES NHOM_DICH_VU(MaNhomDV),FOREIGN KEY(MaDonVi) REFERENCES DON_VI_TINH(MaDonVi))"]:cur.execute(statement)
        cur.executemany('INSERT INTO NHOM_DICH_VU VALUES(%s,%s)',[(f'NDV{i:02d}',f'Nhóm {i}') for i in range(1,11)])
        cur.execute("INSERT INTO DON_VI_TINH VALUES ('DVT01','Phần'),('DVT02','Chai')")
        rows=[(f'DV{i:05d}',f'Mặt hàng {i}',5000+(i%95)*1000,i%200,['DangKinhDoanh','NgungKinhDoanh'][i%2],f'NDV{(i%10)+1:02d}', 'DVT01' if i%2==0 else 'DVT02') for i in range(1,20001)]
        for offset in range(0,len(rows),1000):cur.executemany('INSERT INTO DICH_VU VALUES(%s,%s,%s,%s,%s,%s,%s)',rows[offset:offset+1000])
        query=queries()['Q-P12-02'].rstrip(';');results={}
        for phase in ['before','after']:
            if phase=='after':cur.execute('CREATE INDEX ix_dich_vu_filter ON DICH_VU(MaNhomDV,TrangThaiKinhDoanh,GiaBanHienHanh,MaDichVu)')
            cur.execute('EXPLAIN ANALYZE '+query);plan='\n'.join(r[0] for r in cur.fetchall())
            start=time.perf_counter()
            for _ in range(20):cur.execute(query);found=cur.fetchall()
            results[phase]={'mean_ms':(time.perf_counter()-start)*1000/20,'rows':len(found),'plan':plan,'has_sort':'Sort:' in plan}
            if on_step:on_step('index_'+phase, 'EXPLAIN ANALYZE '+query)
        results.update(dbms=conn.get_server_info(),table_rows=20000,iterations=20,query=query,index='CREATE INDEX ix_dich_vu_filter ON DICH_VU(MaNhomDV,TrangThaiKinhDoanh,GiaBanHienHanh,MaDichVu)',speedup=results['before']['mean_ms']/results['after']['mean_ms'])
        target=ROOT/'evidence/queries';target.mkdir(exist_ok=True,parents=True)
        (target/'index_benchmark.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
        return results
    finally:
        cur.execute(f'DROP DATABASE IF EXISTS `{db}`')
        if previous:cur.execute(f'USE `{previous}`')
        cur.close()
        if own:conn.close()

if __name__=='__main__':
    r=run_benchmark();print('Đã lưu benchmark thật:',round(r['speedup'],2),'lần')
