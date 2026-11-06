"""Capture sanitized actual responses and balance/stock assertions for the backend report."""
import json
import os
from pathlib import Path
from uuid import uuid4
from tests_helpers import login_as,post


def test_capture_real_api_results(client,sql):
    token=login_as(client)
    before=sql("SELECT SoDuVi FROM NGUOI_CHOI WHERE MaTaiKhoan='TK02'")[0]['SoDuVi']
    body={'MaGiaoDich':'G_EVIDENCE','MaYeuCau':'nap:'+str(uuid4()),'MaNguoiChoi':'TK02','SoTien':10000,'PhuongThucGD':'TienMat'}
    first=post(client,'/wallet/topups',token,body)
    replay=post(client,'/wallet/topups',token,body)
    conflict=post(client,'/wallet/topups',token,dict(body,SoTien=20000))
    invalid=post(client,'/wallet/topups',token,dict(body,SoTien=1.9))
    after=sql("SELECT SoDuVi FROM NGUOI_CHOI WHERE MaTaiKhoan='TK02'")[0]['SoDuVi']
    assert [r.status_code for r in [first,replay,conflict,invalid]]==[201,200,409,422]
    assert int(after-before)==10000
    if os.getenv('TD_BROWSER_EVIDENCE_DIR'):
        path=Path(os.environ['TD_BROWSER_EVIDENCE_DIR'])/'TD_api_samples.json'
        path.write_text(json.dumps({'before_balance':int(before),'after_balance':int(after),'request':body,'responses':{name:{'status':response.status_code,'body':response.json} for name,response in [('create',first),('replay',replay),('conflict',conflict),('fraction_rejected',invalid)]}},ensure_ascii=False,indent=2)+'\n')
