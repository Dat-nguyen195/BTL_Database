"""Three actual UI → HTTP → MySQL flows in local Chrome; optional browser dependency."""
import json
import os
from pathlib import Path
import shutil
from threading import Thread
import pytest
from werkzeug.serving import make_server


def test_three_flows_in_browser(app,sql,monkeypatch):
    from datetime import datetime
    from src import clock
    monkeypatch.setattr(clock,"now",lambda:datetime(2026,10,26,9,0,0))
    playwright=pytest.importorskip('playwright.sync_api')
    chrome=shutil.which('google-chrome') or shutil.which('chromium')
    if not chrome:
        pytest.skip('Chrome/Chromium is required for browser E2E')
    server=make_server('127.0.0.1',0,app,threaded=True)
    thread=Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        with playwright.sync_playwright() as automation:
            browser=automation.chromium.launch(executable_path=chrome,headless=True,args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':1440,'height':1100})
            errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            def submit(form,path):
                with page.expect_response(lambda response: response.url.endswith('/api/v1'+path) and response.request.method=='POST') as pending:
                    page.locator(form+' button[type=submit], '+form+' button:not([type])').first.click()
                response=pending.value
                assert response.status in (200,201),response.text()
                return response.json()
            page.goto(f'http://127.0.0.1:{server.server_port}')
            page.locator('#login-form [name=TenDangNhap]').fill('admin')
            page.locator('#login-form [name=MatKhau]').fill('MatKhau123!')
            submit('#login-form','/auth/login')
            page.locator('#dashboard').wait_for(state='visible')
            page.wait_for_function("document.querySelector('#machine-select').options.length>0")
            # D1: Open and settle a member session, verify actual receipt/machine.
            opened=submit('#session-form','/sessions')
            session_id=opened['data']['MaPhien']
            page.wait_for_function("document.querySelector('#close-session-id').value !== ''")
            submit('#close-form',f'/sessions/{session_id}/close')
            assert sql('SELECT COUNT(*) AS n FROM BIEN_LAI_TIEN_MAY WHERE MaPhien=%s',(session_id,))[0]['n']==1
            assert sql("SELECT TrangThaiMay FROM MAY_TRAM WHERE MaMay='M01'")[0]['TrangThaiMay']=='AVAILABLE'
            # D2: Topup replay, draft → acceptance → wallet payment.
            topup=submit('#topup-form','/wallet/topups')
            repeated=submit('#topup-form','/wallet/topups')
            assert repeated['meta']['replayed']
            assert topup['data']['MaGiaoDich']==repeated['data']['MaGiaoDich']
            page.locator('[data-new="session-form"]').click()
            page.wait_for_function("document.querySelector('#machine-select').options.length>0")
            submit('#session-form','/sessions')
            page.locator('#order-form [name=KenhDat]').select_option('TaiMay')
            created=submit('#order-form','/orders')
            order_id=created['data']['MaDonHang']
            page.wait_for_function("document.querySelector('#action-order-id').value !== ''")
            with page.expect_response(lambda r:r.url.endswith(f'/orders/{order_id}/accept')) as pending:
                page.locator('#accept-order').click()
            assert pending.value.status==200
            assert sql("SELECT SoLuongTon FROM DICH_VU WHERE MaDichVu='DV01'")[0]['SoLuongTon']==48
            page.locator('#order-action-form [name=HinhThucThanhToan]').select_option('TruVi')
            submit('#order-action-form',f'/orders/{order_id}/pay')
            assert sql("SELECT SoLuongTon FROM DICH_VU WHERE MaDichVu='DV01'")[0]['SoLuongTon']==48
            assert sql("SELECT SoDuVi FROM NGUOI_CHOI WHERE MaTaiKhoan='TK02'")[0]['SoDuVi']==170000
            # D3: Draft does not change stock; post changes once; reports are real.
            document=submit('#inventory-form','/inventory-documents')
            document_id=document['data']['MaPhieuKho']
            assert sql("SELECT SoLuongTon FROM DICH_VU WHERE MaDichVu='DV01'")[0]['SoLuongTon']==48
            page.wait_for_function("document.querySelector('#post-document-id').value !== ''")
            submit('#post-form',f'/inventory-documents/{document_id}/post')
            replay=submit('#post-form',f'/inventory-documents/{document_id}/post')
            assert replay['meta']['replayed']
            assert sql("SELECT SoLuongTon FROM DICH_VU WHERE MaDichVu='DV01'")[0]['SoLuongTon']==68
            page.locator('#report-form [name=report]').select_option('revenue')
            page.locator('#report-form [name=FromDate]').fill('2026-10-26')
            page.locator('#report-form [name=ToDate]').fill('2026-10-26')
            with page.expect_response(lambda r:'/reports/revenue?' in r.url) as pending:
                page.locator('#report-form button').click()
            assert pending.value.status==200
            assert pending.value.json()['data']['TongDoanhThu']==30000
            assert not errors,errors
            evidence=os.getenv('TD_BROWSER_EVIDENCE_DIR')
            if evidence:
                target=Path(evidence);target.mkdir(parents=True,exist_ok=True)
                page.screenshot(path=str(target/'TD_browser_three_flows.png'),full_page=True)
                (target/'TD_browser_three_flows.json').write_text(json.dumps({'browser':browser.version,'flows':['D1','D2','D3'],'final_stock':68,'service_revenue':30000,'topup_replay':True,'post_replay':True,'javascript_errors':errors},ensure_ascii=False,indent=2)+'\n')
            browser.close()
    finally:
        server.shutdown();thread.join(timeout=5)
