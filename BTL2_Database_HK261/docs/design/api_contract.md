# Hợp đồng API v1 – đã chốt để TD/TT triển khai

Backend Flask, cùng origin với frontend. Base URL `http://127.0.0.1:5000/api/v1`. Hợp đồng đã chốt; các endpoint dưới đây chưa được hiện thực/chạy.

## 1. Quy ước

- JSON UTF-8; trường nghiệp vụ giữ đúng tên cột BTL1. Trường dẫn xuất dùng tên rõ như SoDuKhaDung, CanUseUntil và không ghi ngược vào cột nghiệp vụ.
- Tiền/lượng là JSON integer trong miền DECIMAL/INT tương ứng; không chuỗi tiền định dạng hoặc số lẻ. Thời gian trả ISO 8601 `+07:00`; bộ lọc ngày chấp nhận YYYY-MM-DD, khoảng ngày từ đầu ngày bắt đầu đến trước đầu ngày sau ngày kết thúc.
- ID tối đa theo schema; MaPhien/MaDonHang/MaPhieuKho/MaGiaoDich mới dùng tiền tố P/O/K/G + 19 ký tự hex ngẫu nhiên, do crypto của UI sinh và giữ khi retry. Seed có thể giữ mã ngắn BTL1. Mã URL là chuỗi, không giả định số tự tăng.
- Thành công: `{"ok":true,"data":{},"meta":{"replayed":false},"requestId":"<UUID log>"}`. Danh sách thêm meta.page/pageSize/total, page>=1, pageSize mặc định 20, tối đa 100; sort chỉ cho trường whitelist theo endpoint, mặc định mã đối tượng tăng dần (lịch sử dùng thời điểm rồi mã).
- Lỗi theo [error_codes.md](error_codes.md). Tạo đối tượng mới trả 201; tạo lại hợp lệ trả 200 với replayed=true; hành động và GET trả 200. Không trả thành công trước COMMIT.
- Client không gửi giá, tổng tiền, số dư, người thực hiện hoặc giờ giao dịch. Backend lấy từ DB/phiên đăng nhập/đồng hồ server; từ chối trường ghi ngoài whitelist.

## 2. Đăng nhập và quyền

| API | Đầu vào | Đầu ra / quyền |
|---|---|---|
| GET /auth/csrf | Không | Tạo/lấy CSRF token cho session, data.CsrfToken; dùng trước login. |
| POST /auth/login | TenDangNhap, MatKhau | Kiểm tra MatKhauBam bằng Werkzeug, HoatDong; đổi session và CSRF token, trả MaTaiKhoan/roles/CsrfToken, không trả hash. |
| GET /auth/me | Không | Danh tính và quyền hiện tại; chưa đăng nhập → 401. |
| POST /auth/logout | Không | Xóa session; yêu cầu CSRF. |

Cookie session HttpOnly/SameSite=Lax; SECRET_KEY từ môi trường, Secure khi HTTPS. Mọi POST/PATCH/DELETE (kể cả login) gửi `X-CSRF-Token`; frontend lấy từ /auth/csrf và nhận token mới sau login. Backend kiểm tra tài khoản/quyền hiện tại trong DB, không tin vai trò hoặc MaNhanVien do body gửi. Tài khoản đồng thời là người chơi và nhân viên có tổng quyền hợp lệ; mọi API người chơi vẫn phải đối chiếu chủ tài nguyên. NHOM_NGUOI_DUNG không là quyền.

## 3. API đọc

| API | Bộ lọc/đầu vào | SQL / quyền / data |
|---|---|---|
| GET /workstations | MaKhuVuc, MaNhomMay, TrangThaiMay | Q01; tài khoản đăng nhập; danh sách mã/tên/trạng thái/nhóm/khu. |
| GET /sessions | TrangThaiPhien, MaMay | Q02; người chơi chỉ phiên của mình, ThuNgan/QuanLy xem tất cả; phí hiện tại/CanUseUntil do server tính. |
| GET /sessions/:MaPhien | Mã phiên | Chi tiết cùng quyền như /sessions; không đủ quyền → 403. |
| GET /services | MaNhomDV, TrangThaiKinhDoanh | Danh mục DICH_VU, nhân viên và người chơi đăng nhập; tên/giá hiện hành/khả dụng để tạo nháp. |
| GET /wallets/:MaNguoiChoi | Mã chủ ví | Q03; chủ ví hoặc ThuNgan/QuanLy; SoDuVi, TienGiuCho, SoDuKhaDung tại ThoiDiemTinh, tính phí hiện tại, không dùng cache cũ để quyết định chi. |
| GET /wallets/:MaNguoiChoi/transactions | FromDate, ToDate | Q03; cùng quyền ví; lịch sử, lọc thời gian/phân trang. |
| GET /orders | TrangThaiPhucVu, TrangThaiThanhToan, FromDate, ToDate | Q04; người chơi chỉ đơn TaiMay của mình; ThuNgan/PhaChe/QuanLy xem đơn nghiệp vụ. |
| GET /orders/:MaDonHang | Mã đơn | Đầu và Lines, giá chụp/tổng; quyền như danh sách. |
| GET /inventory-documents | LoaiPhieu, TrangThaiPhieu | ThuNgan/QuanLy; danh sách phiếu. |
| GET /inventory-documents/:MaPhieuKho | Mã phiếu | ThuNgan/QuanLy; đầu phiếu và Lines. |
| GET /reports/revenue | FromDate, ToDate | Q05; QuanLy; doanh thu đã thu, không cộng nạp ví. |
| GET /reports/stock | Threshold (integer>=0) | Q06; ThuNgan/QuanLy; tồn và hàng dưới ngưỡng. |
| GET /reports/inventory-reconciliation | FromDate, ToDate | Q07; QuanLy; đối soát biến động. |
| GET /reports/shifts | FromDate, ToDate, MaNhanVien | Q08; QuanLy; lịch và chồng giờ. |

FromDate/ToDate là cặp tham số: nếu có phải đủ cả hai và FromDate <= ToDate. Bắt buộc cặp này cho Q05/Q07/Q08; lịch sử ví/đơn có thể bỏ cả cặp để xem danh sách phân trang. Các route tĩnh như /reports/... không nhận tên bảng hoặc SQL từ client. BD cung cấp SQL có tham số; TD thêm giới hạn quyền ở server, không chỉ lọc trên UI.

## 4. API ghi

| API | Body được phép | Thực thi / quyền |
|---|---|---|
| POST /sessions | MaPhien, MaMay, MaNguoiChoi (nullable), HinhThucDangNhap, TienNapTruoc | sp_mo_phien. Người chơi mở TraTruoc của mình; ThuNgan/QuanLy mở cho khách; MienPhi chỉ QuanLy. TienNapTruoc=0 trừ vãng lai trả trước. |
| POST /sessions/:MaPhien/close | HinhThucThanhToan, TienNhan | sp_ket_thuc_phien. Chủ phiên chỉ tự trả TruVi; ThuNgan/QuanLy chốt các hình thức khác; miễn phí theo phiên được cấp. Backend sinh mã B/G; ChuaThu chỉ trả sau. |
| POST /wallet/topups | MaGiaoDich, MaYeuCau, MaNguoiChoi, SoTien, PhuongThucGD | sp_nap_vi. ThuNgan/QuanLy; MaYeuCau dạng nap:{UUID}, số tiền >0. |
| POST /orders | MaDonHang, KenhDat, MaPhien (nullable), Lines:[{MaDichVu,SoLuong}] | Service SQL có tham số: đầu MoiDat/ChuaThanhToan + đủ dòng, chụp giá, tổng tính server trong một transaction; chưa trừ kho/tiền. Người chơi TaiMay phiên mình; ThuNgan/QuanLy tạo TaiMay/TaiQuay. |
| POST /orders/:MaDonHang/accept | {} | sp_tiep_nhan_don. ThuNgan/PhaChe/QuanLy; gán nhân viên, trừ tồn một lần. |
| POST /orders/:MaDonHang/pay | HinhThucThanhToan | sp_thanh_toan_don. Chủ phiên chỉ TruVi; ThuNgan/QuanLy TienMat/ChuyenKhoan hoặc thu ví đúng chủ. |
| POST /inventory-documents | MaPhieuKho, LoaiPhieu, GhiChuLyDo, Lines | Service SQL có tham số tạo đầu Nhap + dòng; ThuNgan/QuanLy. NhapKho/XuatHuy: dòng {MaDichVu,SoLuong,DonGiaVon}; KiemKe: dòng {MaDichVu,SoLuongThucTe,DonGiaVon}; server chụp SoLuongSoSach, đặt SoLuong=0 và tính delta. |
| POST /inventory-documents/:MaPhieuKho/post | {} | sp_ghi_so_phieu_kho. Chỉ QuanLy; kiểm tra ảnh sổ sách còn khớp và tồn không âm; ghi sổ một lần. |

Lines phải có ít nhất một dòng, MaDichVu không lặp trong đơn/phiếu (UI gộp lượng trước khi gửi); STTDong phiếu do server gán từ 1. Ghi chú tối đa 255 ký tự. Giá bán chụp từ DICH_VU.GiaBanHienHanh; DonGiaVon là đầu vào nghiệp vụ kho >=0. Từ chối số lượng âm/0 ngoài SoLuong=0 của kiểm kê do server gán.

Không mở API sửa/xóa đơn đã tạo trong demo; để thay nội dung nháp tạo yêu cầu mới với mã mới, không dùng lại mã cũ khác nội dung. Không có route chuyển DangCheBien/DaGiao/hủy/hoàn hay CRUD danh mục/tài khoản/ca; seed có thể chứa lịch sử hợp lệ để báo cáo. Không tuyên bố toàn bộ UC đã có UI ghi. Ba luồng chính dùng MoiDat → DaTiepNhan → thu tiền, kết thúc phiên và ghi sổ kho.

## 5. Ví dụ dùng chung cho TD/TT

Tạo đơn (UUID/mã chỉ là ví dụ cấu trúc; demo dùng mã hợp lệ đang có trong seed):

```json
{"MaDonHang":"O0123456789ABCDEF0123","KenhDat":"TaiMay","MaPhien":"P0123456789ABCDEF0123","Lines":[{"MaDichVu":"DV01","SoLuong":2}]}
```

Giá/tổng/phân quyền đều do server kiểm tra. Response sau commit:

```json
{"ok":true,"data":{"MaDonHang":"O0123456789ABCDEF0123","TrangThaiPhucVu":"MoiDat","TrangThaiThanhToan":"ChuaThanhToan","TongTien":30000,"Lines":[{"MaDichVu":"DV01","SoLuong":2,"DonGiaBan":15000,"ThanhTien":30000}]},"meta":{"replayed":false},"requestId":"e5b0dab3-2ac0-498b-9450-5e7baaeb8eb1"}
```

Chỉ ví dụ đặc tả, không phải bằng chứng API đã chạy. Các trường server bổ sung như thời điểm/giữ chỗ/CanUseUntil phải có trong ca kiểm tra khi endpoint tương ứng được hiện thực. Cùng mã và cùng nội dung gửi lại: 200/replayed=true; cùng mã khác dòng/lượng: 409 IDEMPOTENCY_CONFLICT. Luồng transaction và cách so sánh replay ở [transactions.md](transactions.md).
