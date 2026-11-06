# Minh chứng thực thi

| Vị trí | Nội dung |
|---|---|
| `dbms/manifest.json` | 28 lượt SQL trên MySQL 8.4.13; ánh xạ SQL, JSON, ảnh PNG và PDF vector |
| `report_assets/` | Ảnh SQL client thực thi trực tiếp; bản PDF tương ứng ở `docs/report/latex/assets/dbms/` |
| `queries/index_benchmark.json` | Dữ liệu, số đo và EXPLAIN ANALYZE trước/sau chỉ mục |
| `app/` | Request/response đã bỏ bí mật, JSON và ảnh ba luồng Chrome |
| `final_verification/summary.json` | Tổng hợp kết quả bộ kiểm thử hiện tại |
| `final_verification/all.xml` | JUnit của toàn bộ lượt kiểm thử sau khi dọn cấu trúc |
| `final_verification/latex_qa.json` | Kiểm tra 64 trang, phông, vector và biên dịch nguồn LaTeX độc lập |
| `final_verification/zip_smoke.json` | Cài mới và chạy ứng dụng từ gói bàn giao giải nén |

Các test tạo database/user tạm, chạy MySQL thật rồi dọn đúng tài nguyên của test. Retry/commit mất kết nối có fault injection được ghi rõ trong mã test; các ca khóa, rollback, tranh chấp và lỗi MySQL còn được kiểm tra thật. Hướng dẫn tái hiện: `tests/README.md` và `docs/demo/runbook.md`.

Bản PDF và hồ sơ LaTeX đã được kiểm tra trực quan toàn bộ 64 trang. Bản EER tổng thể là hình tổng quan; sáu phân hệ và nguồn SVG/PDF cho phép đọc/phóng chi tiết. Kết quả kiểm thử chỉ áp dụng cho các ca được triển khai, không khẳng định bao phủ mọi trạng thái có thể có.
