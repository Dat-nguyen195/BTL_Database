# Giao dịch, khóa và chống lặp – hợp đồng đã chốt

## 1. Ai commit

**TD: backend service sở hữu transaction. HT: thủ tục/hàm/trigger không START TRANSACTION, COMMIT hoặc ROLLBACK riêng.** Chạy SQL thủ công cũng phải có caller BEGIN/CALL/COMMIT và rollback khi lỗi. Trigger không làm lớp commit.

Mỗi thao tác ghi lấy một kết nối riêng, đặt `+07:00`, `autocommit=False`, bắt đầu `READ COMMITTED`. Toàn bộ xác thực DB, khóa, CALL hoặc tạo đầu/dòng nháp, kiểm tra hậu điều kiện dùng cùng kết nối. TD đọc hết các result set của CALL, rồi commit một lần; nếu lỗi ở bất kỳ bước nào thì rollback và giải phóng kết nối. Không thực hiện DDL trong transaction nghiệp vụ vì DDL có thể gây implicit commit. Kết nối đọc kết thúc transaction/đóng sau request để không giữ snapshot hoặc khóa ngoài ý muốn.

Trong SQL routine, `BEGIN ... END` là khối lệnh, vẫn được dùng; quy định trên cấm lệnh mở transaction riêng. Lỗi nghiệp vụ SIGNAL theo error_codes.md; không có EXIT HANDLER nuốt lỗi rồi trả kết quả thành công.

## 2. Thứ tự khóa

Dùng SELECT ... FOR UPDATE trên hàng tồn tại; không dùng SELECT COUNT rồi INSERT để thay khóa/UNIQUE. Nếu cần đọc trước để tìm khóa cha, chỉ coi đó là gợi ý và đọc/kiểm tra lại sau khi có khóa.

Thứ tự toàn cục cho những hàng một thao tác cần dùng:

1. NGUOI_CHOI (ví), tăng dần MaTaiKhoan nếu có nhiều ví.
2. MAY_TRAM theo MaMay.
3. PHIEN_SU_DUNG theo MaPhien.
4. DON_GOI_DICH_VU theo MaDonHang, rồi PHIEU_KHO theo MaPhieuKho, rồi BIEN_LAI_TIEN_MAY nếu cần.
5. DICH_VU theo MaDichVu tăng dần; khóa đủ các món trước khi kiểm tra/trừ tồn.
6. GIAO_DICH_VI theo khóa nghiệp vụ; UNIQUE vẫn là chốt chống trùng ở DB.

Chỉ khóa các nhóm thực sự dùng, nhưng không khóa nhóm đứng trước sau khi đã giữ nhóm đứng sau. Ràng buộc/hàm/trigger dùng cùng thứ tự; nếu trigger cần thêm khóa thì service/thủ tục lấy trước. Khóa đầu đơn/phiếu trước khi sửa dòng; tạo nháp chưa thấy bởi transaction khác nên lấy đủ khóa danh mục, tính giá và chèn đầu/dòng nguyên tử. Thuộc tính MaPhien/chủ/kênh của đầu đơn không được sửa sau khi tạo.

Mở phiên khóa ví (nếu có), máy, kiểm tra phiên rồi INSERT; UQ cột sinh chặn cả yêu cầu mở đồng thời. Tiếp nhận đơn khóa phiên nếu tại máy, đầu đơn và các món; trừ tất cả hoặc không trừ món nào. Thu đơn chỉ khóa/ghi tiền và trạng thái thu, **không trừ kho lần nữa**. Ghi sổ khóa đầu phiếu/món, kiểm tra ảnh kiểm kê và cập nhật một lần.

## 3. Chống gửi lặp không thêm bảng

| Thao tác | Khóa ổn định | Cách xử lý |
|---|---|---|
| Mở phiên | MaPhien do UI tạo và giữ khi retry | Cùng mã và cùng máy/chủ/loại/tiền trả trước → lấy lại phiên; khác các trường này → 409. Không so lại giá danh mục mới với giá đã chụp. |
| Tạo đơn nháp | MaDonHang + danh sách món/lượng + kênh/phiên | Trùng mã chỉ replay khi đầu/dòng khớp yêu cầu gốc; không chèn dòng lần hai. Giá lấy từ bản đã chụp khi replay. |
| Tạo phiếu nháp | MaPhieuKho + loại/lý do/các dòng | Cùng mã khác nội dung → 409; tạo nháp không đổi tồn. |
| Nạp ví | GIAO_DICH_VI.MaYeuCau = nap:{UUID} | UI tạo UUID một lần cho một giao dịch; giữ khi gửi lại. So sánh chủ ví/số tiền/phương thức/nhân viên; cùng khóa khác nội dung → 409. |
| Thu giờ bằng ví | gio:{MaPhien} | Một giao dịch ThanhCong/phiên; phí 0 không tạo giao dịch ví. |
| Thu dịch vụ bằng ví | dv:{MaDonHang} | Một giao dịch ThanhCong/đơn; phí 0 không tạo giao dịch ví. |
| Kết thúc/tiếp nhận/thu/ghi sổ | Mã đối tượng + hành động | Khóa đầu đối tượng; nếu hành động đã xong và trường yêu cầu lưu khớp thì đọc lại kết quả, không làm tác dụng phụ lần nữa; phương thức/số tiền khác → 409. |

MaGiaoDich của nạp do UI sinh và giữ lại; mã biên lai/giao dịch thu do backend sinh, truyền xuống routine. Khi replay đã có kết quả, routine dùng mã đã lưu, bỏ qua mã mới backend sinh. UUID/log requestId không được dùng thay khóa sự kiện thu giờ/thu đơn.

Kết quả replay có `meta.replayed=true`; đối tượng nghiệp vụ không bị tạo/thu lại. Không hứa lặp nguyên từng byte response: số dư hiện tại có thể đã thay đổi bởi giao dịch khác. Kiểm tra lại quyền trước khi đọc kết quả replay.

Deadlock 1213 hoặc lock timeout 1205: rollback **toàn bộ**, mở transaction mới và retry tối đa hai lần sau lần đầu, giữ mã đối tượng/khóa đầu vào, không chỉ chạy lại câu SQL lỗi. Không retry lỗi nghiệp vụ. Hết số lần trả 503 TX_RETRY_EXHAUSTED. Mất mạng sau commit: client gửi lại cùng mã, backend đọc kết quả đã lưu. Không dùng bộ nhớ process để bảo đảm chống lặp.

## 4. Tiền giờ và hạn dùng trả trước

Giữ BR-04/05 của BTL1: trước chi ví và quyết toán, khóa ví/phiên, tính lại phí bằng giờ server, cập nhật giữ chỗ, rồi kiểm tra số dư khả dụng. Giữ chỗ không phải bút toán trừ ví; chỉ thu một lần khi đóng.

Với giá dương và ngân sách B VND, số giây tối đa là số nguyên lớn nhất t sao cho floor(t*g/3600) <= B. Backend cấp hạn dùng theo công thức này; chi ví làm giảm ngân sách thì cập nhật hạn dùng ngay trong luồng đã khóa. Mọi lệnh dùng phiên/đặt món kiểm tra hạn trên server. Worker demo kiểm tra phiên trả trước và gọi cùng service kết thúc ở mốc hạn được cấp; không tính phí tới thời điểm worker chạy muộn. Không dùng timer trên trình duyệt làm bảo đảm ngân sách, không tùy tiện cắt phí vượt ngân sách để che lỗi dừng phiên.

Đây là quyền sử dụng phiên mô phỏng ở ứng dụng, không phải phần mềm khóa máy vật lý. Trả sau không giữ chỗ; miễn phí giá 0 chỉ được QuanLy cấp. Nếu chưa thực hiện/kiểm tra hạn dùng thì ghi BR-04 chưa hỗ trợ và không tuyên bố luồng trả trước hoàn chỉnh.

## 5. Kiểm tra bắt buộc

- Hai kết nối tranh cùng máy; một hội viên mở hai máy; hai đơn tranh món cuối; hai giao dịch chi cùng ví. Chỉ kết quả hợp lệ được commit.
- Lỗi ở dòng thứ hai của đơn/phiếu: đầu, dòng, tồn, ví và trạng thái đều rollback theo phạm vi thao tác.
- Gửi lặp cùng khóa và gửi cùng khóa khác nội dung, kể cả sau mất response; không thu/trừ tồn hai lần.
- Chi ví trong phiên qua ngày/gần hết hạn; phí 0; đồng thời nạp/chi/đóng phiên; không chi phần giữ chỗ.
- Người chơi gọi API của người khác và nhân viên sai chức vụ bị chặn; trigger không cho sửa/xóa lịch sử đã chốt.
