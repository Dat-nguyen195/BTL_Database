# Cách làm việc trên GitHub

Đọc [kế hoạch](BTL2_Database_HK261/PLAN.md), checklist cá nhân và [quy tắc phối hợp của dự án](BTL2_Database_HK261/CONTRIBUTING.md) trước khi sửa.

## Thực hiện một phần việc

1. Cập nhật nhánh main rồi tạo nhánh riêng theo mã thành viên/tác vụ, ví dụ `feature/TD-09-auth` hoặc `feature/MD-02-schema`.
2. Sửa tệp/thư mục trong checklist của mình. Với tệp dùng chung, giữ đúng hợp đồng đã chốt và phối hợp với chủ phần để tránh ghi đè.
3. Kiểm tra phần vừa làm, bổ sung cách chạy và minh chứng thực tế; viết phần báo cáo cá nhân.
4. Chỉ tick checklist khi điều kiện hoàn thành đạt. Đồng bộ trạng thái tác vụ tương ứng trong `BTL2_Database_HK261/TASKS.json`; không tự tick phần người khác.
5. Commit nêu mã tác vụ, push nhánh của mình và mở pull request vào main để người kiểm tra chéo xem trước khi hợp nhất.

Ví dụ sau khi clone, thay tên nhánh và đường dẫn theo phần của mình:

```bash
git switch main
git pull --ff-only origin main
git switch -c feature/TD-09-auth
# Thực hiện công việc và kiểm tra kết quả.
git add BTL2_Database_HK261/apps/backend BTL2_Database_HK261/docs/team/01_nguyen_thanh_dat.md
git diff --cached
git commit -m "TD-09: implement authentication and permissions"
git push -u origin feature/TD-09-auth
```

Chỉ thêm các tệp mình cần bàn giao; kiểm tra danh sách trước khi commit. Không đưa `.env`, mật khẩu, khóa bí mật, dữ liệu khách hàng thật, thư viện đã cài, cache hoặc ZIP cũ vào kho. Tệp `.env.example` chỉ là mẫu, không điền thông tin kết nối thật.

Giữ nguyên `BTL2_Database_HK261/docs/btl1_baseline/` và checksum của bản chụp. Thay đổi vật lý đã chốt nằm trong schema_contract.md/change_log.md; cập nhật các phần bị ảnh hưởng khi phát hiện vấn đề cụ thể. Không thay công nghệ hoặc hợp đồng theo từng nhánh riêng.

Chưa hoàn thành chức năng thì để TODO và nêu phần còn thiếu; README hay SQL khung không phải bằng chứng ứng dụng đã chạy.
