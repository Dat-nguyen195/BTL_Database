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
\setsansfont{TeX Gyre Heros}
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
\usepackage[unicode,hypertexnames=false,colorlinks=true,linkcolor=Ink,urlcolor=Accent,citecolor=Accent]{hyperref}
\definecolor{Ink}{HTML}{173453}\definecolor{Accent}{HTML}{007A9D}
\definecolor{Pale}{HTML}{EDF4F8}\definecolor{Edge}{HTML}{8AA6BB}
\definecolor{ErrorInk}{HTML}{923D44}\definecolor{Gold}{HTML}{FFF6DF}
\hypersetup{pdftitle={BTL2 Phần 1 và 2 Hệ thống quản lý quán Net},pdfauthor={L09 Nhóm 10},pdfsubject={GVHD ThS. Trần Thị Quế Nguyệt}}
\renewcommand{\contentsname}{Mục lục}\renewcommand{\listfigurename}{Danh mục hình}
\renewcommand{\figurename}{Hình}\renewcommand{\tablename}{Bảng}\renewcommand{\chaptername}{Phần}
\renewcommand{\bibname}{Tài liệu và nguồn đối chiếu}
\setcounter{tocdepth}{2}\setcounter{secnumdepth}{2}
\setlength{\parindent}{0pt}\setlength{\parskip}{5pt}\linespread{1.08}
\setlength{\emergencystretch}{2em}
\setlist[itemize]{leftmargin=5mm,itemsep=2pt,topsep=3pt}
\setlist[enumerate]{leftmargin=7mm,itemsep=2pt,topsep=3pt}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\small\sffamily HỆ CƠ SỞ DỮ LIỆU | BTL2}
\fancyhead[R]{\small\sffamily L09 — Nhóm 10}\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0.3pt}
\fancypagestyle{plain}{\fancyhf{}\fancyfoot[C]{\small\thepage}\renewcommand{\headrulewidth}{0pt}}
\titleformat{\chapter}[display]{\sffamily\bfseries\color{Ink}}{\large PHẦN \thechapter}{6pt}{\LARGE}
\titlespacing*{\chapter}{0pt}{-10pt}{18pt}
\titleformat{\section}{\sffamily\large\bfseries\color{Ink}}{\thesection}{.7em}{}
\titleformat{\subsection}{\sffamily\normalsize\bfseries\color{Ink}}{\thesubsection}{.7em}{}
\preto\section{\Needspace{10\baselineskip}}
\preto\subsection{\Needspace{6\baselineskip}}
\captionsetup{font=small,labelfont=bf,labelsep=period,skip=7pt}
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}
\newcommand{\code}[1]{\texttt{\detokenize{#1}}}
\newcommand{\sqlinput}[2]{\par\needspace{5\baselineskip}\noindent{\small\sffamily\bfseries\color{Ink}#2}\par\vspace{-2pt}\VerbatimInput[fontsize=\fontsize{8.6}{10.7}\selectfont,breaklines=true,breakanywhere=true,numbers=left,numbersep=5pt,frame=lines,framesep=3mm,rulecolor=\color{Edge},numberblanklines=false]{#1}\par}
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

Các câu SQL trong báo cáo lấy từ bộ mã bàn giao. Ảnh minh chứng là bản xuất trực tiếp của SQL client kết nối MySQL 8.4.13; câu lệnh và đầu ra thô được lưu theo từng lần chạy. Các lưu đồ được dựng bằng TikZ, còn sơ đồ EER được nhúng ở dạng vector để phóng to không vỡ chữ. Câu lệnh và tập kết quả chính được trình bày bằng văn bản/bảng; các hình toàn màn hình giữ vai trò đối chiếu phiên thực thi.
\begin{table}[H]\small\centering\caption{Đối chiếu cấu trúc báo cáo với mẫu Phần 1–2}
\begin{tabularx}{\linewidth}{@{}p{30mm}Yp{31mm}@{}}\toprule
\textbf{Nội dung} & \textbf{Sản phẩm trình bày} & \textbf{Vị trí}\\\midrule
Bảng và ràng buộc & 23 bảng; khóa, miền giá trị và các ca vi phạm & Mục \ref{sec:schema}\\
Chỉ mục & Lý do lựa chọn; kế hoạch và số đo trước/sau & Mục \ref{sec:index}\\
Truy vấn & Năm truy vấn, dữ liệu và kết quả đối chiếu & Mục \ref{sec:queries}\\
SQL nghiệp vụ & CRUD, hai yêu cầu trigger, hai thủ tục và hai hàm & Phần \ref{chap:routines}\\
Kiểm chứng & Ca đúng/sai, hồi quy và ba luồng demo & Phần \ref{chap:verification}\\
Phụ lục & Phân công, EER vector, dữ liệu và nguồn bàn giao & Các phụ lục\\\bottomrule
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
{\sffamily\fontsize{11.5}{15}\selectfont ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH}\\[3mm]
{\sffamily\bfseries\fontsize{15}{19}\selectfont TRƯỜNG ĐẠI HỌC BÁCH KHOA}\\[10mm]
\includegraphics[width=35mm]{assets/logo_bach_khoa.png}\\[11mm]
{\sffamily\color{Ink}\fontsize{14}{18}\selectfont BÁO CÁO BÀI TẬP LỚN SỐ 2}\\[3mm]
{\sffamily\bfseries\fontsize{17}{22}\selectfont HỆ CƠ SỞ DỮ LIỆU}\\[2mm]
{\sffamily\fontsize{11}{14}\selectfont Phần 1 và Phần 2 · Học kỳ 261}\\[10mm]
{\bfseries\color{Ink}\fontsize{26}{32}\selectfont HỆ THỐNG QUẢN LÝ\\QUÁN NET}\\[12mm]
\begin{tabular}{@{}rl@{}}
\textbf{GVHD:}&\textbf{ThS. Trần Thị Quế Nguyệt}\\[3mm]
\textbf{Lớp:}&L09\\[2mm]\textbf{Nhóm:}&10
\end{tabular}\\[10mm]
{\sffamily\bfseries Sinh viên thực hiện}\\[3mm]
\renewcommand{\arraystretch}{1.25}
\begin{tabular}{@{}ll@{}}\toprule
\textbf{Họ và tên} & \textbf{MSSV}\\\midrule
Nguyễn Thành Đạt & 2410709\\
Nguyễn Minh Đạt & 2410694\\
Nguyễn Phúc Bảo Đạt & 2410696\\
Nguyễn Hữu Tây & 2413095\\
Trần Tiến Thành & 2413181\\\bottomrule
\end{tabular}
\vfill
{\sffamily Thành phố Hồ Chí Minh, tháng 11 năm 2026}
\end{center}\end{titlepage}''')
    schema=r'''\chapter{Tạo bảng, dữ liệu mẫu và truy vấn}\label{chap:schema}
\section{Lược đồ vật lý và ràng buộc}\label{sec:schema}
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
    schema+=snap('img_01_dbms_tables','Kiểm đếm các bảng sau khi cài mới trên MySQL')+snap('img_02_dbms_constraints','Khóa ngoại và CHECK từ chối dữ liệu sai; dòng máy ban đầu được giữ nguyên')
    schema+=r'''\section{Chỉ mục và kiểm chứng hiệu năng}\label{sec:index}
\subsection{Chức năng cần tối ưu}
Ở màn hình gọi món tại máy hoặc bán tại quầy, người dùng lọc dịch vụ đang kinh doanh theo nhóm và khoảng giá, sau đó xem giá từ cao xuống thấp. Truy vấn Q-P12-02 vì vậy là cơ sở lựa chọn chỉ mục nhiều cột, không đánh chỉ mục tách rời khỏi nhu cầu sử dụng.
'''+sql('indexes.sql','Bộ chỉ mục của hệ thống')
    schema+=r'''\subsection{Thiết kế phép đo và kết quả}
Phép đo dùng database riêng với 20.000 dòng dịch vụ, 10 nhóm và hai đơn vị tính. Cùng một câu SELECT được chạy 20 lượt trước và sau khi thêm \code{ix_dich_vu_filter}. Cả hai giai đoạn đều lấy hết tập kết quả. Số đo phụ thuộc máy chạy, cache và tải tại thời điểm đo; đây là bằng chứng cho tập dữ liệu cụ thể, không phải cam kết hiệu năng trong mọi môi trường.
'''
    schema+='\\begin{table}[H]\\centering\\caption{Kết quả phép đo Q-P12-02}\\begin{tabularx}{\\linewidth}{@{}Yrr@{}}\\toprule\\textbf{Chỉ tiêu}&\\textbf{Trước}&\\textbf{Sau}\\\\\\midrule\n'
    schema+=f"Trung bình 20 lượt (ms)&{bench['before']['mean_ms']:.3f}&{bench['after']['mean_ms']:.3f}\\\\\nSố dòng kết quả&{bench['before']['rows']}&{bench['after']['rows']}\\\\\nCó bước Sort&{'Có' if bench['before']['has_sort'] else 'Không'}&{'Có' if bench['after']['has_sort'] else 'Không'}\\\\\\bottomrule\\end{{tabularx}}\\end{{table}}\n"
    schema+=f"Tỉ lệ thời gian trước/sau trong lần đo này là \\textbf{{{bench['speedup']:.2f} lần}}. Kế hoạch thực thi dưới đây mới là cơ sở xác định cách MySQL đọc và sắp xếp dữ liệu. Việc tạo chỉ mục không đồng nghĩa MySQL loại bỏ hoàn toàn bước Sort.\n"
    schema+=sql('plan_before.txt','EXPLAIN ANALYZE trước chỉ mục')+sql('plan_after.txt','EXPLAIN ANALYZE sau chỉ mục')
    schema+=snap('index_before','SQL client thực thi EXPLAIN ANALYZE trước chỉ mục')+snap('index_after','SQL client thực thi EXPLAIN ANALYZE sau chỉ mục')
    schema+=r'''\section{Năm truy vấn theo chức năng}\label{sec:queries}
Các truy vấn sử dụng dữ liệu seed P1–2. Q01 và Q02 có SELECT, FROM, WHERE, ORDER BY; Q03 và Q04 bổ sung GROUP BY và hàm tổng hợp; Q05 có hai cấp truy vấn lồng cùng AVG. Các bảng dữ liệu mẫu liên quan được trình bày ở Phụ lục \ref{app:data}.
'''
    query_specs=[
      ('Danh sách máy theo khu vực','Thu ngân kiểm tra các máy có thể sử dụng tại KV01, kèm nhóm và giá giờ. Truy vấn nối MAY_TRAM với KHU_VUC và NHOM_MAY; sắp theo vị trí hàng, cột để phù hợp sơ đồ bố trí máy.',['MaMay','TenMay','TrangThaiMay','TenNhomMay','DonGiaGioMacDinh'],['Mã máy','Tên máy','Trạng thái','Nhóm máy','Giá giờ']),
      ('Lọc thực đơn theo nhóm và giá','Người chơi hoặc thu ngân tìm các dịch vụ đang bán thuộc NDV01, giá từ 10.000 đến 50.000đ. Kết quả có nhóm, đơn vị và tồn; sắp theo giá giảm dần rồi mã dịch vụ để có thứ tự xác định.',['MaDichVu','TenDichVu','TenDonVi','GiaBanHienHanh','SoLuongTon'],['Mã DV','Tên dịch vụ','Đơn vị','Giá bán','Tồn']),
      ('Tổng hợp đơn đã thanh toán','Quản lý thống kê số đơn và tổng tiền theo ngày đặt cùng kênh đặt trong khoảng xét. Đây là phân tích đơn hàng theo ngày đặt; báo cáo thu tiền theo ngày thanh toán được xử lý riêng ở thủ tục doanh thu.',['NgayDat','KenhDat','SoLuongDon','TongTienDonHang'],['Ngày đặt','Kênh đặt','Số đơn','Tổng tiền']),
      ('Số ca và thời lượng trực','Quản lý tổng hợp thời lượng theo nhân viên. Một nhân viên có thể trực nhiều khu trong cùng ca, nên cặp mã nhân viên–mã ca phải được khử trùng trước khi cộng giờ. Với seed sạch, TK03 chỉ có một ca, năm giờ.',['MaNhanVien','TenNhanVien','TongSoCaTruc','TongGioTruc'],['Mã NV','Tên nhân viên','Số ca','Số giờ']),
      ('Hội viên có số dư vượt mức trung bình','Chọn hội viên có số dư cao hơn số dư trung bình của nhóm từng có giao dịch ví thành công trong khoảng xét. Cấp lồng trong lấy tập mã hội viên; cấp ngoài tính AVG. Seed hiện tại trả về TK09, số dư 250.000đ.',['MaHoiVien','TenHoiVien','SoDuVi','NgayDangKy'],['Mã hội viên','Tên hội viên','Số dư ví','Ngày đăng ký'])]
    for i,(title,desc,cols,heads) in enumerate(query_specs,1):
        name=f'img_{i+3:02d}_q{i:02d}';schema+=f'\\subsection{{Q-P12-{i:02d} {title}}}\n{esc(desc)}\n'
        schema+=sql(f'Q-P12-{i:02d}.sql',f'Q-P12-{i:02d} Câu lệnh truy vấn')
        schema+=result_table(name,cols,heads,f'Tập kết quả Q-P12-{i:02d} trên seed P1–2')+snap(name,f'Minh chứng thực thi Q-P12-{i:02d} trên MySQL')
    write('sections/01_schema.tex',schema)
    routines_text=r'''\chapter{Thủ tục, trigger và hàm}\label{chap:routines}
\section{Ba thủ tục INSERT, UPDATE và DELETE}
\subsection{Lựa chọn bảng và nguyên tắc xử lý}
Bảng KHU\_VUC được chọn để minh họa CRUD vì có ý nghĩa quản trị rõ ràng và có tham chiếu từ máy trạm, phân công trực. Thủ tục nhận chuỗi đầu vào đủ rộng để kiểm tra độ dài trước khi ghi xuống cột; thông báo lỗi thể hiện nguyên nhân đầu vào, không tồn tại hoặc còn phụ thuộc. Mỗi thủ tục trả mã khu vực, tên thao tác và số dòng tác động.
'''
    for mode,title,desc,record in [
      ('insert','Thêm khu vực','Đầu vào gồm mã, tên và mô tả vị trí. Tên/mã rỗng hoặc vượt miền bị từ chối; mã đã có trả 60009; tên trùng trả 60001. Nếu hợp lệ, ghi một dòng mới.','img_09_crud_insert'),
      ('update','Cập nhật khu vực','Kiểm tra đầu vào, sự tồn tại của mã và việc tên mới trùng khu khác. Không đổi mã định danh. Mã không tồn tại trả 60002; tên mới sai hoặc trùng trả 60001.','img_10_crud_update'),
      ('delete','Xóa khu vực','Chỉ xóa khu vực tồn tại và không còn máy trạm hoặc phân công trực tham chiếu. Khi còn phụ thuộc, trả 60015 thay vì làm mất dữ liệu liên quan.','img_11_crud_delete')]:
        routines_text+='\\subsection{'+title+'}\n'+desc+'\n'+flow('crud_'+mode,'Lưu đồ thủ tục '+mode.upper()+' khu vực')+sql(mode+'.sql','Định nghĩa thủ tục '+mode.upper())+cases(record)+snap(record,'Ca hợp lệ và ca bị từ chối của thủ tục '+mode.upper())
    routines_text+=snap('routines_created','Các routine đã được tạo trong database kiểm chứng')
    routines_text+=r'''\section{Hai yêu cầu sử dụng trigger}
\subsection{Bảo vệ biên lai đã thanh toán}
Đây là ràng buộc phụ thuộc giá trị cũ của dòng khi xảy ra UPDATE/DELETE, không thể thay thế bằng CHECK chỉ xét giá trị mới. BEFORE trigger kiểm tra trạng thái cũ; biên lai đã thanh toán trả 60011. Biên lai chưa thanh toán vẫn được cập nhật/xóa nếu các ràng buộc khác hợp lệ. Trigger không tự COMMIT và không vô hiệu hóa các khóa ngoại hay CHECK.
'''+flow('receipt','Bảo vệ chứng từ đã thanh toán')+sql('trigger_receipt.sql','Nhóm trigger trên BIEN_LAI_TIEN_MAY')+cases('img_12_trigger_t1')+snap('img_12_trigger_t1','Sửa và xóa biên lai đã thanh toán đều bị từ chối; dữ liệu không đổi')+cases('trigger_t1_valid')+snap('trigger_t1_valid','Cập nhật và xóa biên lai chưa thanh toán hợp lệ')
    routines_text+=r'''\subsection{Đồng bộ tổng tiền đơn từ chi tiết}
Nhóm AFTER trigger trên CHI\_TIET\_GOI\_DICH\_VU cập nhật DON\_GOI\_DICH\_VU: INSERT cộng giá trị mới; UPDATE cộng chênh lệch; DELETE trừ giá trị cũ. Các BEFORE trigger hiện có chặn thay đổi chi tiết của đơn đã chốt và đổi mã đơn. Nhờ vậy, tổng đầu đơn và dòng chi tiết thay đổi trong cùng giao dịch; nếu lỗi, thay đổi bị rollback theo giao dịch của bên gọi.
'''+flow('order_total','Nhóm trigger liên bảng duy trì tổng tiền đơn')+sql('trigger_total.sql','Ba AFTER trigger trên chi tiết đơn')+cases('trigger_t2_before')+snap('trigger_t2_before','Đơn nháp ban đầu có tổng tiền bằng 0')+cases('img_13_trigger_t2')+snap('img_13_trigger_t2','Thêm, sửa, xóa chi tiết làm tổng lần lượt bằng 30.000, 45.000 và 0đ')+cases('trigger_t2_errors')+snap('trigger_t2_errors','INSERT, UPDATE và DELETE bị chặn trên chi tiết đơn đã chốt')+snap('triggers_created','Các trigger trong hai yêu cầu đã được tạo')
    routines_text+=r'''\section{Hai thủ tục tổng hợp dữ liệu}
\subsection{Doanh thu theo ngày}
\code{sp_bao_cao_doanh_thu_ngay} nhận ngày bắt đầu và kết thúc, kiểm tra NULL, thứ tự ngày và giới hạn chênh lệch ngày DATEDIFF không quá 31, sau đó duyệt từng ngày bằng WHILE. Mỗi ngày lấy tiền máy từ biên lai theo thời điểm thanh toán; tiền dịch vụ theo thời điểm thanh toán của đơn; tiền hoàn theo thời điểm hoàn thực tế. Thu ròng bằng thu máy cộng thu dịch vụ trừ hoàn dịch vụ.

Đầu ra là một dòng chứa mảng JSON. Cách tách ba mốc thời gian tránh kéo khoản thu hoặc hoàn về ngày đặt đơn. Các ngày không có phát sinh vẫn có số tổng bằng 0, thuận tiện cho màn hình báo cáo liên tục theo ngày.
'''+flow('revenue','Duyệt khoảng ngày và tổng hợp thu/hoàn theo mốc phát sinh')+sql('report_revenue.sql','Thủ tục báo cáo doanh thu theo ngày')+cases('img_14_sp_doanh_thu')+snap('img_14_sp_doanh_thu','Khoảng ngày ngược bị từ chối; khoảng hợp lệ trả số thu từng ngày')
    routines_text+=r'''\subsection{Báo cáo tồn và phân loại dịch vụ}
\code{sp_bao_cao_ton_dich_vu} nhận nhóm dịch vụ (có thể bỏ trống để xét toàn bộ) và ngưỡng tồn không âm. CURSOR đọc dữ liệu nối từ DICH\_VU, NHOM\_DICH\_VU và DON\_VI\_TINH. Mỗi dòng được phân loại: tồn bằng 0 là HetHang; tồn dương không quá ngưỡng là SapHet; còn lại là DuHang. Dữ liệu được gom vào JSON và trả sau khi đóng cursor.

Biến đọc tên dịch vụ dài 100 ký tự và đơn vị dài 30 ký tự, khớp miền cột gốc. Đây là điều kiện cần để dữ liệu hợp lệ ở bảng không bị cắt khi đọc qua cursor.
'''+flow('stock','CURSOR đọc dịch vụ và phân loại theo ngưỡng tồn')+sql('report_stock.sql','Thủ tục báo cáo tồn dịch vụ')+cases('img_15_sp_ton_kho')+snap('img_15_sp_ton_kho','Ngưỡng âm bị từ chối; dữ liệu nhóm NDV02 thể hiện đủ ba mức tồn')
    routines_text+=r'''\section{Hai hàm đọc và xử lý dữ liệu}
\subsection{Tổng chi ví ròng}
\code{fn_tong_chi_vi_rong} nhận mã người chơi và khoảng thời gian nửa mở từ giờ bắt đầu (bao gồm) đến giờ kết thúc (không gồm). Hàm trả NULL nếu hội viên không tồn tại hoặc khoảng thời gian không hợp lệ. CURSOR chỉ lấy giao dịch thành công; cộng TruTienMay/TruTienDichVu, trừ HoanTien và bỏ qua NapTien. Khi không có giao dịch phù hợp, tổng khởi tạo bằng 0 được giữ nguyên.

Giá trị cộng dồn và kiểu trả về là DECIMAL(18,0), phù hợp tiền VND nguyên và rộng hơn miền một giao dịch riêng lẻ. Dấu của kết quả phản ánh chênh lệch chi và hoàn trong khoảng, không phải số dư ví hiện tại.
'''+flow('wallet','Tính tổng chi ròng theo loại giao dịch ví')+sql('fn_wallet.sql','Hàm tổng chi ví ròng')+cases('img_16_fn_chi_vi')+snap('img_16_fn_chi_vi','Hàm tổng chi trả 15.000đ cho TK02; mã không tồn tại trả NULL')
    routines_text+=r'''\subsection{Tổng tiền từ dòng chi tiết đơn}
\code{fn_tong_tien_don} trả NULL nếu đơn không tồn tại. Nếu tồn tại, CURSOR duyệt từng dòng, kiểm tra số lượng và đơn giá, rồi cộng tích của hai giá trị. Hàm dùng DECIMAL(18,0) để không làm hẹp miền tổng tiền đã được schema cho phép. Hàm có thể dùng để đối chiếu giá trị đầu đơn với tổng các chi tiết; việc duy trì tổng tự động vẫn do trigger đảm nhiệm.
'''+flow('order','Cộng dồn số lượng nhân đơn giá của từng dòng chi tiết')+sql('fn_order.sql','Hàm tổng tiền đơn hàng')+cases('img_17_fn_tien_don')+snap('img_17_fn_tien_don','Tổng đơn DH_P12_01 là 52.000đ; mã không tồn tại trả NULL')
    write('sections/02_routines.tex',routines_text)
    write('sections/03_verification.tex',r'''\chapter{Kiểm chứng và tích hợp ứng dụng}\label{chap:verification}
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
    append=r'''\chapter{Bảng kê nhiệm vụ và đánh giá}
\section{Phân công theo sản phẩm}
Bảng dưới kế thừa phân công đang lưu trong hồ sơ nhóm. Mỗi hàng chỉ đánh dấu một người phụ trách chính; nội dung tích hợp có thể được kiểm tra chéo. Các cột dùng bốn số cuối MSSV để tránh thu hẹp cột mô tả. Tỉ lệ đóng góp là mức đề xuất, không phải điểm đã được giảng viên xác nhận.
\begin{table}[H]\small\centering\caption{Danh sách thành viên và cột phân công}
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
\clearpage\section{Đánh giá của giảng viên}
Các cột nhận xét, điều chỉnh và tổng điểm để trống cho giảng viên.
\begin{table}[H]\centering\small\renewcommand{\arraystretch}{2.2}
\begin{tabularx}{\linewidth}{@{}>{\raggedright\arraybackslash}p{36mm}lp{12mm}Y>{\raggedright\arraybackslash}p{13mm}p{13mm}@{}}\toprule
\textbf{Họ tên}&\textbf{MSSV}&\textbf{Đề xuất}&\textbf{Nhận xét}&\textbf{Điểm trừ/cộng}&\textbf{Tổng}\\\midrule
Nguyễn Thành Đạt&2410709&20\%&&&\\
Nguyễn Minh Đạt&2410694&20\%&&&\\
Nguyễn Phúc Bảo Đạt&2410696&20\%&&&\\
Nguyễn Hữu Tây&2413095&20\%&&&\\
Trần Tiến Thành&2413181&20\%&&&\\\bottomrule
\end{tabularx}\end{table}
\chapter{Sơ đồ EER và thay đổi so với BTL1}\label{app:eer}
\section{Sơ đồ tổng thể dạng vector}
Sơ đồ giữ ký hiệu EER Chen của BTL1. Bản tổng quan trình bày toàn hệ thống; các trang tiếp theo phóng riêng từng phân hệ. Tệp PDF/SVG nguồn được kèm trong bộ LaTeX, cho phép phóng to mà không vỡ nét hoặc dùng để in khổ lớn.
\begin{figure}[H]\centering\includegraphics[width=\linewidth,height=.76\textheight,keepaspectratio]{assets/eer/erd_full_vector.pdf}\caption{EER tổng thể kế thừa từ thiết kế BTL1}\end{figure}
'''
    for name,title in [('eerd_sub_user','Danh tính và người dùng'),('eerd_sub_workstation','Máy trạm và phiên sử dụng'),('eerd_sub_wallet','Ví hội viên và chứng từ'),('eerd_sub_shift','Ca trực và phân công'),('eerd_sub_service_inventory','Dịch vụ và đơn hàng'),('eerd_sub_inventory','Phiếu kho và kiểm kê')]:
        append+='\\clearpage\\section{'+title+'}\n\\begin{figure}[H]\\centering\\includegraphics[width=\\linewidth,height=.78\\textheight,keepaspectratio]{assets/eer/'+name+'.pdf}\\caption{EER phân hệ '+title.lower()+'}\\end{figure}\n'
    append+=r'''\clearpage\section{Các thay đổi khi hiện thực}
\begin{longtable}{@{}>{\raggedright\arraybackslash}p{32mm}>{\raggedright\arraybackslash}p{49mm}>{\raggedright\arraybackslash}p{63mm}@{}}\toprule\textbf{Nội dung}&\textbf{Hiện thực BTL2}&\textbf{Lý do}\\\midrule\endhead
Duy nhất có điều kiện&Cột sinh và UNIQUE cho phiên đang hoạt động&Ngăn hai phiên đồng thời trên cùng máy/hội viên.\\
Tổng tiền đơn&Ba AFTER trigger từ chi tiết&Giữ tổng đầu đơn nhất quán khi INSERT/UPDATE/DELETE.\\
Ngày doanh thu&Tách thời điểm thanh toán và hoàn&Không phân bổ thu/hoàn về ngày đặt đơn.\\
Miền tiền trong hàm&DECIMAL(18,0) cho biến tổng và kết quả&Không thu hẹp miền tổng tiền hợp lệ ở bảng.\\
Miền chuỗi cursor&Đọc đúng 100 ký tự tên dịch vụ và 30 ký tự đơn vị&Tránh cắt dữ liệu hợp lệ khi tạo báo cáo.\\
Chỉ mục thực đơn&Chỉ mục kết hợp theo Q-P12-02&Giảm chi phí đọc; hiệu quả được đo theo kế hoạch thực thi.\\\bottomrule
\end{longtable}
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
''')
    print('Prepared self-contained LaTeX source:',OUT)

if __name__=='__main__':prepare()
