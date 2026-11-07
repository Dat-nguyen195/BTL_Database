"""Script chạy kiểm tra và xuất kết quả các câu truy vấn và bảng dữ liệu dạng bảng đẹp mắt."""
import json
import os
from pathlib import Path
import sys
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'apps/backend'))
sys.path.insert(0, str(ROOT / 'scripts'))

from src.db import get_db_connection
from submission_queries import queries


def print_table(title, columns, rows):
    """In dữ liệu dưới dạng bảng ASCII trực quan."""
    print("=" * 80)
    print(f"📊 {title}")
    print("=" * 80)
    if not rows:
        print("(Không có dòng dữ liệu nào)")
        print()
        return

    # Tính độ rộng cột tối ưu
    widths = [
        max(len(str(col)), max((len(str(row[i] if row[i] is not None else 'NULL')) for row in rows), default=0))
        for i, col in enumerate(columns)
    ]
    header = " | ".join(str(col).ljust(widths[i]) for i, col in enumerate(columns))
    separator = "-+-".join("-" * widths[i] for i in range(len(columns)))

    print(header)
    print(separator)
    for row in rows:
        formatted_row = [str(val if val is not None else 'NULL').ljust(widths[i]) for i, val in enumerate(row)]
        print(" | ".join(formatted_row))
    print(f"👉 Tổng số dòng: {len(rows)}\n")


def show_summary_tables(conn):
    """Thống kê 23 bảng và số dòng hiện tại trong CSDL."""
    cur = conn.cursor()
    cur.execute("SHOW TABLES;")
    tables = [r[0] for r in cur.fetchall()]
    table_stats = []
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM `{t}`;")
        count = cur.fetchone()[0]
        table_stats.append((t, count))
    print_table("TỔNG HỢP 23 BẢNG CƠ SỞ DỮ LIỆU & SỐ DÒNG HIỆN CÓ", ["Tên Bảng", "Số Dòng (Rows)"], table_stats)
    cur.close()


def show_submission_queries(conn):
    """Chạy 5 câu truy vấn Q01 - Q05 trong đề bài và xuất dạng bảng."""
    cur = conn.cursor()
    q_dict = queries()
    descriptions = {
        "Q-P12-01": "Danh sách máy trạm theo khu vực KV01 (màn hình sơ đồ máy)",
        "Q-P12-02": "Lọc thực đơn món ăn giá 10k - 50k (màn hình gọi món)",
        "Q-P12-03": "Thống kê tổng tiền đơn hàng đã thanh toán theo ngày và kênh",
        "Q-P12-04": "Tổng số ca và thời lượng trực của nhân viên (khử trùng ca)",
        "Q-P12-05": "Hội viên có số dư ví lớn hơn trung bình (lồng 2 cấp)",
    }
    for q_code, sql in q_dict.items():
        desc = descriptions.get(q_code, "")
        title = f"{q_code}: {desc}"
        cur.execute(sql)
        cols = list(cur.column_names)
        rows = cur.fetchall()
        print_table(title, cols, rows)
    cur.close()


def show_reports(conn):
    """Gọi thử các thủ tục báo cáo P1-2."""
    cur = conn.cursor()
    print("=" * 80)
    print("📈 THỦ TỤC: sp_bao_cao_ton_dich_vu(pMaNhomDV = NULL, pNguongTon = 35)")
    print("=" * 80)
    cur.callproc("sp_bao_cao_ton_dich_vu", [None, 35])
    for result in cur.stored_results():
        raw_json = result.fetchone()[0]
        items = json.loads(raw_json)
        if items:
            cols = ["MaDichVu", "TenDichVu", "TenNhomDV", "GiaBanHienHanh", "SoLuongTon", "PhanLoaiTon"]
            rows = [[item.get(c) for c in cols] for item in items]
            print_table("KẾT QUẢ PHÂN LOẠI TỒN KHO DỊCH VỤ", cols, rows)
        else:
            print("(Không có dữ liệu)")

    print("=" * 80)
    print("📈 THỦ TỤC: sp_bao_cao_doanh_thu_ngay(2026-10-01, 2026-10-31)")
    print("=" * 80)
    cur.callproc("sp_bao_cao_doanh_thu_ngay", ["2026-10-01", "2026-10-31"])
    for result in cur.stored_results():
        raw_json = result.fetchone()[0]
        items = json.loads(raw_json)
        # Chỉ in các ngày có phát sinh doanh thu > 0 để bảng gọn gàng
        active_items = [it for it in items if (it.get("ThuMay", 0) > 0 or it.get("ThuDichVu", 0) > 0)]
        if active_items:
            cols = ["Ngay", "ThuMay", "ThuDichVu", "HoanDichVu", "TongThucThu"]
            rows = [[item.get(c) for c in cols] for item in active_items]
            print_table("CÁC NGÀY PHÁT SINH DOANH THU TRONG THÁNG 10/2026", cols, rows)
        else:
            print("(Chưa có ngày nào phát sinh doanh thu)")
    cur.close()


def show_custom_table(conn, table_name):
    """In toàn bộ dữ liệu của một bảng cụ thể."""
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM `{table_name}` LIMIT 50;")
    cols = list(cur.column_names)
    rows = cur.fetchall()
    print_table(f"DỮ LIỆU BẢNG: {table_name}", cols, rows)
    cur.close()


if __name__ == "__main__":
    conn = get_db_connection()
    try:
        # Nếu truyền tên bảng (ví dụ: python test_show_tables.py MAY_TRAM)
        if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
            table_name = sys.argv[1].upper()
            show_custom_table(conn, table_name)
        else:
            print("\n" + "#" * 80)
            print("  KIỂM TRA & XUẤT BẢNG KẾT QUẢ TRUY VẤN CSDL BTL2 (HỆ THỐNG QUÁN NET)")
            print("#" * 80 + "\n")
            
            # 1. Hiển thị thống kê 23 bảng
            show_summary_tables(conn)
            
            # 2. Hiển thị 5 truy vấn nộp bài Q01 - Q05
            show_submission_queries(conn)
            
            # 3. Hiển thị kết quả thủ tục báo cáo
            show_reports(conn)
            
    finally:
        conn.close()
