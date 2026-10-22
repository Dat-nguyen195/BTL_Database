# Quy tắc BTL1 cần kế thừa khi hiện thực BTL2

Trích các miền dữ liệu và quy tắc nghiệp vụ do nhóm thiết kế trong BTL1, từ nguồn báo cáo của nhóm. Đây là yêu cầu thiết kế, chưa phải xác nhận BTL2 đã thực hiện. Mô hình 23 bảng nằm trong model.json và sơ đồ nguồn BTL1_EER.drawio.

## Miền dữ liệu D-01 đến D-09

| Mã / nội dung | Quy tắc |
|---|---|
| D-01: số và mã | PK NOT NULL; mã duy nhất. Giá, số dư, lương, tổng tiền >= 0. Số lượng bán, thứ tự dòng/địa chỉ > 0; tồn >= 0. Chênh lệch kiểm kê có dấu. |
| D-02: thời gian | Phiên kết thúc >= bắt đầu; ca kết thúc > bắt đầu. Phiên đang hoạt động có kết thúc NULL; đã kết thúc có kết thúc khác NULL. DaHuy chỉ dành phiên mở lỗi chưa sử dụng, phí và giữ chỗ 0; phiên đã sử dụng phải kết thúc và có biên lai. Mốc thanh toán/hoàn/ghi sổ phải phù hợp trạng thái và không trước mốc tạo. |
| D-03: kiểu phiên | HinhThucDangNhap thuộc TraTruoc/TraSau/MienPhi. MienPhi có giá, phí, tiền nạp, giữ chỗ đều 0. TienNapTruoc chỉ dùng vãng lai trả trước; nếu giá dương thì > 0. Các loại khác có tiền nạp 0. |
| D-04: kênh đơn | TaiMay => MaPhien NOT NULL; TaiQuay => MaPhien NULL và không TruVi. MoiDat chưa cần nhân viên; DaTiepNhan/DangCheBien/DaGiao phải có. DaHuy trước tiếp nhận được NULL, hủy sau tiếp nhận giữ nhân viên. DaHuy phải có ThoiDiemHuy và TrangThaiTruocHuy thuộc MoiDat/DaTiepNhan/DangCheBien; ngoài DaHuy hai cột này NULL. |
| D-05: thu và hoàn đơn | ChuaThanhToan: chưa có mốc thu, chưa có hoàn. DaThanhToan: có hình thức/mốc thu, tiền hoàn 0. DaHoanTien: giữ mốc thu gốc, có mốc hoàn và SoTienDaHoan=TongTien; chỉ hoàn khi đơn hủy. Không nhận hoàn một phần trong phạm vi này. |
| D-06: biên lai | Một MaPhien duy nhất. Đã thu tiền mặt/chuyển khoản: TienNhan - TienHoan = TongTienGio. TruVi có TienNhan=TienHoan=0. MienPhi có tất cả khoản bằng 0. Công nợ chưa thu không ghi mốc thanh toán; tiền nhận/hoàn 0 cho tới khi thu đủ. |
| D-07: giao dịch ví | SoTien > 0; MaYeuCau duy nhất. NapTien: đơn/phiên/gốc NULL, hình thức tiền mặt/chuyển khoản, có nhân viên. TruTienMay: chỉ MaPhien; TruTienDichVu: chỉ MaDonHang; HoanTien: MaDonHang và MaGDGoc, không MaPhien; ba loại nội bộ dùng NoiBo. |
| D-08: phiếu kho | NhapKho: lượng >0, delta=+lượng. XuatHuy: lượng >0, delta=-lượng. KiemKe: lượng=0, sổ sách/thực tế >=0, delta=thực tế-sổ sách. TaiPhanLoai: lượng>0, delta=0, có MaDonHang. Các loại không kiểm kê có sổ sách/thực tế NULL; loại khác tái phân loại có MaDonHang NULL. |
| D-09: chuỗi trạng thái | Tài khoản HoatDong/Khoa/TamDung; máy AVAILABLE/ONLINE/MAINTENANCE/DISCONNECTED; mặt hàng DangBan/NgungBan. CHECK miền theo từ điển, không dùng chuỗi tùy ý. |

## Quy tắc nghiệp vụ BR-01 đến BR-16

| Mã / nội dung | Quy tắc |
|---|---|
| BR-01 — Toàn phần/chồng lấp | Tạo cha và ít nhất một con trong một giao dịch; cấm xóa lớp con cuối cùng khi cha còn tồn tại. Cho phép cả hai. CHECK/FK đơn lẻ không bảo đảm toàn phần; cần thủ tục có quyền ghi giới hạn và kiểm tra trước commit. |
| BR-02 — Quản lý đệ quy | MaNguoiQuanLy là nhân viên, khác chính mình và không dẫn tới chu trình. Khi đổi quản lý phải duyệt chuỗi tổ tiên dưới kiểm soát cập nhật đồng thời. |
| BR-03 — Chiếm máy/phiên | Tối đa một DangHoatDong mỗi MaMay và mỗi MaNguoiChoi khác NULL. Máy ONLINE tương ứng phiên hoạt động; mở/đóng và chuyển trạng thái nguyên tử, máy bảo trì không mở phiên. |
| BR-04 — Dừng và giữ chỗ | Máy chủ cấp thời hạn sử dụng theo ngân sách; khóa ví rồi phiên, cập nhật phí phát sinh trước khi chi; tổng giữ chỗ <= số dư. Sau chi phải rút ngắn hạn dùng. Giao dịch không thể cam kết nếu phí đã vượt ngân sách; thiết bị phải dừng ở hạn được cấp. |
| BR-05 — Quyết toán | Kết thúc phiên và lập biên lai trong một giao dịch. Phí biên lai bằng phí chốt phiên; trả trước vãng lai quyết toán từ tiền nhận, hoàn phần dư. Hội viên trừ ví chỉ một giao dịch thành công mỗi phiên. Mọi phiên kết thúc có biên lai, kể cả phí 0; không tạo giao dịch ví khi phí bằng 0. |
| BR-06 — Chụp giá và tổng | Giá phiên/món lấy từ máy chủ tại mốc tạo. TongTien đơn bằng tổng dòng; đổi danh mục không sửa giá chụp. Cấm sửa dòng đã tiếp nhận và biên lai đã thu; hoàn không xóa hoặc sửa giá gốc. |
| BR-07 — Đơn và chủ ví | Đặt TaiMay chỉ trên phiên đang hoạt động; máy và chủ ví suy từ MaPhien. TruVi chỉ khi phiên có người chơi; giao dịch có cùng MaNguoiChoi của phiên. Thu đúng TongTien, không thu trùng cả tiền mặt và ví. |
| BR-08 — Chống lặp và hoàn | MaYeuCau gắn sự kiện nghiệp vụ (vd dv:MaDonHang), giữ ổn định khi retry. Cùng khóa khác nội dung bị từ chối. Một thu dịch vụ thành công/đơn, một thu giờ/phiên, một hoàn/giao dịch gốc. Giao dịch hoàn phải trỏ thu dịch vụ thành công, cùng đơn, chủ và số tiền; không hoàn từ một hoàn. |
| BR-09 — Vòng đời đơn | MoiDat -> DaTiepNhan -> DangCheBien -> DaGiao; hàng đóng gói cho phép DaTiepNhan -> DaGiao. Hủy từ trạng thái chưa giao, theo quyền; chụp trạng thái trước hủy và mốc hủy trong cùng giao dịch. Đơn đã giao cần quy trình trả hàng riêng ngoài phạm vi; không quay ngược trạng thái để sửa lịch sử. |
| BR-10 — Kho một lần | Chuyển sang DaTiepNhan trừ tất cả dòng một lần, có khóa và kiểm tra tồn. Thanh toán không trừ lần nữa. Hủy trước chế biến bù lượng xuất một lần; sau chế biến không bù và không trừ lần hai. Chỉ cho hủy một lần từ trạng thái hợp lệ. |
| BR-11 — Tái phân loại | Phiếu chỉ cho đơn DaHuy có TrangThaiTruocHuy=DangCheBien; mỗi món phải thuộc đơn, lượng tái phân loại không vượt lượng đã xuất chưa hoàn kho. Tối đa một phiếu TaiPhanLoai cho mỗi đơn. Phiếu delta 0 không tham gia tính tăng/giảm tồn. |
| BR-12 — Ghi sổ kho | Nháp phải có dòng; mọi dòng đúng loại phiếu. Khóa mặt hàng theo thứ tự mã; xác nhận ảnh kiểm kê khớp tồn hiện tại, tính delta, kiểm tra không âm, cập nhật tồn và trạng thái phiếu cùng giao dịch. Không cho ghi sổ lặp; trạng thái DaGhiSo bất biến. |
| BR-13 — Bảo toàn lịch sử | Chặn DELETE và UPDATE nghiệp vụ của đơn đã tiếp nhận/thu/hoàn, biên lai đã thu, phiếu đã ghi sổ và giao dịch đã kết thúc; chặn sửa/xóa/chèn dòng sau chốt. Chỉ thay trạng thái qua chuyển hợp lệ hoặc lập chứng từ bù. FK không thay được các điều kiện này. |
| BR-14 — Lịch trực | CA_TRUC là lần trực có ngày giờ; a và b chồng nếu a.start < b.end và b.start < a.end. Cho phép hai khoảng tiếp giáp, kể cả 22h-06h rồi 06h-14h. Cùng nhân viên cùng MaCa nhiều khu được phép; khác MaCa chồng giờ bị cấm. Không sửa/xóa ca đã có phân công lịch sử. |
| BR-15 — Đối soát | Tồn đầu + nhập - xuất hủy + chênh kiểm kê - lượng đơn đã xuất + hàng được trả trước chế biến = tồn cuối. Tái phân loại delta 0. Số dư cuối = đầu + nạp + hoàn - thu giờ - thu dịch vụ; giữ chỗ giảm khả dụng, không phải chi đã ghi sổ. |
| BR-16 — Doanh thu | Doanh thu đã thu = tiền giờ biên lai DaThanhToan + đơn đã thanh toán - hoàn. Không cộng thêm giao dịch ví tương ứng và không cộng tiền nạp ví. Biên lai công nợ, đơn hủy chưa thu và giữ chỗ không là doanh thu đã thu. |

## Công thức tiền giờ và ngân sách

- F(t,g) = floor(t*g/3600), tiền VND nguyên; t là số giây theo DATETIME đầy đủ ngày. Ví dụ 59 giây ở giá 10000 VND/giờ cho phí 163 VND; 5400 giây cho phí 15000 VND.
- Giá ưu tiên BANG_GIA theo nhóm người dùng/nhóm máy; thiếu cặp dùng NHOM_MAY.DonGiaGioMacDinh. Vãng lai dùng nhóm VangLai. Giá 0 không chia để tính hạn và không phát sinh phí.
- Số dư khả dụng = số dư ví - tổng giữ chỗ tiền giờ của các phiên đang hoạt động. Trước chi ví/quyết toán tính lại dưới khóa theo giờ server; giữ chỗ không phải bút toán trừ ví.
- Với trả trước giá dương, hạn dùng là số giây nguyên lớn nhất thỏa phí không vượt ngân sách. Sau chi dịch vụ cập nhật hạn dùng; không dùng bộ đếm chậm để cho phép phát sinh nợ. Trả sau không giữ chỗ, công nợ chưa thu không là doanh thu.
