# Ba kịch bản demo – TT phối hợp cả nhóm

## D1 – Phiên chơi

Máy AVAILABLE → mở phiên hợp lệ → mở lại bị từ chối → tính phí (có ca qua ngày/giá 0 trong kiểm tra) → kết thúc → đúng một biên lai/giao dịch thu → máy rảnh. Đối chiếu PHIEN_SU_DUNG, BIEN_LAI_TIEN_MAY và GIAO_DICH_VI.

## D2 – Ví và đơn dịch vụ

Nạp ví có MaYeuCau → gửi lặp không cộng hai lần → đặt món → tiếp nhận và trừ kho một lần → thu đơn đúng chủ ví → đối chiếu số dư/tồn. Có ca thiếu tiền hoặc thiếu tồn, chứng minh rollback.

## D3 – Kho và báo cáo

Lập phiếu/dòng → ghi sổ → gửi lại không tăng tồn lần nữa → xem đối soát kho và doanh thu → nạp ví không bị đếm như doanh thu tiêu dùng. Kiểm tra lịch ca/ca qua đêm trong Q08.

Chủ phần điền dữ liệu mẫu cụ thể, API, SQL trước/sau, thời lượng và bằng chứng. Không trình diễn hủy/hoàn nếu chưa hiện thực đủ quy tắc BTL1.
