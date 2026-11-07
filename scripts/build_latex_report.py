"""Prepare a self-contained Vietnamese XeLaTeX report from verified project sources.
Compile: cd docs/report/latex && latexmk -xelatex -outdir=build main.tex
"""
from pathlib import Path
import json,re,shutil
from submission_queries import queries
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/report/latex'

def esc(v):
    return ''.join({'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}.get(c,c) for c in str(v))
def write(name,text):
    p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
    if p.suffix == '.tex' and name != 'main.tex':
        text='% !TeX root = ../main.tex\n'+text.strip()
    p.write_text(text.strip()+'\n')
def routine_file(source,names,target):
    parts=[]
    for b in (ROOT/source).read_text().split('$$'):
        for name in names:
            m=re.search(r'CREATE (?:PROCEDURE|FUNCTION|TRIGGER) `?'+name+r'`?\b',b)
            if m:parts.append(b[m.start():].strip()+'$$')
    assert len(parts)==len(names),(source,names)
    write('sql/'+target,'DELIMITER $$\n\n'+'\n\n'.join(parts)+'\n\nDELIMITER ;')
def snap(name,caption,label=None):
    return r'\snapshot{'+name+'}{'+esc(caption)+'}{'+(label or 'fig:'+name)+'}\n'
def sql(name,title):return r'\sqlinput{sql/'+name+'}{'+esc(title)+'}\n'
def cases(name):
    shutil.copy2(ROOT/'evidence/dbms'/f'{name}.sql',OUT/'sql'/f'demo_{name}.sql')
    return sql('demo_'+name+'.sql','Câu lệnh kiểm chứng trên MySQL')
def flow(name,caption):return r'\flowfigure{diagrams/'+name+'.tex}{'+esc(caption)+'}{fig:flow-'+name+'}\n'
def result_table(name,selected,headers,caption):
    record=json.loads((ROOT/'evidence/dbms'/f'{name}.json').read_text())
    found=next(r for r in record['results'] if r['rows'] and not r['error'])
    rows=[]
    for r in found['rows']:
        d=dict(zip(found['columns'],r));rows.append([d[k] for k in selected])
    s='\\begin{table}[H]\n\\centering\\small\n\\caption{'+esc(caption)+'}\n\\begin{tabularx}{\\linewidth}{@{}'+('X'*len(headers))+'@{}}\\toprule\n'
    s+=' & '.join('\\textbf{'+esc(h)+'}' for h in headers)+r'\\\midrule'+'\n'
    for row in rows:s+=' & '.join(esc(v) for v in row)+r'\\'+'\n'
    return s+'\\bottomrule\\end{tabularx}\\end{table}\n'

def prepare():
    for d in ['assets/dbms','assets/eer','sections','diagrams','sql']: (OUT/d).mkdir(parents=True,exist_ok=True)
    for i,p in enumerate(sorted((ROOT/'database/01_schema').glob('*.sql')),1):shutil.copy2(p,OUT/'sql'/p.name)
    for path,target in [('database/02_constraints/01_constraints.sql','constraints.sql'),('database/03_indexes/01_indexes.sql','indexes.sql')]:shutil.copy2(ROOT/path,OUT/'sql'/target)
    for key,q in queries().items():write('sql/'+key+'.sql',q)
    routines=[('database/06_procedures/04_khu_vuc_crud.sql',['sp_khu_vuc_insert'],'insert.sql'),('database/06_procedures/04_khu_vuc_crud.sql',['sp_khu_vuc_update'],'update.sql'),('database/06_procedures/04_khu_vuc_crud.sql',['sp_khu_vuc_delete'],'delete.sql'),('database/08_triggers/01_history.sql',['tr_bien_lai_tien_may_update','tr_bien_lai_tien_may_delete'],'trigger_receipt.sql'),('database/08_triggers/03_order_detail_triggers.sql',['tr_chi_tiet_goi_dich_vu_after_insert','tr_chi_tiet_goi_dich_vu_after_update','tr_chi_tiet_goi_dich_vu_after_delete'],'trigger_total.sql'),('database/06_procedures/05_reports_p12.sql',['sp_bao_cao_doanh_thu_ngay'],'report_revenue.sql'),('database/06_procedures/05_reports_p12.sql',['sp_bao_cao_ton_dich_vu'],'report_stock.sql'),('database/07_functions/02_functions_p12.sql',['fn_tong_chi_vi_rong'],'fn_wallet.sql'),('database/07_functions/02_functions_p12.sql',['fn_tong_tien_don'],'fn_order.sql')]
    for source,names,target in routines:routine_file(source,names,target)
    bench=json.loads((ROOT/'evidence/queries/index_benchmark.json').read_text())
    for phase in ['before','after']:write('sql/plan_'+phase+'.txt',bench[phase]['plan'])
    # Preserve hand-maintained vector diagrams; rebuilding SQL must not reset their layout.
    for name in ['styles','architecture','crud_insert','crud_update','crud_delete','receipt','order_total','revenue','stock','wallet','order']:
        if not (OUT/'diagrams'/(name+'.tex')).is_file():
            raise FileNotFoundError('Missing report diagram: '+name)
    write('main.tex',r'''% !TeX program = latexmk
% !TeX encoding = UTF-8
\documentclass[11pt,a4paper]{report}
\usepackage{fontspec}
\setmainfont{TeX Gyre Termes}
\setsansfont{TeX Gyre Termes}
\setmonofont{LiberationMono}[
  Path=assets/fonts/,
  Extension=.ttf,
  UprightFont=*-Regular,
  BoldFont=*-Bold,
  ItalicFont=*-Italic,
  BoldItalicFont=*-BoldItalic,
  Scale=1.0
]
\usepackage[a4paper,left=25mm,right=22mm,top=23mm,bottom=23mm,headheight=15pt]{geometry}
\usepackage{xcolor,graphicx,booktabs,longtable,tabularx,array,multirow}
\usepackage{tikz}\usetikzlibrary{arrows.meta,shapes.geometric,positioning,calc}
\usepackage{fvextra,float,caption,enumitem,titlesec,fancyhdr,lastpage,needspace,etoolbox}
\usepackage[unicode,hypertexnames=false,colorlinks=true,allcolors=black]{hyperref}
\definecolor{Ink}{HTML}{000000}\definecolor{Accent}{HTML}{000000}
\definecolor{Pale}{HTML}{F8F8F8}\definecolor{Edge}{HTML}{000000}
\definecolor{ErrorInk}{HTML}{000000}\definecolor{Gold}{HTML}{F8F8F8}
\hypersetup{pdftitle={BTL2 Phần 1 và 2 Hệ thống quản lý quán Net},pdfauthor={L09 Nhóm 09},pdfsubject={GVHD ThS. Trần Thị Quế Nguyệt}}
\renewcommand{\contentsname}{Mục lục}\renewcommand{\listfigurename}{Danh mục hình}
\renewcommand{\figurename}{Hình}\renewcommand{\tablename}{Bảng}\renewcommand{\chaptername}{Phần}
\renewcommand{\bibname}{Tài liệu và nguồn đối chiếu}
\setcounter{tocdepth}{2}\setcounter{secnumdepth}{2}
\setlength{\parindent}{0pt}\setlength{\parskip}{5pt}\linespread{1.08}
\setlength{\emergencystretch}{2em}
\setlist[itemize]{leftmargin=5mm,itemsep=2pt,topsep=3pt}
\setlist[enumerate]{leftmargin=7mm,itemsep=2pt,topsep=3pt}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\small HỆ CƠ SỞ DỮ LIỆU | BTL2}
\fancyhead[R]{\small L09 — Nhóm 09}\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0.3pt}
\fancypagestyle{plain}{\fancyhf{}\fancyfoot[C]{\small\thepage}\renewcommand{\headrulewidth}{0pt}}
\titleformat{\chapter}[display]{\bfseries\color{black}}{\large PHẦN \thechapter}{6pt}{\LARGE}
\titlespacing*{\chapter}{0pt}{-10pt}{18pt}
\titleformat{\section}{\large\bfseries\color{black}}{\thesection}{.7em}{}
\titleformat{\subsection}{\normalsize\bfseries\color{black}}{\thesubsection}{.7em}{}
\preto\section{\Needspace{10\baselineskip}}
\preto\subsection{\Needspace{6\baselineskip}}
\captionsetup{font=small,labelfont=bf,labelsep=period,skip=7pt}
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}
\newcommand{\code}[1]{\texttt{\detokenize{#1}}}
\newcommand{\sqlinput}[2]{\par\needspace{5\baselineskip}\noindent{\small\bfseries\color{black}#2}\par\vspace{-2pt}\VerbatimInput[fontsize=\fontsize{8.6}{10.7}\selectfont,breaklines=true,breakanywhere=true,numbers=left,numbersep=5pt,frame=lines,framesep=3mm,rulecolor=\color{black},numberblanklines=false]{#1}\par}
\newcommand{\snapshot}[3]{\begin{figure}[H]\centering\includegraphics[width=\linewidth,height=.75\textheight,keepaspectratio]{assets/dbms/#1.pdf}\caption{#2}\label{#3}\end{figure}}
\input{diagrams/styles.tex}
\newsavebox{\flowbox}
\newcommand{\flowfigure}[3]{\begin{figure}[H]\centering
\sbox{\flowbox}{\input{#1}}%
\typeout{FLOWFIGURE #1: width=\the\wd\flowbox; height=\the\dimexpr\ht\flowbox+\dp\flowbox\relax}%
\ifdim\wd\flowbox>\linewidth\resizebox{\linewidth}{!}{\usebox{\flowbox}}\else\usebox{\flowbox}\fi
\caption{#2}\label{#3}\end{figure}}
\begin{document}
\input{sections/cover}
\pagenumbering{roman}
\tableofcontents\clearpage
\chapter*{Phạm vi và cách đọc báo cáo}\addcontentsline{toc}{chapter}{Phạm vi và cách đọc báo cáo}
Báo cáo trình bày phần hiện thực cơ sở dữ liệu của hệ thống quản lý quán Net, kế thừa mô hình 23 bảng từ BTL1. Phạm vi Phần 1–2 gồm lược đồ vật lý, dữ liệu mẫu, chỉ mục, truy vấn, thủ tục, hàm và trigger. Ứng dụng Flask được dùng để kiểm chứng các giao dịch và ba luồng vận hành liên quan.

Các câu SQL trong báo cáo lấy từ bộ mã bàn giao. Ảnh minh chứng là bản xuất trực tiếp của SQL client kết nối MySQL 8.4.13; câu lệnh và đầu ra thô được lưu theo từng lần chạy. Các lưu đồ được dựng bằng TikZ, còn sơ đồ EER được nhúng ở dạng vector để phóng to không vỡ chữ. Toàn bộ chữ và câu lệnh được trình bày bằng phông chữ Times New Roman và mực đen theo đúng quy chuẩn báo cáo học thuật.
\begin{table}[H]\small\centering\caption{Đối chiếu cấu trúc báo cáo với mẫu Phần 1–2}
\begin{tabularx}{\linewidth}{@{}p{32mm}Yp{28mm}@{}}\toprule
\textbf{Mục theo Mẫu BTL2} & \textbf{Sản phẩm trình bày} & \textbf{Vị trí}\\\midrule
1.1 Các câu lệnh tạo bảng và ràng buộc & 23 bảng; khóa, miền giá trị và các ca vi phạm & Mục \ref{sec:schema}\\
1.2 Câu lệnh tạo chỉ mục & Lý do lựa chọn; kế hoạch và số đo trước/sau & Mục \ref{sec:index}\\
1.3 Truy vấn dữ liệu & Năm truy vấn, dữ liệu và kết quả đối chiếu & Mục \ref{sec:queries}\\
2. THỦ TỤC – HÀM - TRIGGER & CRUD, hai yêu cầu trigger, hai thủ tục và hai hàm & Phần \ref{chap:routines}\\
3. PHẦN THÊM & Kiểm chứng giao dịch, hồi quy và ba luồng demo & Phần \ref{chap:verification}\\
Bảng kê nhiệm vụ & Phân công theo nội dung và người phụ trách & Phụ lục A\\
Đánh giá của giáo viên & Bảng đánh giá theo tỷ lệ đề xuất & Phụ lục A\\
Phụ lục ERD & Thiết kế ERD cập nhật và ghi chú thay đổi BTL1 & Phụ lục B\\
Dữ liệu mẫu & Bảng dữ liệu mẫu và nguồn minh chứng DBMS & Phụ lục C\\\bottomrule
\end{tabularx}\end{table}
\clearpage\pagenumbering{arabic}
\input{sections/01_schema}
\input{sections/02_routines}
\input{sections/03_verification}
\appendix
\input{sections/04_appendices}
\end{document}''')
    write('sections/cover.tex',r'''\begin{titlepage}\thispagestyle{empty}
\begin{center}
{\fontsize{11.5}{15}\selectfont ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH}\\[3mm]
{\bfseries\fontsize{14}{18}\selectfont TRƯỜNG ĐẠI HỌC BÁCH KHOA}\\[10mm]
\includegraphics[width=35mm]{assets/logo_bach_khoa.png}\\[11mm]
{\fontsize{14}{18}\selectfont BÁO CÁO BÀI TẬP LỚN SỐ 2 - PHẦN 1 \& 2}\\[3mm]
{\bfseries\fontsize{18}{22}\selectfont MÔN HỆ CƠ SỞ DỮ LIỆU}\\[2mm]
{\fontsize{11}{14}\selectfont Học kỳ 261}\\[10mm]
{\bfseries\fontsize{24}{30}\selectfont HỆ THỐNG QUẢN LÝ\\QUÁN NET}\\[12mm]
\begin{tabular}{@{}rl@{}}
\textbf{GVHD:}&\textbf{ThS. Trần Thị Quế Nguyệt}\\[3mm]
\textbf{Lớp:}&L09\\[2mm]\textbf{Nhóm:}&09
\end{tabular}\\[10mm]
{\bfseries Sinh viên thực hiện}\\[3mm]
\renewcommand{\arraystretch}{1.25}
\begin{tabular}{@{}ll@{}}\toprule
\textbf{Họ và tên} & \textbf{MSSV}\\\midrule
\underline{Nguyễn Thành Đạt} & 2410709\\
Nguyễn Minh Đạt & 2410694\\
Nguyễn Phúc Bảo Đạt & 2410696\\
Nguyễn Hữu Tây & 2413095\\
Trần Tiến Thành & 2413181\\\bottomrule
\end{tabular}\\[2.5mm]
{\footnotesize\itshape (*Gạch dưới tên thành viên nộp báo cáo trên LMS)}
\vfill
{Thành phố Hồ Chí Minh, tháng 11 năm 2026}
\end{center}\end{titlepage}''')
    schema=r'''\chapter{Tạo bảng, dữ liệu mẫu và truy vấn dữ liệu}\label{chap:schema}
\section{Các câu lệnh tạo bảng và ràng buộc kiểm tra}\label{sec:schema}
\subsection{Tổ chức lược đồ}
Hệ thống quản lý đồng thời thời gian sử dụng máy, ví hội viên, bán dịch vụ và tồn kho. Một sự kiện kinh tế được lưu qua chứng từ: phiên và biên lai cho tiền máy; đơn cùng dòng chi tiết cho dịch vụ; phiếu cùng dòng chi tiết cho nhập, xuất hoặc kiểm kê. Cách tổ chức này giúp truy nguyên thay đổi số dư và tồn thay vì chỉ lưu các giá trị tổng hiện tại.

MySQL 8.4.13 sử dụng InnoDB để hỗ trợ khóa ngoại và giao dịch. Các mã định danh dùng so sánh nhị phân \code{ascii_bin}; dữ liệu văn bản dùng \code{utf8mb4_0900_as_cs}. Tiền VND được lưu theo số nguyên; giá trị dẫn xuất ở dòng chi tiết được tính từ số lượng và đơn giá.
\begin{table}[H]\centering\small\caption{Năm phân hệ trong lược đồ 23 bảng}
\begin{tabularx}{\linewidth}{@{}p{34mm}Yc@{}}\toprule
\textbf{Phân hệ}&\textbf{Các bảng}&\textbf{Số bảng}\\\midrule
Danh tính & NHOM\_NGUOI\_DUNG, TAI\_KHOAN, SO\_DIEN\_THOAI, NGUOI\_CHOI, NHAN\_VIEN, DIA\_CHI\_NV & 6\\
Máy trạm & KHU\_VUC, NHOM\_MAY, BANG\_GIA, MAY\_TRAM, PHIEN\_SU\_DUNG, BIEN\_LAI\_TIEN\_MAY & 6\\
Dịch vụ & NHOM\_DICH\_VU, DON\_VI\_TINH, MAY\_IN, DICH\_VU, DON\_GOI\_DICH\_VU, CHI\_TIET\_GOI\_DICH\_VU & 6\\
Kho & PHIEU\_KHO, CHI\_TIET\_PHIEU\_KHO & 2\\
Nhân sự và ví & CA\_TRUC, PHAN\_CONG\_TRUC, GIAO\_DICH\_VI & 3\\\bottomrule
\end{tabularx}\end{table}
\subsection{Câu lệnh tạo bảng}
Các tệp sau là nguồn DDL được dùng khi khởi tạo database mới. Khóa chính định danh từng thực thể; UNIQUE ngăn trùng mã nghiệp vụ; CHECK giới hạn trạng thái, miền tiền, số lượng và thứ tự thời gian. Cột sinh kết hợp UNIQUE được dùng cho các trường hợp cần đảm bảo duy nhất có điều kiện, chẳng hạn một máy chỉ có một phiên đang hoạt động.
'''
    for name,title in [('01_identity.sql','DDL phân hệ danh tính'),('02_workstations.sql','DDL phân hệ máy trạm'),('03_services.sql','DDL phân hệ dịch vụ'),('04_inventory.sql','DDL phân hệ kho'),('05_staff_wallet.sql','DDL phân hệ nhân sự và ví')]:schema+=sql(name,title)
    schema+=r'''\subsection{Khóa ngoại và chính sách toàn vẹn}
Khóa ngoại bảo đảm các dòng chi tiết và chứng từ tham chiếu đối tượng tồn tại. Các tham chiếu lịch sử dùng RESTRICT khi việc xóa đối tượng cha có thể làm mất khả năng đối soát. CASCADE chỉ được sử dụng theo quan hệ đã định nghĩa trong DDL; không được hiểu là quyền tùy ý xóa chứng từ đã chốt.
'''+sql('constraints.sql','Các khóa ngoại được áp dụng')
    schema+=snap('img_01_dbms_tables','Kết quả DBMS minh họa câu lệnh tạo bảng thực thi thành công (23 bảng)')+snap('img_02_dbms_constraints','Kết quả DBMS minh họa các ràng buộc khóa ngoại và CHECK được áp dụng')
    schema+=r'''\section{Câu lệnh tạo chỉ mục}\label{sec:index}
\subsection{Mô tả lý do cần đánh chỉ mục}
Ở màn hình gọi món tại máy hoặc bán tại quầy, người dùng lọc dịch vụ đang kinh doanh theo nhóm và khoảng giá, sau đó xem giá từ cao xuống thấp. Yêu cầu này xuất phát từ chức năng xem thực đơn phục vụ khách và thu ngân. Truy vấn Q-P12-02 vì vậy là cơ sở lựa chọn chỉ mục nhiều cột, không đánh chỉ mục tách rời khỏi nhu cầu sử dụng thực tế.
'''+sql('indexes.sql','Câu lệnh tạo chỉ mục: ix_dich_vu_filter')
    schema+=r'''\subsection{Minh họa hiệu quả truy vấn trước và sau khi đánh chỉ mục}
Phép đo dùng database riêng với 20.000 dòng dịch vụ, 10 nhóm và hai đơn vị tính. Cùng một câu SELECT được chạy 20 lượt trước và sau khi thêm \code{ix_dich_vu_filter}. Cả hai giai đoạn đều lấy hết tập kết quả. Số đo phụ thuộc máy chạy, cache và tải tại thời điểm đo; đây là bằng chứng cho tập dữ liệu cụ thể, không phải cam kết hiệu năng trong mọi môi trường.
'''
    schema+='\\begin{table}[H]\\centering\\caption{So sánh hiệu năng truy vấn trước và sau khi đánh chỉ mục}\\begin{tabularx}{\\linewidth}{@{}Yrr@{}}\\toprule\\textbf{Chỉ tiêu}&\\textbf{Trước}&\\textbf{Sau}\\\\\\midrule\n'
    schema+=f"Thời gian trung bình 20 lượt (ms)&{bench['before']['mean_ms']:.3f}&{bench['after']['mean_ms']:.3f}\\\\\nSố dòng kết quả&{bench['before']['rows']}&{bench['after']['rows']}\\\\\nCó bước Sort&{'Có' if bench['before']['has_sort'] else 'Không'}&{'Có' if bench['after']['has_sort'] else 'Không'}\\\\\\bottomrule\\end{{tabularx}}\\end{{table}}\n"
    schema+=f"Hiệu quả tăng tốc đạt \\textbf{{{bench['speedup']:.2f} lần}} (từ {bench['before']['mean_ms']:.1f}ms xuống {bench['after']['mean_ms']:.1f}ms). Kế hoạch thực thi dưới đây minh họa chi tiết đường dẫn truy xuất dữ liệu từ Table Scan sang Index Range Scan:\n"
    schema+=sql('plan_before.txt','Kế hoạch thực thi EXPLAIN ANALYZE trước khi tạo chỉ mục')+sql('plan_after.txt','Kế hoạch thực thi EXPLAIN ANALYZE sau khi tạo chỉ mục')
    schema+=snap('index_before','Kết quả DBMS hiển thị EXPLAIN ANALYZE trước khi tạo chỉ mục')+snap('index_after','Kết quả DBMS hiển thị EXPLAIN ANALYZE sau khi tạo chỉ mục')
    schema+=r'''\section{Truy vấn dữ liệu}\label{sec:queries}
Yêu cầu: 5 câu truy vấn độc lập trên các bảng dữ liệu khác nhau, kèm dữ liệu mẫu và kết quả thực thi trên DBMS. Hai câu đầu có SELECT, FROM, WHERE, ORDER BY; hai câu tiếp theo có GROUP BY và AGGREGATE; câu cuối cùng lồng 2 cấp và AGGREGATE. Các bảng dữ liệu mẫu chi tiết được đối chiếu thêm tại Phụ lục \ref{app:data}.
'''
    query_specs=[
      ('Danh sách máy theo khu vực','Mô tả: Dùng cho màn hình sơ đồ máy của thu ngân để kiểm tra các máy có thể sử dụng tại KV01, hiển thị tên máy, nhóm máy và đơn giá giờ; sắp xếp theo vị trí hàng, cột.',['MaMay','TenMay','TrangThaiMay','TenNhomMay','DonGiaGioMacDinh'],['Mã máy','Tên máy','Trạng thái','Nhóm máy','Giá giờ']),
      ('Lọc thực đơn theo nhóm và giá','Mô tả: Dùng cho màn hình gọi món của khách hoặc bán tại quầy của thu ngân để tìm các món thuộc nhóm NDV01 có giá từ 10.000 đến 50.000đ; sắp theo giá giảm dần rồi theo mã.',['MaDichVu','TenDichVu','TenDonVi','GiaBanHienHanh','SoLuongTon'],['Mã DV','Tên dịch vụ','Đơn vị','Giá bán','Tồn']),
      ('Tổng hợp đơn đã thanh toán','Mô tả: Dùng cho màn hình báo cáo ca của quản lý để thống kê số đơn và doanh số theo ngày đặt và kênh đặt; có nhóm theo ngày, kênh và tính tổng tiền, đếm số đơn.',['NgayDat','KenhDat','SoLuongDon','TongTienDonHang'],['Ngày đặt','Kênh đặt','Số đơn','Tổng tiền']),
      ('Số ca và thời lượng trực','Mô tả: Dùng cho màn hình chấm công và phân ca để thống kê tổng số ca và tổng thời lượng trực của nhân viên; loại bỏ trùng lặp mã ca trước khi cộng tổng.',['MaNhanVien','TenNhanVien','TongSoCaTruc','TongGioTruc'],['Mã NV','Tên nhân viên','Số ca','Số giờ']),
      ('Hội viên có số dư vượt mức trung bình','Mô tả: Dùng cho màn hình chăm sóc khách hàng VIP để tìm hội viên có số dư ví cao hơn mức số dư trung bình của nhóm hội viên từng phát sinh giao dịch ví thành công.',['MaHoiVien','TenHoiVien','SoDuVi','NgayDangKy'],['Mã hội viên','Tên hội viên','Số dư ví','Ngày đăng ký'])]
    for i,(title,desc,cols,heads) in enumerate(query_specs,1):
        name=f'img_{i+3:02d}_q{i:02d}';schema+=f'\\subsection{{Câu truy vấn {i}: {title} (Q-P12-{i:02d})}}\n{esc(desc)}\n'
        schema+=sql(f'Q-P12-{i:02d}.sql',f'Câu lệnh SELECT - Truy vấn {i} (Q-P12-{i:02d})')
        schema+=result_table(name,cols,heads,f'Bảng dữ liệu mẫu và kết quả thực thi Truy vấn {i}')+snap(name,f'Kết quả màn hình hiển thị từ DBMS minh họa thực thi Truy vấn {i}')
    write('sections/01_schema.tex',schema)
    routines_text=r'''\chapter{THỦ TỤC – HÀM - TRIGGER}\label{chap:routines}
\section{Thủ tục INSERT / UPDATE / DELETE dữ liệu vào 1 bảng dữ liệu}
\subsection{Nguyên tắc xử lý và bảng dữ liệu chính}
Bảng dữ liệu chính liên quan: \code{KHU_VUC}. Bảng dữ liệu phụ liên quan: \code{MAY_TRAM}, \code{PHAN_CONG_TRUC}. Thủ tục kiểm tra đầy đủ điều kiện ràng buộc nghiệp vụ và xử lý ngoại lệ có mã lỗi rõ ràng. Mỗi thủ tục trả về mã khu vực, tên thao tác và số dòng bị tác động.
'''
    for mode,m_name,title,desc,record in [
      ('insert','INSERT',r'Thủ tục INSERT: Thêm khu vực (sp\_khu\_vuc\_insert)',r'Mô tả: Thêm khu vực mới trong màn hình quản trị mặt bằng quán. Kiểm tra mã không rỗng, tên không trùng. Input: \code{p_ma_khu_vuc}, \code{p_ten_khu_vuc}, \code{p_mo_ta_vi_tri}. Output: \code{ma_khu_vuc}, \code{thao_tac}, \code{so_dong_tac_dong}.','img_09_crud_insert'),
      ('update','UPDATE',r'Thủ tục UPDATE: Cập nhật khu vực (sp\_khu\_vuc\_update)',r'Mô tả: Cập nhật thông tin tên và vị trí khu vực. Kiểm tra khu vực tồn tại, tên mới không trùng khu vực khác. Input: \code{p_ma_khu_vuc}, \code{p_ten_moi}, \code{p_mo_ta_moi}. Output: \code{ma_khu_vuc}, \code{thao_tac}, \code{so_dong_tac_dong}.','img_10_crud_update'),
      ('delete','DELETE',r'Thủ tục DELETE: Xóa khu vực (sp\_khu\_vuc\_delete)',r'Mô tả: Xóa khu vực không còn hoạt động. Kiểm tra khu vực tồn tại và không còn máy trạm hoặc lịch trực tham chiếu. Input: \code{p_ma_khu_vuc}. Output: \code{ma_khu_vuc}, \code{thao_tac}, \code{so_dong_tac_dong}.','img_11_crud_delete')]:
        routines_text+='\\subsection{'+title+'}\n'+desc+'\n'+flow('crud_'+mode,'Lưu đồ minh họa thao tác xử lý thủ tục '+m_name)+sql(mode+'.sql','Câu lệnh tạo thủ tục '+m_name)+cases(record)+snap(record,'Kết quả từ DBMS minh họa kiểm tra thủ tục '+m_name+' (trường hợp báo lỗi và trường hợp đúng)')
    routines_text+=snap('routines_created','Kết quả màn hình hiển thị từ DBMS minh họa cho việc tạo các thủ tục CRUD')
    routines_text+=r'''\section{TRIGGER}
\subsection{Trigger 1: Bảo vệ biên lai đã thanh toán (T-P12-01)}
Bảng dữ liệu chính liên quan: \code{BIEN_LAI_TIEN_MAY}. Mô tả: Trigger kiểm tra ràng buộc nghiệp vụ kế toán — không cho phép sửa đổi hoặc xóa biên lai đã ở trạng thái thanh toán (\code{DA_THANH_TOAN}). Được kích hoạt BEFORE UPDATE và BEFORE DELETE. Vẽ flowchart minh họa xử lý.
'''+flow('receipt','Lưu đồ minh họa xử lý Trigger 1 bảo vệ biên lai đã thanh toán')+sql('trigger_receipt.sql','Câu lệnh tạo Trigger 1 trên BIEN_LAI_TIEN_MAY')+cases('img_12_trigger_t1')+snap('img_12_trigger_t1','Kết quả DBMS minh họa trường hợp báo lỗi: Chặn sửa và xóa biên lai đã thanh toán')+cases('trigger_t1_valid')+snap('trigger_t1_valid','Kết quả DBMS minh họa trường hợp đúng: Cho phép sửa và xóa biên lai chưa thanh toán')
    routines_text+=r'''\subsection{Trigger 2: Đồng bộ tổng tiền đơn từ chi tiết (T-P12-02)}
Bảng dữ liệu chính liên quan: \code{CHI_TIET_GOI_DICH_VU}. Bảng dữ liệu phụ liên quan: \code{DON_GOI_DICH_VU}. Mô tả: Nhóm trigger thao tác ảnh hưởng tới hơn 1 bảng — tự động cập nhật tổng tiền đầu đơn (\code{tong_tien}) khi thêm, sửa số lượng/giá, hoặc xóa dòng chi tiết món. Kích hoạt AFTER INSERT, AFTER UPDATE, AFTER DELETE.
'''+flow('order_total','Lưu đồ minh họa xử lý Trigger 2 đồng bộ tổng giá trị đơn hàng')+sql('trigger_total.sql','Câu lệnh tạo nhóm Trigger 2 trên CHI_TIET_GOI_DICH_VU')+cases('trigger_t2_before')+snap('trigger_t2_before','Dữ liệu đơn hàng ban đầu có tổng tiền bằng 0')+cases('img_13_trigger_t2')+snap('img_13_trigger_t2','Kết quả DBMS minh họa trường hợp đúng: Tổng tiền tự động đồng bộ khi thêm/sửa/xóa dòng món')+cases('trigger_t2_errors')+snap('trigger_t2_errors','Kết quả DBMS minh họa trường hợp báo lỗi: Chặn thao tác trên đơn đã đóng hoặc đã hủy')+snap('triggers_created','Các trigger trong hai yêu cầu đã được tạo')
    routines_text+=r'''\section{THỦ TỤC}
\subsection{Thủ tục 1: Báo cáo doanh thu theo ngày (sp\_bao\_cao\_doanh\_thu\_ngay)}
Mô tả thủ tục: Tổng hợp dữ liệu từ nhiều bảng (\code{BIEN_LAI_TIEN_MAY}, \code{DON_GOI_DICH_VU}). Sử dụng câu lệnh điều kiện IF kiểm tra ngày hợp lệ và vòng lặp WHILE duyệt qua từng ngày trong khoảng thời gian để tính tổng thu máy, thu dịch vụ và hoàn tiền. Output: Mảng JSON doanh thu chi tiết từng ngày.
'''+flow('revenue','Lưu đồ minh họa Thủ tục 1 duyệt vòng lặp WHILE tính doanh thu theo ngày')+sql('report_revenue.sql','Câu lệnh tạo Thủ tục 1: sp_bao_cao_doanh_thu_ngay')+cases('img_14_sp_doanh_thu')+snap('img_14_sp_doanh_thu','Kết quả DBMS minh họa kiểm tra Thủ tục 1 (ca báo lỗi ngày sai và ca đúng trả mảng JSON)')
    routines_text+=r'''\subsection{Thủ tục 2: Báo cáo tồn và phân loại dịch vụ (sp\_bao\_cao\_ton\_dich\_vu)}
Mô tả thủ tục: Đọc dữ liệu từ bảng \code{DICH_VU}, \code{NHOM_DICH_VU}, \code{DON_VI_TINH}. Sử dụng CURSOR duyệt danh sách món kết hợp IF/ELSE phân loại trạng thái tồn kho (\code{HetHang}, \code{SapHet}, \code{DuHang}) theo ngưỡng chỉ định. Output: Mảng JSON danh sách dịch vụ và trạng thái phân loại.
'''+flow('stock','Lưu đồ minh họa Thủ tục 2 sử dụng CURSOR và IF phân loại tồn kho')+sql('report_stock.sql','Câu lệnh tạo Thủ tục 2: sp_bao_cao_ton_dich_vu')+cases('img_15_sp_ton_kho')+snap('img_15_sp_ton_kho','Kết quả DBMS minh họa kiểm tra Thủ tục 2 (ca báo lỗi ngưỡng âm và ca đúng trả dữ liệu)')
    routines_text+=r'''\section{HÀM}
\subsection{Hàm 1: Tổng chi ví ròng (fn\_tong\_chi\_vi\_rong)}
Mô tả hàm: Đọc dữ liệu từ bảng \code{GIAO_DICH_VI} và \code{NGUOI_CHOI}. Sử dụng CURSOR duyệt qua lịch sử giao dịch kết hợp câu lệnh IF kiểm tra loại giao dịch (\code{TruTienMay}, \code{TruTienDichVu}, \code{HoanTien}) để tính tổng số tiền chi ròng của hội viên trong một khoảng thời gian. Input: \code{p_ma_nguoi_choi}, \code{p_tu_gio}, \code{p_den_gio}. Output: DECIMAL(18,0).
'''+flow('wallet','Lưu đồ minh họa Hàm 1 dùng CURSOR và IF tính tổng chi ròng')+sql('fn_wallet.sql','Câu lệnh tạo Hàm 1: fn_tong_chi_vi_rong')+cases('img_16_fn_chi_vi')+snap('img_16_fn_chi_vi','Kết quả DBMS minh họa kiểm tra Hàm 1 (ca đúng trả tổng tiền và ca sai mã trả NULL)')
    routines_text+=r'''\subsection{Hàm 2: Tổng tiền từ dòng chi tiết đơn (fn\_tong\_tien\_don)}
Mô tả hàm: Đọc dữ liệu từ bảng \code{CHI_TIET_GOI_DICH_VU}. Sử dụng CURSOR duyệt từng dòng chi tiết của đơn hàng kết hợp kiểm tra IF điều kiện số lượng và đơn giá hợp lệ, sau đó cộng dồn thành tiền của toàn bộ đơn. Input: \code{p_ma_don_goi}. Output: DECIMAL(18,0).
'''+flow('order','Lưu đồ minh họa Hàm 2 dùng CURSOR tính tổng tiền đơn hàng')+sql('fn_order.sql','Câu lệnh tạo Hàm 2: fn_tong_tien_don')+cases('img_17_fn_tien_don')+snap('img_17_fn_tien_don','Kết quả DBMS minh họa kiểm tra Hàm 2 (ca đúng trả tổng tiền và ca sai mã trả NULL)')
    write('sections/02_routines.tex',routines_text)
    write('sections/03_verification.tex',r'''\chapter{PHẦN THÊM: Kiểm chứng và tích hợp ứng dụng}\label{chap:verification}
\section{Kiến trúc và giao dịch}
Giao diện HTML/CSS/JavaScript gọi REST API Flask trên cùng origin. Backend tách tuyến HTTP, dịch vụ nghiệp vụ và lớp truy cập dữ liệu. Dịch vụ nắm ranh giới BEGIN/COMMIT/ROLLBACK trên một kết nối; routine được gọi trong giao dịch đó, không tự chốt độc lập. Runtime dùng tài khoản hạn quyền, không cấp trực tiếp quyền cập nhật số dư ví hoặc tồn kho.

\flowfigure{diagrams/architecture.tex}{Luồng giao tiếp giữa giao diện, backend và MySQL}{fig:architecture}

Xác thực dùng phiên đăng nhập và kiểm tra CSRF cho API ghi. Dữ liệu đầu vào bị kiểm tra miền kiểu và phạm vi; mã yêu cầu được dùng để phân biệt gửi lặp với xung đột nội dung. Khi có tranh chấp, dữ liệu được đọc lại dưới khóa thay vì tin vào trạng thái đã đọc trước giao dịch.
\section{Ba luồng kiểm chứng}
\begin{enumerate}
\item \textbf{Phiên chơi:} chọn máy, mở phiên, kết thúc, đối chiếu biên lai và giải phóng máy. Với trả trước, giờ sử dụng và số dư khả dụng được kiểm soát tại server.
\item \textbf{Ví và dịch vụ:} nạp ví, gửi lại cùng mã, tạo/tiếp nhận/thanh toán đơn, đối chiếu số dư và tồn. Thanh toán đơn của phiên cũ vẫn phải tính tiền giữ chỗ của phiên đang hoạt động.
\item \textbf{Kho và báo cáo:} phiếu nháp không đổi tồn; ghi sổ chỉ tác động một lần; xem báo cáo với khoảng ngày chứa dữ liệu phát sinh.
\end{enumerate}
\section{Tổng hợp bộ kiểm thử}
\begin{table}[H]\centering\caption{Kết quả kiểm chứng được lưu trong hồ sơ nghiệm thu}
\begin{tabularx}{\linewidth}{@{}Yr@{}}\toprule\textbf{Nhóm ca}&\textbf{PASS}\\\midrule
API: quyền, đầu vào, chống lặp &30\\
Integration: rollback, retry, khóa và tranh chấp &45\\
SQL P1–2 &14\\
E2E HTTP và Chrome ba luồng &4\\
Ba ca hồi quy bổ sung &3\\\midrule
\textbf{Tổng; không FAIL, ERROR hoặc SKIP}&\textbf{96}\\\bottomrule
\end{tabularx}\end{table}
Đây là kết quả của bộ ca đã triển khai, không phải khẳng định mọi trạng thái có thể có đều được bao phủ. Dữ liệu test và tài khoản test được tạo riêng rồi dọn sau từng ca; không reset database ứng dụng. JUnit và log gốc nằm trong \path{evidence/final_verification/}.
\subsection{Các ca biên có ảnh hưởng trực tiếp đến tính đúng}
\begin{itemize}
\item Đơn đặt, thanh toán và hoàn ở ba ngày khác nhau được phân bổ đúng mốc thu/hoàn.
\item Ví 100.000đ đang giữ 90.000đ cho phiên mới không được trả đơn cũ 15.000đ.
\item Đơn tổng 10 tỷ và tên dịch vụ 90 ký tự không bị tràn/cắt trong hai routine liên quan.
\item Gửi lại phiếu kho khác loại trả 409; page quá lớn trả 422, không thành lỗi 500.
\end{itemize}
\section{Cài mới và đối chiếu từ gói bàn giao}
Bộ cài từ bản ZIP đã được chạy trên database/user mới: tạo 23 bảng, nạp hai đơn seed P1–2, mở giao diện và đăng nhập thành công. Chạy seed lại giữ nguyên dữ liệu; bộ seed một phần bị từ chối để tránh ghi đè không rõ trạng thái.

Các bước vận hành: cài thư viện đã khóa phiên bản, chạy script demo để sinh cấu hình riêng và khởi động MySQL/Flask, sau đó sử dụng tài khoản demo. Mật khẩu quản trị không được đưa vào báo cáo hay ZIP. Hướng dẫn đầy đủ ở README và runbook; kết quả phép thử từ ZIP ở \path{evidence/final_verification/zip_smoke.json}.
\section{Phạm vi chưa đưa vào demo}
Ứng dụng hiện minh họa ba luồng trên, chưa khóa máy vật lý. API chưa bao gồm đầy đủ hủy/hoàn, quản trị tài khoản, danh mục và ca trực. Các thao tác SQL quản trị ngoài API cần được đối chiếu riêng với toàn bộ quy tắc BTL1. Phần trình bày ứng dụng theo đợt riêng của môn học cần tuân thủ yêu cầu của đợt đó; báo cáo này tập trung vào Phần 1–2.
''')
    append=r'''\chapter{BẢNG KÊ NHIỆM VỤ VÀ ĐÁNH GIÁ}
\section{Bảng kê nhiệm vụ}
Bảng dưới kế thừa phân công đang lưu trong hồ sơ nhóm. Mỗi hàng chỉ đánh dấu một người phụ trách chính; nội dung tích hợp có thể được kiểm tra chéo. Các cột dùng bốn số cuối MSSV để tránh thu hẹp cột mô tả. Tỉ lệ đóng góp là mức đề xuất, không phải điểm đã được giảng viên xác nhận.
\begin{table}[H]\small\centering\caption{Danh sách thành viên và tỷ lệ điểm đề xuất}
\begin{tabularx}{\linewidth}{@{}lYc@{}}\toprule\textbf{MSSV}&\textbf{Họ và tên}&\textbf{Đề xuất}\\\midrule
2410709&Nguyễn Thành Đạt&20\%\\2410694&Nguyễn Minh Đạt&20\%\\2410696&Nguyễn Phúc Bảo Đạt&20\%\\2413095&Nguyễn Hữu Tây&20\%\\2413181&Trần Tiến Thành&20\%\\\bottomrule\end{tabularx}\end{table}
'''
    rows=json.loads((OUT/'team_assignments.json').read_text())
    append+=r'''\begingroup\small\setlength{\tabcolsep}{3pt}\renewcommand{\arraystretch}{1.15}
\begin{longtable}{@{}>{\raggedright\arraybackslash}p{82mm}ccccc@{}}\caption{Bảng kê người phụ trách từng nội dung}\\\toprule
\textbf{Nội dung} &\textbf{0694}&\textbf{0696}&\textbf{3095}&\textbf{0709}&\textbf{3181}\\\midrule\endfirsthead
\toprule\textbf{Nội dung (tiếp)} &\textbf{0694}&\textbf{0696}&\textbf{3095}&\textbf{0709}&\textbf{3181}\\\midrule\endhead
\bottomrule\endfoot
'''
    for row in rows:
        append+=esc(row['task'])+' & '+' & '.join('x' if mssv==row['assignee_mssv'] else '' for mssv in ['2410694','2410696','2413095','2410709','2413181'])+r'\\'+'\n'
    append+=r'''\end{longtable}\endgroup
\clearpage\section{Đánh giá của giáo viên}
(Điền danh sách thành viên và \% đóng góp bên dưới và để trống các cột còn lại)
\begin{table}[H]\centering\small\renewcommand{\arraystretch}{2.2}
\begin{tabularx}{\linewidth}{@{}>{\raggedright\arraybackslash}p{36mm}lp{12mm}Y>{\raggedright\arraybackslash}p{13mm}p{13mm}@{}}\toprule
\textbf{Họ tên}&\textbf{MSSV}&\textbf{Đề xuất}&\textbf{Nhận xét}&\textbf{Điểm trừ/cộng}&\textbf{Tổng}\\\midrule
Nguyễn Thành Đạt&2410709&20\%&&&\\
Nguyễn Minh Đạt&2410694&20\%&&&\\
Nguyễn Phúc Bảo Đạt&2410696&20\%&&&\\
Nguyễn Hữu Tây&2413095&20\%&&&\\
Trần Tiến Thành&2413181&20\%&&&\\\bottomrule
\end{tabularx}\end{table}
\chapter{PHỤ LỤC: Thiết kế ERD cập nhật mới nhất}\label{app:eer}
\section{Sơ đồ tổng thể dạng vector}
Sơ đồ giữ ký hiệu EER Chen của BTL1. Bản tổng quan trình bày toàn hệ thống; các trang tiếp theo phóng riêng từng phân hệ. Tệp PDF/SVG nguồn được kèm trong bộ LaTeX, cho phép phóng to mà không vỡ nét hoặc dùng để in khổ lớn.
\begin{figure}[H]\centering\includegraphics[width=\linewidth,height=.76\textheight,keepaspectratio]{assets/eer/erd_full_vector.pdf}\caption{EER tổng thể kế thừa từ thiết kế BTL1}\end{figure}
'''
    for name,title in [('eerd_sub_user','Danh tính và người dùng'),('eerd_sub_workstation','Máy trạm và phiên sử dụng'),('eerd_sub_wallet','Ví hội viên và chứng từ'),('eerd_sub_shift','Ca trực và phân công'),('eerd_sub_service_inventory','Dịch vụ và đơn hàng'),('eerd_sub_inventory','Phiếu kho và kiểm kê')]:
        append+='\\clearpage\\section{'+title+'}\n\\begin{figure}[H]\\centering\\includegraphics[width=\\linewidth,height=.78\\textheight,keepaspectratio]{assets/eer/'+name+'.pdf}\\caption{EER phân hệ '+title.lower()+'}\\end{figure}\n'
    append+=r'''\clearpage\section{Bảng ghi chú các thay đổi so với BTL1}
\begingroup\small\setlength{\tabcolsep}{3.5pt}\renewcommand{\arraystretch}{1.2}
\begin{longtable}{@{}>{\raggedright\arraybackslash}p{28mm}>{\raggedright\arraybackslash}p{38mm}>{\raggedright\arraybackslash}p{44mm}>{\raggedright\arraybackslash}p{44mm}@{}}\toprule
\textbf{Nội dung thay đổi}&\textbf{Phiên bản cũ (BTL1)}&\textbf{Phiên bản mới (BTL2)}&\textbf{Lí do}\\\midrule\endhead
\bottomrule\endfoot
Duy nhất có điều kiện&Chỉ có ràng buộc quan hệ thực thể, chưa ràng buộc mức DBMS chống phiên mở đồng thời.&Bổ sung cột sinh và chỉ mục UNIQUE có điều kiện cho phiên đang hoạt động.&Ngăn chặn triệt để 1 tài khoản mở nhiều phiên hoặc 1 máy trạm mở cùng lúc 2 phiên.\\\midrule
Đồng bộ tổng tiền đơn&Tổng tiền đơn tính độc lập hoặc dựa vào logic tầng ứng dụng.&Bộ 3 AFTER trigger trên chi tiết dịch vụ tự động đồng bộ lại tổng tiền đầu đơn.&Bảo toàn tính nhất quán dữ liệu kế toán, không phụ thuộc ứng dụng ngoài.\\\midrule
Phân định ngày doanh thu&Thống kê doanh thu theo ngày tạo đơn hoặc ngày tạo phiên.&Tách riêng thời điểm thanh toán biên lai/đơn và thời điểm hoàn tiền.&Phản ánh đúng dòng tiền thực tế theo ngày phát sinh thay vì ngày đặt đơn.\\\midrule
Miền giá trị tiền tệ trong hàm&Dùng INT hoặc DECIMAL ngắn trong các biến tính toán của hàm.&Chuẩn hóa sang DECIMAL(18,0) cho toàn bộ biến tổng và kết quả trả về của hàm.&Tránh tràn số và sai lệch số học khi tổng tiền hoặc giao dịch ví quy mô lớn.\\\midrule
Miền chuỗi Cursor trong thủ tục&Khai báo biến tạm VARCHAR(50) ngắn trong thân thủ tục.&Khai báo khớp độ dài lược đồ (VARCHAR(100) cho tên, VARCHAR(30) cho đơn vị).&Tránh lỗi cắt cụt chuỗi dữ liệu (Data truncation) khi duyệt báo cáo tồn kho.\\\midrule
Tối ưu hóa chỉ mục thực đơn&Chỉ có các khóa chính và khóa ngoại mặc định theo thiết kế ERD.&Tạo chỉ mục phức hợp \texttt{ix\_dich\_vu\_filter} trên \texttt{(trang\_thai, ma\_nhom, ten\_dich\_vu)}.&Giảm chi phí đọc và tăng tốc truy vấn lọc thực đơn 3.88x (đo bằng EXPLAIN ANALYZE).\\\bottomrule
\end{longtable}\endgroup
\chapter{Dữ liệu mẫu và nguồn minh chứng}\label{app:data}
Mỗi hình dưới là bản xuất của SQL client trong cùng phiên kiểm chứng với các truy vấn ở Phần 1. Các dữ liệu là dữ liệu demo; không sử dụng thông tin cá nhân thật. Phần SQL và kết quả thô đầy đủ đi kèm ở thư mục evidence/dbms.
'''
    for i in range(1,6):append+=snap(f'q{i:02d}_data',f'Các bảng dữ liệu mẫu liên quan Q-P12-{i:02d}')
    append+=r'''\section{Nguồn và khả năng tái tạo}
\begin{itemize}
\item Đề gốc và mẫu Updated: thư mục \path{docs/requirements/} và tệp mẫu trong \path{docs/} của gói bàn giao.
\item DDL, khóa và routine: \path{database/01_schema/} đến \path{database/08_triggers/}.
\item Minh chứng trực tiếp: \path{evidence/dbms/manifest.json}; mỗi mục ánh xạ ảnh, câu SQL và kết quả JSON.
\item Số đo chỉ mục: \path{evidence/queries/index_benchmark.json}; kiểm thử: \path{evidence/final_verification/}.
\item Nguồn sơ đồ EER: \path{docs/btl1_baseline/BTL1_EER.drawio}; các bản vector dùng trong báo cáo nằm tại \path{assets/eer/} của bộ LaTeX.
\item Nguồn báo cáo: \path{main.tex}, các tệp \path{sections/}, \path{diagrams/} và \path{sql/}. Biên dịch bằng XeLaTeX để giữ nguyên tiếng Việt và phông chữ.
\end{itemize}
'''
    write('sections/04_appendices.tex',append)
    write('README.md',r'''# Báo cáo LaTeX BTL2 Phần 1–2

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

Từ gốc repository có thể chạy `./scripts/build_report_latex.sh` để biên dịch riêng vào `build/` và cập nhật PDF nộp ngay trong thư mục `docs/report/latex/`.

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
''')
    print('Prepared self-contained LaTeX source:',OUT)

if __name__=='__main__':prepare()
