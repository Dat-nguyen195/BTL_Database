# Danh mục chỉ mục – MD phối hợp BD

Các chỉ mục dưới đây là phương án đã chốt để hiện thực/đo; chưa có số liệu EXPLAIN hoặc kết quả chạy được xác nhận. Cú pháp cột sinh và UNIQUE theo schema_contract.md.

| Tên | Bảng/cột | Quy tắc / truy vấn | Mục đích |
|---|---|---|---|
| uq_phien_may_active | PHIEN_SU_DUNG(MaMayDangHoatDong) | BR-03 | Tối đa một active/máy. |
| uq_phien_nguoi_active | PHIEN_SU_DUNG(MaNguoiChoiDangHoatDong) | BR-03 | Tối đa một active/hội viên. |
| uq_vi_thu_phien | GIAO_DICH_VI(MaPhienThuThanhCong) | BR-05/08 | Một thu thành công/phiên. |
| uq_vi_thu_don | GIAO_DICH_VI(MaDonHangThuThanhCong) | BR-08 | Một thu thành công/đơn. |
| uq_vi_hoan_goc | GIAO_DICH_VI(MaGDGocHoanThanhCong) | BR-08 | Một hoàn thành công/giao dịch gốc. |
| ix_don_thoi_diem | DON_GOI_DICH_VU(ThoiDiemDat) | Q04/Q05 | Lọc thời gian đơn. |
| ix_bien_lai_thanh_toan | BIEN_LAI_TIEN_MAY(ThoiDiemThanhToan) | Q05 | Lọc tiền giờ theo thời điểm thu. |
| ix_vi_nguoi_thoi_diem | GIAO_DICH_VI(MaNguoiChoi,ThoiDiemGD) | Q03 | Lịch sử ví theo chủ/khoảng thời gian. |
| ix_ca_khoang | CA_TRUC(ThoiDiemBatDau,ThoiDiemKetThuc) | Q08 | Hỗ trợ tìm ca theo khoảng; vẫn cần điều kiện chồng giờ. |

Giữ PK/UQ/FK từ baseline, đặc biệt UQ MaYeuCau và biên lai.MaPhien. MD kiểm tra chỉ mục đã được PK/UQ/FK tạo để không tạo trùng. BD thêm bảng đo gồm Q-ID, lượng dữ liệu, EXPLAIN trước/sau, thời gian, chi phí ghi và giới hạn; không bịa số đo hoặc khẳng định chỉ mục khởi điểm luôn tối ưu.
