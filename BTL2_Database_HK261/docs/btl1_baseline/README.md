# Mốc kế thừa BTL1 – bản dùng trong kho công khai

BTL2 tiếp nối mô hình và nghiệp vụ BTL1 của nhóm Quản lý quán Net. Bộ dưới cung cấp nội dung cần để triển khai và đối chiếu; chưa phải bằng chứng CSDL/ứng dụng BTL2 đã chạy.

- [model.json](model.json): mô hình 23 bảng, cột/kiểu/PK/FK/UQ/NULL và quy tắc, giữ nguyên bản chụp từ BTL1.
- [BTL1_EER.drawio](BTL1_EER.drawio): nguồn sơ đồ chỉnh sửa được, giữ nguyên bản chụp từ BTL1.
- [business_rules.md](business_rules.md): đầy đủ D-01–D-09, BR-01–BR-16 và công thức tiền giờ để HT/MD/TD/BD/TT hiện thực.
- [SHA256SUMS](SHA256SUMS): checksum của các tệp trong bộ thiết kế công khai này.

Bản công khai không kèm PDF báo cáo BTL1 hoặc PDF đề bài gốc. Thành viên đọc yêu cầu môn học tại [thư mục lớp trên Drive](https://drive.google.com/drive/u/9/folders/1v_9W2CMeLXQi4SlCZRHUT_k7J5sAouoQ) và [bản tổng hợp yêu cầu](../requirements/requirements.md). Bộ ảnh/sơ đồ báo cáo BTL1 của nhóm có tại [thư mục tư liệu trên Drive](https://drive.google.com/drive/folders/1BfTV1t4VnWgrrj1HocAwoIMVtgA-kJsw).

Giữ nguyên bộ thiết kế này khi hiện thực; ghi khác biệt trong docs/design/change_log.md và migration tương ứng. Toàn phần/chồng lấp, ngân sách/giữ chỗ, lịch sử bất biến, chống lặp và các quy tắc chưa hỗ trợ phải được đối chiếu rõ trong ma trận BTL2.
