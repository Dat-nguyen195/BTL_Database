# Báo cáo LaTeX BTL2 Phần 1–2

`main.tex` là tệp chính; cần giữ đủ `sections/`, `diagrams/`, `sql/` và `assets/` khi tải lên trình soạn thảo.

## Cách biên dịch

Báo cáo dùng **XeLaTeX**. `pdfLaTeX` không hỗ trợ fontspec và sẽ dừng ngay ở đầu báo cáo.

Từ thư mục chứa main.tex, chạy:

```bash
latexmk main.tex
```

Tệp cấu hình ẩn `.latexmkrc` đã chọn XeLaTeX, tự chạy đủ các lượt để cập nhật mục lục/tham chiếu và ghi PDF vào `main.pdf` ngay cạnh main.tex. Vị trí này khớp trình xem PDF mặc định của LaTeX Workshop, kể cả khi mở thư mục cha chứa cả BTL1 và BTL2. Nếu công cụ không đọc tệp cấu hình ẩn, dùng lệnh rõ trình biên dịch:

```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
```

Từ gốc repository có thể chạy `./scripts/build_report_latex.sh` để biên dịch riêng vào `build/` và cập nhật PDF nộp trong deliverables.

## VS Code / LaTeX Workshop

Mở `docs/report/latex/main.tex`, chọn **Build LaTeX project** (Ctrl+Alt+B), rồi **View LaTeX PDF** (Ctrl+Alt+V). Nếu mở thư mục cha như Assignment, hai lệnh này vẫn dùng main.pdf ngay cạnh main.tex. Repository có recipe XeLaTeX trong `.vscode/settings.json`; main.tex có chỉ dẫn chạy latexmk và các tệp con trỏ về main.tex. Không chọn recipe pdfLaTeX hoặc biên dịch riêng một tệp trong sections/.

Nếu từng gặp lỗi fontspec, sau khi cập nhật nguồn hãy chạy lệnh XeLaTeX ở trên hoặc chọn recipe **BTL2: XeLaTeX (latexmk)**. Không dùng lại kết quả thất bại được lưu từ lượt pdfLaTeX cũ.

## Overleaf

Tải **toàn bộ bộ nguồn LaTeX** (bao gồm tệp ẩn `.latexmkrc`) vào project, chọn **Main document: main.tex** và **Compiler: XeLaTeX** trong phần cài đặt. Nếu nhập toàn bộ repository, chọn main document là `docs/report/latex/main.tex`. Không chỉ tải riêng main.tex.

## Phụ thuộc

Cần latexmk và TeX Live/XeLaTeX có fontspec, TeX Gyre, fvextra, TikZ, titlesec, fancyhdr, needspace và các gói khai báo trong main.tex. Trên Debian/Ubuntu có thể cài:

```bash
sudo apt install latexmk texlive-xetex texlive-latex-extra texlive-pictures tex-gyre
```

Phông TeX Gyre Termes/Heros thuộc bộ TeX; bốn kiểu Liberation Mono đã được kèm trong `assets/fonts/` cùng giấy phép SIL OFL. Không phụ thuộc phông Liberation Mono được cài riêng trên máy. Các tệp SQL và hình đã nằm trong bộ nguồn; không cần database hoặc Internet khi biên dịch sau khi đã cài TeX.

GVHD: ThS. Trần Thị Quế Nguyệt. Logo kế thừa trang bìa BTL1; lưu đồ TikZ và EER/PDF vector giữ nét khi phóng to. Minh chứng SQL được xuất từ MySQL thật.

Để cập nhật nội dung từ SQL hiện hành, chạy `python3 scripts/build_latex_report.py` tại gốc repository rồi biên dịch lại. Phân công nằm trong `team_assignments.json`; tỉ lệ đóng góp là đề xuất của nhóm.

Các lưu đồ được chỉnh trực tiếp trong `diagrams/*.tex`, dùng chung hình học và kiểu chữ trong `diagrams/styles.tex`. Script cập nhật SQL giữ nguyên các tệp sơ đồ để tránh làm mất phần dàn trang đã kiểm tra.
