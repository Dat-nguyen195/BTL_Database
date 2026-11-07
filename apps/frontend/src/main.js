import {api, code} from './services/api.js';
const $ = selector => document.querySelector(selector);
let user;
const keys = new Map();
function value(id) { return Object.fromEntries(new FormData($(id))); }
const labels={MaPhien:'Mã phiên',MaMay:'Máy',MaNguoiChoi:'Hội viên',MaDonHang:'Mã đơn',MaPhieuKho:'Mã phiếu',MaDichVu:'Mã dịch vụ',TenDichVu:'Dịch vụ',SoLuong:'Số lượng',DonGiaBan:'Đơn giá',ThanhTien:'Thành tiền',TongTien:'Tổng tiền',SoDuVi:'Số dư ví',SoDuKhaDung:'Có thể chi',TienGiuCho:'Tiền giờ giữ chỗ',CanUseUntil:'Hạn dùng',PhiHienTai:'Tiền giờ hiện tại',TrangThaiPhien:'Trạng thái phiên',TrangThaiPhucVu:'Phục vụ',TrangThaiThanhToan:'Thanh toán',TrangThaiPhieu:'Trạng thái phiếu',ThoiDiemBatDau:'Bắt đầu',ThoiDiemKetThuc:'Kết thúc',ThoiDiemThanhToan:'Đã thu lúc',TongDoanhThu:'Tổng doanh thu',LoaiDoanhThu:'Nguồn thu',TongTienGio:'Tiền giờ',TienNhan:'Tiền nhận',TienHoan:'Tiền hoàn',DonGiaGioApDung:'Giá giờ',TienNapTruoc:'Tiền nạp trước',TongTienTamTinh:'Tiền giờ tích lũy',TenMay:'Tên máy',TenDangNhap:'Tài khoản',KenhDat:'Kênh đặt',HinhThucDangNhap:'Loại phiên',HinhThucThanhToan:'Cách thanh toán',SoLuongTon:'Tồn kho',TonHienTai:'Tồn hiện tại',TongNhap:'Nhập kho',TongXuatHuy:'Xuất hủy',TongBan:'Đã bán',BienDongRong:'Thay đổi tồn',ChenhLechKiemKe:'Lệch kiểm kê',SoLuongSoSach:'Tồn sổ sách',SoLuongThucTe:'Đếm thực tế',SoLuongChenhLech:'Chênh lệch',DonGiaVon:'Giá vốn',GhiChuLyDo:'Lý do',LoaiPhieu:'Loại phiếu',SoTien:'Số tiền',PhuongThucGD:'Phương thức',Ngay:'Ngày',Kenh:'Kênh',SoGiaoDich:'Số giao dịch',Lines:'Chi tiết',BienLai:'Biên lai',ChiTiet:'Chi tiết',Phien:'Phiên',Don:'Đơn',MaNhanVienXuLy:'Nhân viên',MaNhanVienThu:'Người thu',ThoiDiemLap:'Lập lúc',ThoiDiemDat:'Đặt lúc',ThoiDiemGhiSo:'Ghi sổ lúc',ThoiDiemGD:'Giao dịch lúc',MaGiaoDich:'Mã giao dịch',TrangThaiGD:'Trạng thái',LoaiGiaoDich:'Giao dịch',MaBienLai:'Mã biên lai',TrangThaiBienLai:'Trạng thái biên lai',FromDate:'Từ ngày',ToDate:'Đến ngày',STTDong:'Dòng',MaNhanVien:'Nhân viên',MaCa:'Mã ca',TenCa:'Ca',ChongGio:'Chồng giờ',MaKhuVuc:'Khu vực',TenKhuVuc:'Tên khu',GhiChuNhiemVu:'Nhiệm vụ'};
function readable(data,depth=0){
  const pad='  '.repeat(depth);
  if(Array.isArray(data)) return data.length?data.map((x,i)=>`${pad}${i+1}.\n${readable(x,depth+1)}`).join('\n'):`${pad}Chưa có dữ liệu.`;
  if(data && typeof data==='object') return Object.entries(data).filter(([k,v])=>v!==null && k!=='MaYeuCau').map(([k,v])=>typeof v==='object'?`${pad}${labels[k]||k}:\n${readable(v,depth+1)}`:`${pad}${labels[k]||k}: ${typeof v==='boolean'?(v?'Có':'Không'):v}`).join('\n');
  return pad+String(data);
}
function show(id,data){$(id).textContent=readable(data);}
function notice(message, error=false) { $('#notice').textContent=message; $('#notice').dataset.error=error; }
function stable(form,payload,prefix) {
  const serialized=JSON.stringify(payload);
  const saved=keys.get(form);
  if (!saved || saved.serialized!==serialized) keys.set(form,{serialized,key:code(prefix),request:'nap:'+crypto.randomUUID()});
  return keys.get(form);
}
async function run(action) {
  try { await action(); } catch(error) { notice(error.message,true); }
}
function bind(id,action) {
  $(id).addEventListener('submit',event=>{ event.preventDefault(); run(async()=>{
    const button=$(id+' button');button.disabled=true;
    try { await action(value(id)); } finally {button.disabled=false;}
  }); });
}
function result(id,response) {show(id,response.data);notice(response.meta.replayed?'Yêu cầu đã được xử lý trước đó; không ghi thêm lần nữa.':'Thao tác thành công.');}
function option(select,items,label) {
  const old=select.value;select.replaceChildren();
  for(const [key,title] of items) {const opt=document.createElement('option');opt.value=key;opt.textContent=title;select.append(opt);}
  if([...select.options].some(x=>x.value===old))select.value=old;
}
async function refresh() {
  const [machines,services,sessions,orders]=await Promise.all(['/workstations','/services','/sessions','/orders'].map(x=>api(x)));
  const table=document.createElement('table');
  for(const fields of [['Máy','Trạng thái','Khu vực'],...machines.data.map(x=>[x.TenMay,x.TrangThaiMay,x.TenKhuVuc])]) {
    const row=table.insertRow();for(const field of fields) row.insertCell().textContent=field;
  }
  $('#machines').replaceChildren(table);
  option($('#machine-select'),machines.data.filter(x=>x.TrangThaiMay==='AVAILABLE').map(x=>[x.MaMay,x.TenMay]));
  for(const id of ['#order-service','#inventory-service'])option($(id),services.data.map(x=>[x.MaDichVu,`${x.TenDichVu} · ${x.GiaBanHienHanh.toLocaleString('vi-VN')}đ · tồn ${x.SoLuongTon}`]));
  show('#overview',{Phien:sessions.data,Don:orders.data});
}
async function signedIn(identity) {
  user=identity;$('#login-panel').hidden=true;$('#dashboard').hidden=false;$('#logout').hidden=false;
  $('#account').textContent=`${user.TenDangNhap} · ${user.roles.join(', ')}`;
  for(const element of document.querySelectorAll('[data-staff]')) element.hidden=!element.dataset.staff.split(',').some(x=>user.roles.includes(x));
  if(!user.roles.some(x=>['QuanLy','ThuNgan'].includes(x))) {
    $('#session-form [name=MaNguoiChoi]').value=user.MaTaiKhoan;
    $('#session-form [name=MaNguoiChoi]').readOnly=true;
  }
  await refresh();notice('Đã đăng nhập.');
}
bind('#login-form',async data=>signedIn((await api('/auth/login',data)).data));
$('#logout').onclick=()=>run(async()=>{await api('/auth/logout',{});location.reload();});
$('#refresh').onclick=()=>run(refresh);
for(const button of document.querySelectorAll('[data-new]'))button.onclick=()=>{keys.delete('#'+button.dataset.new);notice('Đã tạo ngữ cảnh yêu cầu mới.');};
bind('#session-form',async data=>{
  data.MaNguoiChoi=data.MaNguoiChoi||null;data.TienNapTruoc=Number(data.TienNapTruoc);
  data.MaPhien=stable('#session-form',data,'P').key;
  const response=await api('/sessions',data);result('#session-result',response);
  $('#close-session-id').value=data.MaPhien;$('#order-session-id').value=data.MaPhien;await refresh();
});
bind('#close-form',async data=>{
  const key=data.MaPhien;delete data.MaPhien;data.TienNhan=Number(data.TienNhan);
  const response=await api('/sessions/'+encodeURIComponent(key)+'/close',data);result('#close-result',response);await refresh();
});
bind('#topup-form',async data=>{
  data.SoTien=Number(data.SoTien);const stableKey=stable('#topup-form',data,'G');
  const response=await api('/wallet/topups',{...data,MaGiaoDich:stableKey.key,MaYeuCau:stableKey.request});result('#wallet-result',response);await refresh();
});
bind('#order-form',async data=>{
  const payload={KenhDat:data.KenhDat,MaPhien:data.KenhDat==='TaiMay'?data.MaPhien:null,Lines:[{MaDichVu:data.MaDichVu,SoLuong:Number(data.SoLuong)}]};
  payload.MaDonHang=stable('#order-form',payload,'O').key;
  const response=await api('/orders',payload);result('#order-result',response);$('#action-order-id').value=payload.MaDonHang;await refresh();
});
$('#accept-order').onclick=()=>run(async()=>{const key=$('#action-order-id').value;result('#order-result',await api('/orders/'+encodeURIComponent(key)+'/accept',{}));await refresh();});
bind('#order-action-form',async data=>{result('#order-result',await api('/orders/'+encodeURIComponent(data.MaDonHang)+'/pay',{HinhThucThanhToan:data.HinhThucThanhToan}));await refresh();});
bind('#inventory-form',async data=>{
  const line={MaDichVu:data.MaDichVu,DonGiaVon:Number(data.DonGiaVon),[data.LoaiPhieu==='KiemKe'?'SoLuongThucTe':'SoLuong']:Number(data.SoLuong)};
  const payload={LoaiPhieu:data.LoaiPhieu,GhiChuLyDo:data.GhiChuLyDo||null,Lines:[line]};payload.MaPhieuKho=stable('#inventory-form',payload,'K').key;
  const response=await api('/inventory-documents',payload);result('#inventory-result',response);$('#post-document-id').value=payload.MaPhieuKho;await refresh();
});
bind('#post-form',async data=>{result('#inventory-result',await api('/inventory-documents/'+encodeURIComponent(data.MaPhieuKho)+'/post',{}));await refresh();});
bind('#report-form',async data=>{const query=data.report==='stock'?'':('?'+new URLSearchParams({FromDate:data.FromDate,ToDate:data.ToDate}));result('#report-result',await api('/reports/'+data.report+query));});
const today=new Intl.DateTimeFormat('sv-SE',{timeZone:'Asia/Ho_Chi_Minh'}).format(new Date());
$('#report-form [name=FromDate]').value=today;$('#report-form [name=ToDate]').value=today;
run(async()=>{try {await signedIn((await api('/auth/me')).data);}catch(error){if(!error.message.startsWith('UNAUTHENTICATED'))throw error;}});
