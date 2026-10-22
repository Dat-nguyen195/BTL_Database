# SQL BTL2

Các tệp SQL hiện là khung có nhãn CHƯA HIỆN THỰC, không phải bộ cài đã hoàn chỉnh.

Môi trường đã chốt: MySQL 8.4.13/InnoDB, schema_contract.md. Backend giữ transaction, routine không tự commit.

Thứ tự cài đặt để hiện thực và kiểm tra: 00_bootstrap → 01_schema → 02_constraints → 03_indexes → 04_seed → 07_functions → 06_procedures → 08_triggers → kiểm tra → 05_queries. HT/MD kiểm tra phụ thuộc thực tế trước khi xác nhận lệnh cài chính thức. FK có thể bổ sung sau khi tạo đủ bảng để tránh vấn đề thứ tự/cycle.

Mỗi tệp ghi chủ phần, DBMS/phiên bản đã thử, phụ thuộc và lệnh tái hiện. Không dùng dữ liệu seed sai để làm cho các kiểm tra trông như thành công. Mọi thay đổi sau mốc đã chốt có migration và change log.
