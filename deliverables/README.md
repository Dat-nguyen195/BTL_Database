# Sản phẩm bàn giao

- `BTL2_L09_Nhom10_P1_P2.pdf`: báo cáo LaTeX 66 trang để in/nộp, có logo Bách khoa và GVHD ThS. Trần Thị Quế Nguyệt.
- `BTL2_L09_Nhom10_LaTeX.zip`: bộ nguồn LaTeX tự đủ, gồm main.tex, nội dung, SQL, TikZ, dữ liệu phân công và tài sản vector.
- `BTL2_L09_Nhom10_BanGiao.zip`: mã nguồn, SQL, báo cáo, thiết kế, minh chứng và hướng dẫn.
- `SHA256SUMS`: mã kiểm tra ba tệp trên.

PDF được quản lý trong Git. Hai ZIP và checksum được tạo local bằng:

```bash
apps/backend/.venv/bin/python scripts/package_deliverables.py
```

ZIP không chứa `.env`, môi trường Python, bộ nhớ đệm, tệp biên dịch LaTeX hoặc bản ZIP khác. Mỗi ZIP có manifest SHA-256 cho các tệp bên trong; công cụ đóng gói kiểm tra CRC, nội dung và bí mật cấu hình trước khi bàn giao.

Nguồn chính ở `docs/report/latex/`. Sau khi giải nén ZIP LaTeX, biên dịch từ thư mục có main.tex:

```bash
latexmk -xelatex -outdir=build main.tex
```
