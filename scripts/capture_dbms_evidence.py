"""Chạy SQL thật trong MySQL riêng và chụp toàn màn hình SQL client.
Cần requirements-dev.lock và Chrome. Không ghi mật khẩu vào log/minh chứng.
"""
from pathlib import Path
import json,os,secrets,shutil,sys,time
from threading import Thread
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'apps/backend'),str(ROOT/'scripts')]
from dotenv import load_dotenv
import mysql.connector
from flask import Flask,request,jsonify,render_template_string
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright
from bootstrap_backend import initialize,sql_statements
from seed_demo_p12 import apply_seed
from submission_queries import queries
from benchmark_index import run_benchmark

HTML='''<!doctype html><html lang="vi"><meta charset="utf-8"><title>MySQL SQL Client — BTL2</title><style>
*{box-sizing:border-box}body{font:18px Arial;margin:0;color:#17243a;background:#eef2f6}header{background:#172d49;color:white;padding:18px 24px}h1{font-size:24px;margin:0 0 7px}main{padding:18px 24px}textarea{width:100%;height:205px;font:15px monospace;white-space:pre;background:white;border:1px solid #8191a8;padding:12px}button{background:#126b58;color:white;padding:9px 20px;border:0;margin:8px 0;font-size:17px}table{border-collapse:collapse;background:white;width:100%;font-size:16px;margin:8px 0 16px}th,td{border:1px solid #a5b2c3;padding:5px;text-align:left;overflow-wrap:anywhere}th{background:#dce7f1}pre{white-space:pre-wrap;font:14px monospace}.error{color:#a41424;background:#fff0f0;padding:9px}.status{color:#1d6651;font-size:16px}h2{font-size:19px;margin:8px 0}#results{max-height:620px;overflow:auto}footer{font-size:13px;color:#526278;margin-top:12px}</style>
<header><h1>MySQL SQL Client</h1><div>Máy chủ MySQL {{ version }} · Kết nối local · Phiên kiểm chứng BTL2 L09 Nhóm 09</div></header>
<main><h2 id="label">SQL và kết quả trực tiếp từ MySQL</h2><textarea id="sql" spellcheck="false"></textarea><button id="run">Thực thi SQL</button><span id="state"></span><div id="results"></div><footer>SQL được gửi tới MySQL thật. Mỗi ảnh có câu lệnh và đầu ra JSON tương ứng trong evidence/dbms.</footer></main>
<script>
let lastResult=null;document.querySelector('#run').onclick=async()=>{document.querySelector('#state').textContent='Đang chạy';let response=await fetch('/execute',{method:'POST',headers:{'Content-Type':'application/json','X-Token':{{ token|tojson }}},body:JSON.stringify({sql:document.querySelector('#sql').value})});lastResult=await response.json();let box=document.querySelector('#results');box.replaceChildren();for(let r of lastResult.results){let h=document.createElement('div');h.className=r.error?'error':'status';h.textContent=r.error?('ERROR '+r.errno+' ('+r.sqlstate+'): '+r.error):(r.rows.length+' dòng · '+r.elapsed_ms.toFixed(2)+' ms');box.append(h);if(r.rows.length){let rows=r.rows;let columns=r.columns;if(columns.length===1&&typeof rows[0][0]==='string'){try{let arr=JSON.parse(rows[0][0]);if(Array.isArray(arr)&&arr.length&&typeof arr[0]==='object'){columns=Object.keys(arr[0]);rows=arr.map(x=>columns.map(k=>x[k]));}}catch(e){}}let t=document.createElement('table');let hr=t.insertRow();columns.forEach(c=>{let th=document.createElement('th');th.textContent=c;hr.append(th)});rows.forEach(row=>{let tr=t.insertRow();row.forEach(v=>{let td=tr.insertCell();td.textContent=v===null?'NULL':v})});box.append(t)}}document.querySelector('#state').textContent=lastResult.database+' · Hoàn tất';};
</script></html>'''

def capture():
    load_dotenv(ROOT/'.env')
    conn=mysql.connector.connect(host=os.getenv('TD_TEST_DB_HOST',os.getenv('DB_HOST','127.0.0.1')),port=int(os.getenv('TD_TEST_DB_PORT',os.getenv('DB_PORT','13307'))),user=os.getenv('TD_TEST_DB_OWNER','root'),password=os.getenv('TD_TEST_DB_PASSWORD') or os.environ['MYSQL_ROOT_PASSWORD'],use_pure=True,autocommit=True)
    db='btl2_evidence_'+secrets.token_hex(6);app=Flask(__name__);token=secrets.token_hex(24)
    assets=ROOT/'evidence/report_assets';logs=ROOT/'evidence/dbms';assets.mkdir(exist_ok=True,parents=True);logs.mkdir(exist_ok=True,parents=True)
    manifest=[];version=conn.get_server_info()
    @app.get('/')
    def home():return render_template_string(HTML,version=version,token=token)
    @app.post('/execute')
    def execute():
        if request.headers.get('X-Token')!=token:return jsonify(error='Forbidden'),403
        results=[]
        for statement in sql_statements(request.json['sql']):
            cur=conn.cursor();started=time.perf_counter()
            try:
                cur.execute(statement);sets=[]
                while True:
                    columns=list(cur.column_names) if cur.with_rows else []
                    rows=[json.loads(json.dumps(list(r),default=str)) for r in cur.fetchall()] if cur.with_rows else []
                    if columns:sets.append({'columns':columns,'rows':rows})
                    if not cur.nextset():break
                if not sets:sets=[{'columns':[],'rows':[]}]
                for s in sets:results.append(dict(s,sql=statement,elapsed_ms=(time.perf_counter()-started)*1000,error=None))
            except mysql.connector.Error as e:results.append(dict(sql=statement,columns=[],rows=[],errno=e.errno,sqlstate=e.sqlstate,error=e.msg,elapsed_ms=(time.perf_counter()-started)*1000))
            finally:cur.close()
        # jsonify serializes Decimal as string; store identical values in raw evidence.
        return jsonify(database=conn.database,version=version,results=results)
    server=None
    try:
        initialize(conn,db);apply_seed(conn)
        server=make_server('127.0.0.1',0,app,threaded=False);thread=Thread(target=server.serve_forever,daemon=True);thread.start()
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=shutil.which('google-chrome') or shutil.which('chromium'),headless=True,args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':1200,'height':1100},device_scale_factor=2.5);page.goto(f'http://127.0.0.1:{server.server_port}')
            def shot(name,sql):
                sql=sql.rstrip().rstrip(";")+";"
                page.locator('#label').evaluate('(el,t)=>el.textContent=t',name)
                page.locator('#sql').fill(sql);page.evaluate('lastResult=null');page.locator('#run').click();page.wait_for_function('lastResult!==null');data=page.evaluate('lastResult')
                page.locator('#sql').evaluate('(el)=>el.scrollTop=0');
                (logs/(name+'.sql')).write_text(sql+'\n');(logs/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
                # A real SQL-client print preserves vector text; expand result overflow instead of clipping rows.
                page.add_style_tag(content='#results{max-height:none;overflow:visible} body{background:white} textarea{height:170px;font-size:16px} footer{margin-bottom:10px}')
                page.screenshot(path=str(assets/(name+'.png')),full_page=True)
                pdf_dir=ROOT/'docs/report/latex/assets/dbms';pdf_dir.mkdir(parents=True,exist_ok=True)
                footer_box=page.locator('footer').bounding_box()
                height=footer_box['y']+footer_box['height']+15
                page.pdf(path=str(pdf_dir/(name+'.pdf')),width='1200px',height=str(height+8)+'px',print_background=True,margin={'top':'0','right':'0','bottom':'0','left':'0'})
                manifest.append({'name':name,'sql':name+'.sql','result':name+'.json','image':'../report_assets/'+name+'.png','vector_pdf':'../../docs/report/latex/assets/dbms/'+name+'.pdf','errors':[r['errno'] for r in data['results'] if r['error']]})
                return data
            shot('img_01_dbms_tables',"SHOW TABLES;\nSELECT VERSION() AS MySQLVersion, COUNT(*) AS SoBang FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE();")
            shot('img_02_dbms_constraints',"INSERT INTO MAY_TRAM(MaMay,TenMay,TrangThaiMay,MaNhomMay,MaKhuVuc) VALUES('BAD_FK','Sai FK','AVAILABLE','NONE','KV01');\nUPDATE MAY_TRAM SET TrangThaiMay='INVALID' WHERE MaMay='M01';\nSELECT MaMay,TrangThaiMay,MaNhomMay,MaKhuVuc FROM MAY_TRAM WHERE MaMay='M01';")
            shot('routines_created',"SELECT ROUTINE_NAME,ROUTINE_TYPE FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA=DATABASE() ORDER BY ROUTINE_TYPE,ROUTINE_NAME;")
            shot('triggers_created',"SELECT TRIGGER_NAME,EVENT_MANIPULATION,EVENT_OBJECT_TABLE FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=DATABASE() AND EVENT_OBJECT_TABLE IN ('BIEN_LAI_TIEN_MAY','CHI_TIET_GOI_DICH_VU');")
            samples={1:"SELECT MaMay,MaNhomMay,MaKhuVuc,TrangThaiMay FROM MAY_TRAM;\nSELECT * FROM KHU_VUC;\nSELECT MaNhomMay,TenNhomMay,DonGiaGioMacDinh FROM NHOM_MAY;",2:"SELECT MaDichVu,TenDichVu,GiaBanHienHanh,MaNhomDV,MaDonVi FROM DICH_VU;\nSELECT * FROM NHOM_DICH_VU;\nSELECT * FROM DON_VI_TINH;",3:"SELECT MaDonHang,ThoiDiemDat,KenhDat,TongTien,TrangThaiThanhToan FROM DON_GOI_DICH_VU;",4:"SELECT MaNhanVien,MaCa,MaKhuVuc FROM PHAN_CONG_TRUC;\nSELECT MaCa,ThoiDiemBatDau,ThoiDiemKetThuc FROM CA_TRUC;\nSELECT MaTaiKhoan,ChucVu FROM NHAN_VIEN;",5:"SELECT MaTaiKhoan,SoDuVi FROM NGUOI_CHOI;\nSELECT MaNguoiChoi,LoaiGiaoDich,SoTien,TrangThaiGD FROM GIAO_DICH_VI;"}
            for i,sql in enumerate(queries().values(),1):
                shot(f'q{i:02d}_data',samples[i]);shot(f'img_{i+3:02d}_q{i:02d}',sql)
            shot('img_09_crud_insert',"CALL sp_khu_vuc_insert('KV99','Khu Demo','Tầng 2');\nCALL sp_khu_vuc_insert('KV99','Khu Demo','Tầng 2');\nSELECT * FROM KHU_VUC WHERE MaKhuVuc='KV99';")
            shot('img_10_crud_update',"CALL sp_khu_vuc_update('KV99','Khu Demo Mới','Tầng 3');\nCALL sp_khu_vuc_update('KV_NONE','Không có','');\nSELECT * FROM KHU_VUC WHERE MaKhuVuc='KV99';")
            shot('img_11_crud_delete',"CALL sp_khu_vuc_delete('KV01');\nCALL sp_khu_vuc_delete('KV99');\nSELECT COUNT(*) AS ConLai FROM KHU_VUC WHERE MaKhuVuc='KV99';")
            shot('img_12_trigger_t1',"SELECT MaBienLai,TrangThaiBienLai,TongTienGio FROM BIEN_LAI_TIEN_MAY;\nUPDATE BIEN_LAI_TIEN_MAY SET TongTienGio=99999 WHERE MaBienLai='BL_P12_01';\nDELETE FROM BIEN_LAI_TIEN_MAY WHERE MaBienLai='BL_P12_01';\nSELECT MaBienLai,TrangThaiBienLai,TongTienGio FROM BIEN_LAI_TIEN_MAY;")
            shot('trigger_t1_valid', "INSERT INTO PHIEN_SU_DUNG(MaPhien,MaMay,MaNguoiChoi,HinhThucDangNhap,ThoiDiemBatDau,ThoiDiemKetThuc,DonGiaGioApDung,TienNapTruoc,TienGiuCho,TongTienTamTinh,TrangThaiPhien) VALUES('P_VALID','M04',NULL,'MienPhi','2026-10-23 10:00:00','2026-10-23 11:00:00',0,0,0,0,'DaKetThuc');\nINSERT INTO BIEN_LAI_TIEN_MAY(MaBienLai,MaPhien,ThoiDiemLap,TongTienGio,TienNhan,TienHoan,HinhThucThanhToan,TrangThaiBienLai,MaNhanVienThu) VALUES('BL_REVIEW','P_VALID',NOW(),0,0,0,'MienPhi','ChuaThanhToan','TK03');\nUPDATE BIEN_LAI_TIEN_MAY SET TienNhan=1,TienHoan=1 WHERE MaBienLai='BL_REVIEW';\nSELECT MaBienLai,TrangThaiBienLai,TienNhan,TienHoan FROM BIEN_LAI_TIEN_MAY WHERE MaBienLai='BL_REVIEW';\nDELETE FROM BIEN_LAI_TIEN_MAY WHERE MaBienLai='BL_REVIEW';\nSELECT COUNT(*) AS ConLai FROM BIEN_LAI_TIEN_MAY WHERE MaBienLai='BL_REVIEW';")
            # Existing paid receipt covers errors; valid DML is shown on a separate fresh unpaid receipt/session.
            shot('trigger_t2_before',"INSERT INTO DON_GOI_DICH_VU(MaDonHang,ThoiDiemDat,KenhDat,TongTien,TrangThaiPhucVu,TrangThaiThanhToan,SoTienDaHoan) VALUES('DH_EVIDENCE',NOW(),'TaiQuay',0,'MoiDat','ChuaThanhToan',0);\nSELECT MaDonHang,TongTien FROM DON_GOI_DICH_VU WHERE MaDonHang='DH_EVIDENCE';")
            shot('img_13_trigger_t2',"INSERT INTO CHI_TIET_GOI_DICH_VU(MaDonHang,MaDichVu,SoLuong,DonGiaBan) VALUES('DH_EVIDENCE','DV01',2,15000);\nSELECT MaDonHang,TongTien FROM DON_GOI_DICH_VU WHERE MaDonHang='DH_EVIDENCE';\nUPDATE CHI_TIET_GOI_DICH_VU SET SoLuong=3 WHERE MaDonHang='DH_EVIDENCE';\nSELECT MaDonHang,TongTien FROM DON_GOI_DICH_VU WHERE MaDonHang='DH_EVIDENCE';\nDELETE FROM CHI_TIET_GOI_DICH_VU WHERE MaDonHang='DH_EVIDENCE';\nSELECT MaDonHang,TongTien FROM DON_GOI_DICH_VU WHERE MaDonHang='DH_EVIDENCE';")
            shot('trigger_t2_errors',"INSERT INTO CHI_TIET_GOI_DICH_VU VALUES('DH_P12_01','DV04',1,18000,DEFAULT);\nUPDATE CHI_TIET_GOI_DICH_VU SET SoLuong=2 WHERE MaDonHang='DH_P12_01';\nDELETE FROM CHI_TIET_GOI_DICH_VU WHERE MaDonHang='DH_P12_01';")
            shot('img_14_sp_doanh_thu',"CALL sp_bao_cao_doanh_thu_ngay('2026-10-25','2026-10-20');\nCALL sp_bao_cao_doanh_thu_ngay('2026-10-20','2026-10-22');")
            shot('img_15_sp_ton_kho',"CALL sp_bao_cao_ton_dich_vu('NDV02',-1);\nCALL sp_bao_cao_ton_dich_vu('NDV02',10);")
            shot('img_16_fn_chi_vi',"SELECT fn_tong_chi_vi_rong('TK02','2026-10-01','2026-11-01') AS TongChi;\nSELECT fn_tong_chi_vi_rong('TK_NONE','2026-10-01','2026-11-01') AS KhongTonTai;")
            shot('img_17_fn_tien_don',"SELECT fn_tong_tien_don('DH_P12_01') AS TongTien;\nSELECT fn_tong_tien_don('DH_NONE') AS KhongTonTai;")
            run_benchmark(conn,shot)
            shutil.copy2(assets/'index_after.png',assets/'img_03_dbms_indexes.png')
            browser.close()
        (logs/'manifest.json').write_text(json.dumps({'mysql_version':version,'source':'live MySQL SQL client','shots':manifest},ensure_ascii=False,indent=2)+'\n')
        print('Đã chụp',len(manifest),'ảnh từ kết quả MySQL thật')
    finally:
        if server:server.shutdown()
        cur=conn.cursor();cur.execute(f'DROP DATABASE IF EXISTS `{db}`');cur.close();conn.close()

if __name__=='__main__':capture()
