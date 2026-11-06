# Báo cáo LaTeX BTL2 Phần 1–2

Biên dịch từ thư mục chứa main.tex:

```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=build main.tex
```

Cần TeX Live có fontspec, fvextra, TikZ, titlesec, fancyhdr và các gói được khai báo trong main.tex. Phông: TeX Gyre Termes, TeX Gyre Heros, Liberation Mono. Các tệp assets/ và sql/ đã nằm trong bộ nguồn, không cần truy cập database hay Internet để biên dịch lại PDF.

GVHD: ThS. Trần Thị Quế Nguyệt. Logo được tái sử dụng từ trang bìa BTL1 của nhóm. Các flowchart là TikZ vector; EER giữ nguồn SVG/PDF vector từ BTL1; minh chứng là PDF xuất từ SQL client chạy MySQL thật. Không dùng ảnh PNG flowchart độ phân giải thấp trong bản in mới.

Để cập nhật dữ liệu nguồn, chạy scripts/build_latex_report.py từ gốc dự án rồi biên dịch lại. Các thông tin phân công kế thừa hồ sơ nhóm; phần đề xuất đóng góp không phải điểm đã chấm.
