def login_as(client,username='admin',password='MatKhau123!'):
    token=client.get('/api/v1/auth/csrf').json['data']['CsrfToken']
    result=client.post('/api/v1/auth/login',json={'TenDangNhap':username,'MatKhau':password},headers={'X-CSRF-Token':token})
    assert result.status_code==200,result.json
    return result.json['data']['CsrfToken']

def post(client,path,token,body):
    return client.post('/api/v1'+path,json=body,headers={'X-CSRF-Token':token})
