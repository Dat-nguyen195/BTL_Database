# Kế hoạch và phân công BTL2 – L09, Nhóm 10

**Đề tài:** Quản lý quán Net. **BTL2 tiếp nối trực tiếp BTL1**, sử dụng mô hình 23 bảng, UC và các quy tắc nghiệp vụ đã thiết kế.

**Ngày bắt đầu: 23/10/2026. Hạn nội bộ kết thúc: thứ Ba 03/11/2026.**

Cả nhóm chủ động sắp xếp công việc trong khoảng này theo phụ thuộc kỹ thuật; tất cả sản phẩm được bàn giao theo hạn chung. Ngày kết thúc là hạn nội bộ của nhóm; lịch nộp chính thức tuần 47/49 phải đối chiếu LMS theo [yêu cầu gốc](docs/requirements/requirements.md).

## Quyết định áp dụng ngay

| Phần | Lựa chọn đã chốt |
|---|---|
| CSDL và lược đồ | MySQL Community Server 8.4.13, InnoDB; giữ 23 bảng/cột nghiệp vụ BTL1, bổ sung cột sinh/UNIQUE theo hợp đồng. |
| Backend | Python 3.12 + Flask 3.1.3 + mysql-connector-python 26.7.0; SQL tham số/CALL, không ORM. |
| Frontend | HTML/CSS/JavaScript modules; Flask phục vụ cùng origin cổng 5000, không cần Node/build. |
| API và quyền | /api/v1 JSON; session cookie + CSRF; quyền theo hồ sơ/ChucVu/chủ tài nguyên, không theo nhóm giá. |
| Thủ tục và lỗi | Sáu thủ tục chính, hai hàm, ba nhóm trigger; chữ ký và mã SIGNAL/HTTP đã ghi trong tài liệu. |
| Giao dịch | Backend service BEGIN/COMMIT/ROLLBACK trên một kết nối; routine chỉ kiểm tra/cập nhật trong giao dịch đó; READ COMMITTED, khóa và chống lặp thống nhất. |

Chi tiết và lý do ở [decisions.md](docs/design/decisions.md). Các thành viên triển khai và kiểm tra theo quyết định này; không phải họp để chọn lại. Phần mã/SQL vẫn là công việc cần làm.

## 1. Kết quả và phạm vi cần hoàn thành

- CSDL thật cài được từ đầu, nhất quán với 23 bảng BTL1; có dữ liệu mẫu, ràng buộc, chỉ mục và đặc tả truy vấn.
- Thủ tục, hàm và trigger thực hiện nghiệp vụ BTL1, có ca kiểm tra và kết quả thực chạy.
- Ứng dụng kết nối DB thật, có kiến trúc, hướng dẫn cài/chạy và demo thay đổi dữ liệu.
- Báo cáo PDF, SQL/mã nguồn, cấu hình mẫu, nguồn sơ đồ, hướng dẫn, minh chứng và ZIP bàn giao; mỗi người tự viết và giải thích phần mình.

Ba luồng demo của nhóm:

1. **Phiên chơi:** chọn máy → mở phiên → tính giờ → kết thúc → biên lai và giải phóng máy.
2. **Ví và dịch vụ:** nạp ví → đặt/tiếp nhận món → thanh toán; xử lý thiếu tiền/tồn và yêu cầu gửi lặp.
3. **Kho và báo cáo:** ghi sổ phiếu kho → đối chiếu tồn → xem doanh thu và lịch ca.

Mục tiêu do nhóm chọn: **23 bảng, 8 truy vấn, 6 thủ tục, 2 hàm, 3 nhóm trigger**; đây không phải số lượng tối thiểu giảng viên quy định. Một nhóm trigger có thể gồm nhiều trigger. Quy tắc ngoài ba luồng vẫn phải được đối chiếu trong ma trận BTL1; ghi rõ phần chưa hỗ trợ. Luồng hủy/hoàn chỉ đưa vào demo sau khi kiểm tra đủ quy tắc liên quan.

Đề chia BTL2 thành ba nhóm điểm: bảng/dữ liệu/SQL, thủ tục/hàm/trigger, ứng dụng (mỗi nhóm 5% học phần). Chi tiết rubric và nguồn nằm trong [requirements.md](docs/requirements/requirements.md).

## 2. Thành viên và trách nhiệm

| Mã | Thành viên | Phụ trách chính | Kiểm tra chéo | Checklist |
|---|---|---|---|---|
| TD | Nguyễn Thành Đạt | Backend/API và tích hợp nghiệp vụ | Nguyễn Hữu Tây | [12 tác vụ](docs/team/01_nguyen_thanh_dat.md) |
| MD | Nguyễn Minh Đạt | Lược đồ vật lý, ràng buộc và chỉ mục | Nguyễn Phúc Bảo Đạt | [12 tác vụ](docs/team/02_nguyen_minh_dat.md) |
| BD | Nguyễn Phúc Bảo Đạt | Dữ liệu mẫu, truy vấn và kết quả đối chiếu | Nguyễn Minh Đạt | [12 tác vụ](docs/team/03_nguyen_phuc_bao_dat.md) |
| HT | Nguyễn Hữu Tây | Thủ tục, hàm, trigger và giao dịch | Nguyễn Thành Đạt | [12 tác vụ](docs/team/04_nguyen_huu_tay.md) |
| TT | Trần Tiến Thành | Giao diện, báo cáo tổng hợp và điều phối demo | Nguyễn Thành Đạt | [12 tác vụ](docs/team/05_tran_tien_thanh.md) |

Mỗi người tự làm phần kỹ thuật, viết phần báo cáo và lưu minh chứng của mình. TT hợp nhất báo cáo và điều phối demo. Mã TD/MD/BD/HT/TT trong cây thư mục dưới đây chỉ người chủ trì; tệp dùng chung cần trao đổi trước khi sửa.

## 3. Cấu trúc thư mục và nơi làm việc

Mọi đường dẫn tính từ `BTL2_Database_HK261/`. Các thư mục hiện có README hướng dẫn; mã triển khai, tệp khai báo thư viện và minh chứng được người phụ trách bổ sung trong đúng thư mục.

```text
BTL2_Database_HK261/
├── PLAN.md, TASKS.json, CONTRIBUTING.md             # Cả nhóm: kế hoạch và theo dõi
├── README.md, SCAFFOLD_STATUS.md                    # TT: hướng dẫn/trạng thái chung
├── .env.example, .gitignore                        # MD + TD + TT: cấu hình mẫu
├── docs/
│   ├── requirements/                              # TT: đối chiếu yêu cầu, giữ đề gốc
│   │   └── requirements.md, sources.md
│   ├── btl1_baseline/                             # Cả nhóm đọc; MD giữ nguyên bản chụp
│   │   └── README.md, model.json, business_rules.md, BTL1_EER.drawio, SHA256SUMS
│   ├── design/
│   │   ├── btl1_to_btl2.md, change_log.md, decisions.md  # MD: thực hiện theo hợp đồng đã chốt
│   │   ├── index_catalog.md                       # MD chủ trì, BD bổ sung EXPLAIN
│   │   ├── query_catalog.md, seed_scenarios.md     # BD
│   │   ├── routines_catalog.md, rules_matrix.md   # HT; TD/MD đối chiếu
│   │   ├── schema_contract.md                     # MD: chuẩn lược đồ đã chốt
│   │   ├── error_codes.md                         # TD + HT; TT dùng mã lỗi
│   │   ├── transactions.md                        # TD + HT: giao dịch/chống lặp
│   │   ├── api_contract.md                        # TD; HT/TT đối chiếu
│   │   ├── ui_scope.md                            # TT; TD đối chiếu
│   │   └── architecture.md                        # TD + TT
│   ├── team/                                     # Mỗi người cập nhật checklist của mình
│   │   ├── 01_nguyen_thanh_dat.md                  # TD
│   │   ├── 02_nguyen_minh_dat.md                   # MD
│   │   ├── 03_nguyen_phuc_bao_dat.md               # BD
│   │   ├── 04_nguyen_huu_tay.md                    # HT
│   │   └── 05_tran_tien_thanh.md                   # TT
│   ├── report/
│   │   ├── outline.md                             # TT tổng hợp
│   │   └── sections/
│   │       ├── 01_schema.md                       # MD
│   │       ├── 02_data_queries.md                 # BD
│   │       ├── 03_backend.md                      # TD
│   │       ├── 04_routines.md                     # HT
│   │       └── 05_frontend_integration.md         # TT
│   └── demo/                                     # TT chủ trì, cả nhóm đóng góp
│       └── scenarios.md, runbook.md, questions.md
├── database/
│   ├── README.md                                 # MD: thứ tự cài/chạy SQL
│   ├── 00_bootstrap/00_create_database.sql        # MD
│   ├── 01_schema/                                # MD: 23 bảng trong năm tệp
│   │   ├── 01_identity.sql, 02_workstations.sql
│   │   └── 03_services.sql, 04_inventory.sql, 05_staff_wallet.sql
│   ├── 02_constraints/01_constraints.sql          # MD
│   ├── 03_indexes/01_indexes.sql                  # MD; BD phối hợp kiểm tra
│   ├── 04_seed/                                  # BD
│   │   └── 01_reference_data.sql, 02_demo_scenarios.sql
│   ├── 05_queries/                               # BD
│   │   └── 01_operations.sql, 02_reports.sql
│   ├── 06_procedures/                            # HT
│   │   └── 01_sessions.sql, 02_wallet_orders.sql, 03_inventory.sql
│   ├── 07_functions/01_billing.sql                # HT
│   ├── 08_triggers/                               # HT
│   │   └── 01_history.sql, 02_state_identity.sql
│   └── migrations/                               # MD: bổ sung khi thay đổi lược đồ
├── apps/
│   ├── backend/                                  # TD: README, mã và tệp thư viện
│   │   └── src/{routes,services,repositories}/
│   └── frontend/                                 # TT: README, mã và tệp thư viện
│       └── src/{pages,components,services}/
├── tests/
│   ├── sql/schema/                               # MD
│   ├── sql/queries/                              # BD
│   ├── sql/business_rules/                       # HT
│   ├── api/                                      # TD
│   └── e2e/                                      # TD + TT; HT hỗ trợ giao dịch
├── infrastructure/                               # MD: DB; TD: backend; TT: frontend
├── scripts/                                      # MD: cài/backup; TD: backend; TT: đóng gói
├── evidence/
│   ├── database/                                 # MD
│   ├── queries/                                  # BD
│   ├── routines/                                 # HT
│   └── app/                                      # TD + TT
└── deliverables/                                 # TT: PDF và ZIP sau khi hoàn thiện
```

Giữ nguyên bản chụp `docs/btl1_baseline/` để đối chiếu. Nếu thay đổi cấu trúc cài đặt, cập nhật `docs/design/change_log.md`, bảng chuyển tiếp, migration và các phần SQL/API/báo cáo bị ảnh hưởng. Nếu thêm sơ đồ, dùng nguồn `.drawio`, xuất PNG/SVG và ghi đường dẫn nguồn trong tài liệu liên quan.

## 4. Checklist và cách thực hiện

Mỗi checklist cá nhân ở bảng phân công gồm **12 tác vụ cụ thể**, kèm tệp/thư mục cần sửa và hướng dẫn thực hiện. Các checklist chỉ chứa công việc và hướng dẫn, không có hạn riêng hoặc ô ký xác nhận. Chỉ đánh dấu hoàn thành khi sản phẩm thực hiện được theo hướng dẫn và đã đối chiếu kết quả.

Thứ tự phối hợp theo đầu vào cần có:

- **Đã chốt, triển khai trực tiếp:** MD dùng MySQL 8.4.13 và [schema_contract.md](docs/design/schema_contract.md), giữ 23 bảng/tên cột nghiệp vụ BTL1. TD dùng Python/Flask, TT dùng HTML/CSS/JavaScript; API và sáu thủ tục theo [hợp đồng API](docs/design/api_contract.md)/[catalog SQL](docs/design/routines_catalog.md), lỗi theo [error_codes.md](docs/design/error_codes.md). **Backend service sở hữu transaction; routine không tự COMMIT**, theo [transactions.md](docs/design/transactions.md). Không cần họp để chọn lại các phần này.
- **MD → BD/HT:** cung cấp DDL và ràng buộc; BD nạp dữ liệu rồi chạy truy vấn, HT triển khai SQL nghiệp vụ. BD gửi Q-ID để MD thiết kế và đối chiếu chỉ mục.
- **HT → TD → TT:** SQL nghiệp vụ và hợp đồng được dùng để làm API, sau đó nối UI. Có thể dùng mock có đánh dấu trong lúc phát triển; demo dùng DB thật.
- **HT + TD:** kiểm tra rollback, gửi lặp và tranh chấp bằng hai kết nối. **TD + TT:** chạy ba luồng đầu cuối và lưu dữ liệu trước/sau.
- **Cả năm → TT:** bàn giao phần báo cáo, mã và minh chứng; TT hợp nhất PDF, hoàn thiện demo và đóng gói sau khi các phần đã được kiểm tra.

`TASKS.json` lưu cùng 60 mã tác vụ, người phụ trách, đường dẫn, yêu cầu hoàn thành, phụ thuộc và trạng thái; chỉ có ngày bắt đầu/hạn chung của dự án. Khi đổi nội dung phân công, cập nhật đồng thời JSON, checklist và danh mục bàn giao trong kế hoạch này.

## 5. Danh mục sản phẩm bàn giao theo thành viên

Các mục dưới đây là sản phẩm phải hoàn thiện. Các tệp khung đã tồn tại không có nghĩa là chức năng đã chạy; PDF/ZIP ghi “dự kiến” là tên đầu ra cần tạo khi hoàn tất.

### 5.1. Nguyễn Thành Đạt (TD)

| Sản phẩm | Vị trí bàn giao | Nội dung cần có |
|---|---|---|
| Backend hoàn chỉnh và hướng dẫn chạy | `apps/backend/`<br>`.env.example`<br>`infrastructure/README.md` | Python 3.12, Flask 3.1.3, Connector/Python 26.7.0; API/auth/CSRF, transaction, chống lặp và hạn dùng server. Có requirements.in/requirements.lock, cấu hình mẫu và lệnh chạy cổng 5000. |
| Hợp đồng API và kiến trúc | `docs/design/api_contract.md`<br>`docs/design/architecture.md`<br>`docs/design/error_codes.md`<br>`docs/design/transactions.md` | API/DTO, mã lỗi, quyền, CSRF và ranh giới service transaction theo hợp đồng đã chốt; sơ đồ luồng ứng dụng. |
| Bộ kiểm tra và minh chứng backend | `tests/api/`<br>`tests/e2e/`<br>`evidence/app/` | Ca API đúng/sai quyền/sai đầu vào, rollback, gửi lặp; ba luồng tích hợp cùng TT và kết quả thực chạy. |
| Phần báo cáo backend | `docs/report/sections/03_backend.md` | Kiến trúc, ví dụ API, liên hệ BTL1, cách chạy, kết quả và giới hạn. |

### 5.2. Nguyễn Minh Đạt (MD)

| Sản phẩm | Vị trí bàn giao | Nội dung cần có |
|---|---|---|
| Bộ khởi tạo và DDL 23 bảng | `database/00_bootstrap/00_create_database.sql`<br>`database/01_schema/` | Năm tệp 01_identity.sql, 02_workstations.sql, 03_services.sql, 04_inventory.sql, 05_staff_wallet.sql; chạy được từ CSDL rỗng. |
| Ràng buộc và chỉ mục | `database/02_constraints/01_constraints.sql`<br>`database/03_indexes/01_indexes.sql`<br>`docs/design/index_catalog.md` | PK/FK/UQ/NOT NULL/CHECK, chính sách xóa và lý do chỉ mục gắn Q-ID/quy tắc; đối chiếu hiệu năng cùng BD. |
| Ánh xạ từ BTL1 và thay đổi vật lý | `docs/design/btl1_to_btl2.md`<br>`docs/design/change_log.md`<br>`docs/design/decisions.md`<br>`database/migrations/`<br>`docs/design/schema_contract.md` | MySQL 8.4.13, giữ 23 bảng/cột nghiệp vụ; năm cột sinh và ThanhTien dẫn xuất, charset/múi giờ, CH-01/CH-02 và migration cho bản đã cài nếu cần. |
| Cài mới, backup/restore và kiểm chứng CSDL | `database/README.md`<br>`scripts/`<br>`infrastructure/README.md`<br>`.env.example`<br>`tests/sql/schema/`<br>`evidence/database/` | Thứ tự chạy SQL, công cụ cài/sao lưu/khôi phục, ca khóa/ràng buộc hợp lệ và bị từ chối; kết quả dựng lại trên máy khác. |
| Phần báo cáo lược đồ | `docs/report/sections/01_schema.md` | Môi trường, cấu trúc, ràng buộc, chỉ mục, cách cài và bằng chứng. |

### 5.3. Nguyễn Phúc Bảo Đạt (BD)

| Sản phẩm | Vị trí bàn giao | Nội dung cần có |
|---|---|---|
| Dữ liệu mẫu và kịch bản dữ liệu | `database/04_seed/01_reference_data.sql`<br>`database/04_seed/02_demo_scenarios.sql`<br>`docs/design/seed_scenarios.md` | Dữ liệu nhất quán đủ 23 bảng, đúng thứ tự FK, nạp lại được; có ca bình thường, biên và bị từ chối, không dùng thông tin cá nhân thật. |
| Tám truy vấn và đặc tả | `database/05_queries/01_operations.sql`<br>`database/05_queries/02_reports.sql`<br>`docs/design/query_catalog.md` | Q01–Q04 vận hành và Q05–Q08 báo cáo; mỗi Q-ID gắn UC, tham số, SQL và kết quả mong đợi. |
| Kết quả chuẩn và minh chứng truy vấn | `tests/sql/queries/`<br>`evidence/queries/`<br>`docs/design/index_catalog.md` | Dữ liệu kiểm tra, kết quả đối chiếu, ca NULL/rỗng/biên ngày/qua đêm; EXPLAIN trước/sau chỉ mục cùng MD. |
| Phần báo cáo dữ liệu/truy vấn | `docs/report/sections/02_data_queries.md` | Đặc tả Q-ID, cách nạp dữ liệu, SQL, kết quả và giải thích phép nối/tổng hợp. |

### 5.4. Nguyễn Hữu Tây (HT)

| Sản phẩm | Vị trí bàn giao | Nội dung cần có |
|---|---|---|
| Sáu thủ tục nghiệp vụ | `database/06_procedures/01_sessions.sql`<br>`database/06_procedures/02_wallet_orders.sql`<br>`database/06_procedures/03_inventory.sql` | Mở/kết thúc phiên, nạp ví, tiếp nhận đơn, thanh toán đơn và ghi sổ phiếu kho; khóa, chống lặp và giao dịch nhất quán. |
| Hai hàm và ba nhóm trigger | `database/07_functions/01_billing.sql`<br>`database/08_triggers/01_history.sql`<br>`database/08_triggers/02_state_identity.sql` | Hàm tiền giờ/số dư khả dụng; nhóm lịch sử, trạng thái/miền liên quan, danh tính/chuyên biệt hóa. Một nhóm có thể có nhiều trigger. |
| Đặc tả và ma trận quy tắc | `docs/design/routines_catalog.md`<br>`docs/design/rules_matrix.md` | Tham số, đầu ra, mã lỗi, transaction, MaYeuCau; ánh xạ BR/D-ID vào nơi thực thi và phần còn thiếu. |
| Bộ kiểm tra nghiệp vụ và đồng thời | `tests/sql/business_rules/`<br>`evidence/routines/` | Ca thành công/từ chối, rollback, lặp yêu cầu, tranh máy/tồn/ví bằng hai kết nối; hướng dẫn và kết quả thực chạy. |
| Phần báo cáo SQL nghiệp vụ | `docs/report/sections/04_routines.md` | Đặc tả thủ tục/hàm/trigger, cách thực thi quy tắc BTL1, bằng chứng và giới hạn. |

### 5.5. Trần Tiến Thành (TT)

| Sản phẩm | Vị trí bàn giao | Nội dung cần có |
|---|---|---|
| Frontend hoàn chỉnh và phạm vi màn hình | `apps/frontend/`<br>`docs/design/ui_scope.md`<br>`.env.example`<br>`infrastructure/README.md` | HTML/CSS/JavaScript modules không build; Flask phục vụ cùng origin. Có login/CSRF, màn hình theo vai, fetch/error handler, giữ mã khi retry, README và minh chứng dùng API thật. |
| Kiểm chứng tích hợp và bộ demo | `tests/e2e/`<br>`evidence/app/`<br>`docs/demo/scenarios.md`<br>`docs/demo/runbook.md`<br>`docs/demo/questions.md` | Ba luồng UI → API → DB, dữ liệu đầu vào/trước-sau, ca thành công/từ chối; hướng dẫn dựng lại và câu hỏi cho cả năm người. |
| Phần frontend và báo cáo tổng hợp | `docs/report/sections/05_frontend_integration.md`<br>`docs/report/outline.md`<br>`deliverables/` | Tự viết phần frontend; hợp nhất năm phần, đối chiếu rubric và xuất PDF. Tệp đích dự kiến: deliverables/BTL2_L09_Nhom10_BaoCao.pdf. |
| Gói bàn giao cuối và cách sử dụng | `deliverables/`<br>`scripts/`<br>`README.md`<br>`docs/demo/runbook.md` | Tệp đích dự kiến: deliverables/BTL2_L09_Nhom10_BanGiao.zip; có SQL, mã nguồn, báo cáo, cấu hình mẫu, nguồn sơ đồ và hướng dẫn. Kiểm tra giải nén/cài/chạy lại; không chứa thư viện đã cài hoặc tệp tạm. |

## 6. Điều kiện bàn giao chung

- [ ] MD/BD dựng được DB mới, nạp dữ liệu và chạy đủ tám truy vấn; có kết quả chuẩn để đối chiếu.
- [ ] HT/TD chứng minh ràng buộc, rollback, chống lặp và tranh chấp liên quan bằng kết quả thực chạy.
- [ ] TD/TT chạy đủ ba luồng UI → API → DB, cả ca thành công và bị từ chối.
- [ ] Cả nhóm đối chiếu bảng/cột/khóa, UC và quy tắc với BTL1; thay đổi và giới hạn đã được ghi rõ.
- [ ] Năm phần báo cáo cá nhân, minh chứng và tài liệu liên quan đã bàn giao; mỗi người giải thích được phần mình.
- [ ] TT kiểm tra PDF, nguồn sơ đồ, liên kết, cấu hình mẫu, hướng dẫn chạy và danh mục tệp ZIP.
- [ ] ZIP chứa đủ sản phẩm cần nộp, không có mật khẩu thật, thư viện đã cài, tệp tạm hoặc các gói cũ lồng bên trong.
- [ ] Giải nén ZIP vào vị trí mới và làm lại bước cài/khởi động/demo theo hướng dẫn.

Kế hoạch này phân công công việc cần làm; không xác nhận phần hiện thực đã hoàn thành hay tỷ lệ đóng góp thực tế.
