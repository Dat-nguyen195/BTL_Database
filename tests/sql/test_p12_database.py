"""Kiểm tra toàn bộ các đối tượng CSDL P1-2: Truy vấn, CRUD, Trigger, Thủ tục, Hàm."""
import json
from pathlib import Path
import pytest
import mysql.connector
from bootstrap_backend import sql_statements


@pytest.fixture(autouse=True)
def seed_p12_data(db_conn):
    """Nạp dữ liệu mẫu P1-2 phục vụ riêng cho các ca kiểm thử P1-2."""
    seed_file = Path(__file__).resolve().parents[2] / 'database/04_seed/03_p12_demo_seed.sql'
    cur = db_conn.cursor()
    for stmt in sql_statements(seed_file.read_text()):
        cur.execute(stmt)
    cur.close()


def test_q_p12_01_workstations(db_conn):
    """Q-P12-01: Máy theo khu vực, nhóm và trạng thái."""
    cur = db_conn.cursor(dictionary=True)
    sql = """
        SELECT
            m.`MaMay`,
            m.`TenMay`,
            m.`TrangThaiMay`,
            k.`TenKhuVuc`,
            nm.`TenNhomMay`,
            nm.`DonGiaGioMacDinh`,
            m.`ViTriHang`,
            m.`ViTriCot`
        FROM `MAY_TRAM` m
        JOIN `KHU_VUC` k ON m.`MaKhuVuc` = k.`MaKhuVuc`
        JOIN `NHOM_MAY` nm ON m.`MaNhomMay` = nm.`MaNhomMay`
        WHERE m.`TrangThaiMay` IN ('AVAILABLE', 'ONLINE')
          AND k.`MaKhuVuc` = 'KV01'
        ORDER BY m.`ViTriHang` ASC, m.`ViTriCot` ASC;
    """
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    assert len(rows) >= 2
    for r in rows:
        assert r["TrangThaiMay"] in ("AVAILABLE", "ONLINE")


def test_q_p12_02_services(db_conn):
    """Q-P12-02: Dịch vụ đang bán theo nhóm và khoảng giá."""
    cur = db_conn.cursor(dictionary=True)
    sql = """
        SELECT
            d.`MaDichVu`,
            d.`TenDichVu`,
            ndv.`TenNhomDV`,
            dvt.`TenDonVi`,
            d.`GiaBanHienHanh`,
            d.`SoLuongTon`
        FROM `DICH_VU` d
        JOIN `NHOM_DICH_VU` ndv ON d.`MaNhomDV` = ndv.`MaNhomDV`
        JOIN `DON_VI_TINH` dvt ON d.`MaDonVi` = dvt.`MaDonVi`
        WHERE d.`TrangThaiKinhDoanh` = 'DangKinhDoanh'
          AND d.`MaNhomDV` = 'NDV01'
          AND d.`GiaBanHienHanh` BETWEEN 10000 AND 50000
        ORDER BY d.`GiaBanHienHanh` DESC, d.`MaDichVu` ASC;
    """
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    assert len(rows) >= 2
    for r in rows:
        assert 10000 <= r["GiaBanHienHanh"] <= 50000


def test_q_p12_03_orders_aggregate(db_conn):
    """Q-P12-03: Thống kê tổng tiền đơn hàng đã thanh toán theo ngày và kênh."""
    cur = db_conn.cursor(dictionary=True)
    sql = """
        SELECT
            DATE(d.`ThoiDiemDat`) AS `NgayDat`,
            d.`KenhDat`,
            COUNT(d.`MaDonHang`) AS `SoLuongDon`,
            SUM(d.`TongTien`) AS `TongTienDonHang`
        FROM `DON_GOI_DICH_VU` d
        WHERE d.`TrangThaiThanhToan` = 'DaThanhToan'
          AND d.`ThoiDiemDat` >= '2026-10-01 00:00:00'
          AND d.`ThoiDiemDat` <= '2026-11-30 23:59:59'
        GROUP BY DATE(d.`ThoiDiemDat`), d.`KenhDat`
        ORDER BY `NgayDat` DESC, `TongTienDonHang` DESC;
    """
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    assert len(rows) >= 2
    total_revenue = sum(r["TongTienDonHang"] for r in rows)
    assert total_revenue == 102000  # 52000 (DH_P12_01) + 50000 (DH_P12_02)


def test_q_p12_04_shifts_deduplication(db_conn):
    """Q-P12-04: Tổng ca và thời lượng trực khử trùng nhân viên - ca."""
    cur = db_conn.cursor(dictionary=True)
    sql = """
        SELECT
            nv.`MaTaiKhoan` AS `MaNhanVien`,
            tk.`Ten` AS `TenNhanVien`,
            nv.`ChucVu`,
            COUNT(DISTINCT pc.`MaCa`) AS `TongSoCaTruc`,
            ROUND(SUM(TIMESTAMPDIFF(MINUTE, ca.`ThoiDiemBatDau`, ca.`ThoiDiemKetThuc`)) / 60.0, 2) AS `TongGioTruc`
        FROM `NHAN_VIEN` nv
        JOIN `TAI_KHOAN` tk ON nv.`MaTaiKhoan` = tk.`MaTaiKhoan`
        JOIN (
            SELECT DISTINCT `MaNhanVien`, `MaCa`
            FROM `PHAN_CONG_TRUC`
        ) pc ON nv.`MaTaiKhoan` = pc.`MaNhanVien`
        JOIN `CA_TRUC` ca ON pc.`MaCa` = ca.`MaCa`
        WHERE ca.`ThoiDiemBatDau` >= '2026-10-01 00:00:00'
          AND ca.`ThoiDiemKetThuc` <= '2026-11-30 23:59:59'
        GROUP BY nv.`MaTaiKhoan`, tk.`Ten`, nv.`ChucVu`
        ORDER BY `TongGioTruc` DESC, `TongSoCaTruc` DESC;
    """
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    assert len(rows) >= 2
    # TK03 có 2 phân công ở CA01 nhưng phải được tính là 1 ca (5 giờ)
    tk03_row = next((r for r in rows if r["MaNhanVien"] == "TK03"), None)
    assert tk03_row is not None
    assert tk03_row["TongSoCaTruc"] == 1
    assert float(tk03_row["TongGioTruc"]) == 5.0


def test_q_p12_05_nested_player_balance(db_conn):
    """Q-P12-05: Hai cấp truy vấn lồng hội viên có số dư > trung bình hội viên có GD ví thành công."""
    cur = db_conn.cursor(dictionary=True)
    sql = """
        SELECT
            nc.`MaTaiKhoan` AS `MaHoiVien`,
            tk.`Ten` AS `TenHoiVien`,
            nc.`SoCCCD`,
            nc.`SoDuVi`,
            nc.`NgayDangKy`
        FROM `NGUOI_CHOI` nc
        JOIN `TAI_KHOAN` tk ON nc.`MaTaiKhoan` = tk.`MaTaiKhoan`
        WHERE nc.`SoDuVi` > (
            SELECT AVG(sub_nc.`SoDuVi`)
            FROM `NGUOI_CHOI` sub_nc
            WHERE sub_nc.`MaTaiKhoan` IN (
                SELECT DISTINCT gd.`MaNguoiChoi`
                FROM `GIAO_DICH_VI` gd
                WHERE gd.`TrangThaiGD` = 'ThanhCong'
                  AND gd.`ThoiDiemGD` >= '2026-10-01 00:00:00'
                  AND gd.`ThoiDiemGD` <= '2026-11-30 23:59:59'
            )
        )
        ORDER BY nc.`SoDuVi` DESC, nc.`MaTaiKhoan` ASC;
    """
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    # Nhóm có GD ví: TK02 (100k) và TK09 (250k) -> AVG = 175k.
    # Người chơi có SoDuVi > 175k là TK09 (250k).
    assert len(rows) >= 1
    assert rows[0]["MaHoiVien"] == "TK09"


def test_crud_khu_vuc(db_conn):
    """Kiểm thử ba thủ tục INSERT / UPDATE / DELETE trên KHU_VUC."""
    cur = db_conn.cursor(dictionary=True)

    # 1. INSERT hợp lệ
    cur.callproc("sp_khu_vuc_insert", ("KV99", "Khu Thi Đấu Esports", "Tầng 2 cánh trái"))
    result = next(cur.stored_results()).fetchall()[0]
    assert result["MaKhuVuc"] == "KV99"
    assert result["ThaoTac"] == "INSERT"
    assert result["SoDongTacDong"] == 1

    # 2. INSERT trùng mã bị bắt lỗi IDEMPOTENCY_CONFLICT
    with pytest.raises(mysql.connector.Error) as exc:
        cur.callproc("sp_khu_vuc_insert", ("KV99", "Khu Khác", "Mô tả"))
    assert exc.value.errno == 60009

    # 3. INSERT trùng tên bị bắt lỗi INVALID_INPUT
    with pytest.raises(mysql.connector.Error) as exc:
        cur.callproc("sp_khu_vuc_insert", ("KV98", "Khu Thi Đấu Esports", "Mô tả"))
    assert exc.value.errno == 60001

    # 4. UPDATE hợp lệ
    cur.callproc("sp_khu_vuc_update", ("KV99", "Khu Thi Đấu Pro", "Tầng 2 trung tâm"))
    result = next(cur.stored_results()).fetchall()[0]
    assert result["MaKhuVuc"] == "KV99"
    assert result["ThaoTac"] == "UPDATE"
    assert result["SoDongTacDong"] == 1

    # 5. UPDATE không tồn tại bị bắt NOT_FOUND
    with pytest.raises(mysql.connector.Error) as exc:
        cur.callproc("sp_khu_vuc_update", ("KV_NONE", "Tên mới", "Mô tả"))
    assert exc.value.errno == 60002

    # 5b. INSERT mã quá dài (> 10 ký tự) bị bắt INVALID_INPUT
    with pytest.raises(mysql.connector.Error) as exc:
        cur.callproc("sp_khu_vuc_insert", ("KV_TOOLONG_CODE", "Tên", "Mô tả"))
    assert exc.value.errno == 60001

    # 6. DELETE bị chặn khi có khóa ngoại tham chiếu (KV01 có máy trạm)
    with pytest.raises(mysql.connector.Error) as exc:
        cur.callproc("sp_khu_vuc_delete", ("KV01",))
    assert exc.value.errno == 60015

    # 7. DELETE hợp lệ trên khu vực không bị tham chiếu
    cur.callproc("sp_khu_vuc_delete", ("KV99",))
    result = next(cur.stored_results()).fetchall()[0]
    assert result["MaKhuVuc"] == "KV99"
    assert result["ThaoTac"] == "DELETE"
    assert result["SoDongTacDong"] == 1
    cur.close()


def test_trigger_t_p12_01_protect_receipt(db_conn):
    """T-P12-01: Chặn sửa/xóa biên lai đã thanh toán (DaThanhToan)."""
    cur = db_conn.cursor()

    # UPDATE biên lai đã chốt bị từ chối
    with pytest.raises(mysql.connector.Error) as exc:
        cur.execute("UPDATE BIEN_LAI_TIEN_MAY SET TongTienGio = 99999 WHERE MaBienLai = 'BL_P12_01'")
    assert exc.value.errno == 60011

    # DELETE biên lai đã chốt bị từ chối
    with pytest.raises(mysql.connector.Error) as exc:
        cur.execute("DELETE FROM BIEN_LAI_TIEN_MAY WHERE MaBienLai = 'BL_P12_01'")
    assert exc.value.errno == 60011
    cur.close()


def test_trigger_t_p12_02_order_total_maintenance(db_conn):
    """T-P12-02: Duy trì tổng tiền đơn hàng khi thêm, sửa, xóa dòng chi tiết ở trạng thái nháp."""
    cur = db_conn.cursor(dictionary=True)

    # 1. Tạo đơn hàng mới ở trạng thái nháp với TongTien = 0
    cur.execute("""
        INSERT INTO DON_GOI_DICH_VU (MaDonHang, ThoiDiemDat, KenhDat, MaPhien, TongTien, TrangThaiPhucVu, TrangThaiThanhToan, SoTienDaHoan)
        VALUES ('DH_TEST_TR', NOW(), 'TaiQuay', NULL, 0, 'MoiDat', 'ChuaThanhToan', 0)
    """)

    # 2. INSERT dòng 1: DV01 (giá 15.000, số lượng 2) -> Tổng phải tăng lên 30.000
    cur.execute("INSERT INTO CHI_TIET_GOI_DICH_VU (MaDonHang, MaDichVu, SoLuong, DonGiaBan) VALUES ('DH_TEST_TR', 'DV01', 2, 15000)")
    cur.execute("SELECT TongTien FROM DON_GOI_DICH_VU WHERE MaDonHang = 'DH_TEST_TR'")
    assert cur.fetchone()["TongTien"] == 30000

    # 3. INSERT dòng 2: DV02 (giá 12.000, số lượng 1) -> Tổng phải tăng lên 42.000
    cur.execute("INSERT INTO CHI_TIET_GOI_DICH_VU (MaDonHang, MaDichVu, SoLuong, DonGiaBan) VALUES ('DH_TEST_TR', 'DV02', 1, 12000)")
    cur.execute("SELECT TongTien FROM DON_GOI_DICH_VU WHERE MaDonHang = 'DH_TEST_TR'")
    assert cur.fetchone()["TongTien"] == 42000

    # 4. UPDATE dòng 1: tăng số lượng từ 2 lên 3 -> Chênh lệch +15.000 -> Tổng lên 57.000
    cur.execute("UPDATE CHI_TIET_GOI_DICH_VU SET SoLuong = 3 WHERE MaDonHang = 'DH_TEST_TR' AND MaDichVu = 'DV01'")
    cur.execute("SELECT TongTien FROM DON_GOI_DICH_VU WHERE MaDonHang = 'DH_TEST_TR'")
    assert cur.fetchone()["TongTien"] == 57000

    # 5. DELETE dòng 2: bớt 12.000 -> Tổng còn 45.000
    cur.execute("DELETE FROM CHI_TIET_GOI_DICH_VU WHERE MaDonHang = 'DH_TEST_TR' AND MaDichVu = 'DV02'")
    cur.execute("SELECT TongTien FROM DON_GOI_DICH_VU WHERE MaDonHang = 'DH_TEST_TR'")
    assert cur.fetchone()["TongTien"] == 45000

    cur.close()


def test_procedures_p12_reports(db_conn):
    """Kiểm thử hai thủ tục báo cáo có điều kiện và vòng lặp."""
    cur = db_conn.cursor()

    # 1. sp_bao_cao_doanh_thu_ngay
    cur.callproc("sp_bao_cao_doanh_thu_ngay", ("2026-10-20", "2026-10-21"))
    res = next(cur.stored_results()).fetchall()[0][0]
    data = json.loads(res)
    assert len(data) == 2
    # Ngày 2026-10-20: Thu máy 15.000, thu dịch vụ 52.000 -> Doanh thu ròng 67.000
    d20 = next(d for d in data if d["Ngay"] == "2026-10-20")
    assert d20["ThuTienMay"] == 15000
    assert d20["ThuDichVu"] == 52000
    assert d20["DoanhThuRong"] == 67000

    # Lỗi khoảng ngày ngược nhau
    with pytest.raises(mysql.connector.Error) as exc:
        cur.callproc("sp_bao_cao_doanh_thu_ngay", ("2026-10-25", "2026-10-20"))
    assert exc.value.errno == 60001

    # 2. sp_bao_cao_ton_dich_vu
    cur.callproc("sp_bao_cao_ton_dich_vu", ("NDV02", 10))
    res2 = next(cur.stored_results()).fetchall()[0][0]
    data2 = json.loads(res2)
    assert len(data2) >= 3
    # DV04 có tồn 8 (<=10) -> SapHet
    dv04 = next(d for d in data2 if d["MaDichVu"] == "DV04")
    assert dv04["PhanLoaiTon"] == "SapHet"
    # DV05 có tồn 0 -> HetHang
    dv05 = next(d for d in data2 if d["MaDichVu"] == "DV05")
    assert dv05["PhanLoaiTon"] == "HetHang"
    # DV02 có tồn 100 (>10) -> DuHang
    dv02 = next(d for d in data2 if d["MaDichVu"] == "DV02")
    assert dv02["PhanLoaiTon"] == "DuHang"

    cur.close()


def test_functions_p12(db_conn):
    """Kiểm thử hai hàm fn_tong_chi_vi_rong và fn_tong_tien_don."""
    cur = db_conn.cursor(dictionary=True)

    # 1. fn_tong_chi_vi_rong: TK02 có GD_P12_02 (TruTienMay 15.000). Nạp tiền 50k không tính vào chi tiêu.
    cur.execute("SELECT fn_tong_chi_vi_rong('TK02', '2026-10-01 00:00:00', '2026-10-31 23:59:59') AS TongChi")
    res = cur.fetchone()["TongChi"]
    assert float(res) == 15000.00

    # Hội viên không tồn tại trả về NULL
    cur.execute("SELECT fn_tong_chi_vi_rong('TK_NONEXIST', '2026-10-01 00:00:00', '2026-10-31 23:59:59') AS TongChi")
    assert cur.fetchone()["TongChi"] is None

    # 2. fn_tong_tien_don: DH_P12_01 có 3 món (15k + 12k + 25k = 52.000)
    cur.execute("SELECT fn_tong_tien_don('DH_P12_01') AS TongTien")
    res2 = cur.fetchone()["TongTien"]
    assert float(res2) == 52000.00

    # Đơn không tồn tại trả về NULL
    cur.execute("SELECT fn_tong_tien_don('DH_NONEXIST') AS TongTien")
    assert cur.fetchone()["TongTien"] is None

    cur.close()


def test_revenue_report_date_separation(db_conn):
    """Kiểm tra doanh thu dịch vụ phân bổ đúng theo ThoiDiemThanhToan và ThoiDiemHoanTien."""
    cur = db_conn.cursor()
    # Tạo đơn hàng đặt ngày 20/10, thanh toán ngày 21/10, hoàn tiền ngày 22/10
    cur.execute("""
        INSERT INTO DON_GOI_DICH_VU (
            MaDonHang, ThoiDiemDat, KenhDat, MaPhien, MaNhanVienXuLy,
            TongTien, TrangThaiPhucVu, TrangThaiThanhToan, HinhThucThanhToan,
            ThoiDiemThanhToan, SoTienDaHoan, ThoiDiemHoanTien
        ) VALUES (
            'DH_TEST_DATES', '2026-10-20 10:00:00', 'TaiQuay', NULL, 'TK03',
            15000, 'DaGiao', 'DaHoanTien', 'TienMat',
            '2026-10-21 11:00:00', 15000, '2026-10-22 14:00:00'
        )
    """)
    cur.callproc("sp_bao_cao_doanh_thu_ngay", ["2026-10-20", "2026-10-22"])
    raw = next(cur.stored_results()).fetchall()[0][0]
    days = json.loads(raw) if isinstance(raw, str) else raw

    d20 = next(d for d in days if d["Ngay"] == "2026-10-20")
    d21 = next(d for d in days if d["Ngay"] == "2026-10-21")
    d22 = next(d for d in days if d["Ngay"] == "2026-10-22")

    # Ngày 20: chỉ đặt đơn DH_TEST_DATES, chưa thanh toán (chỉ tính 52.000 của DH_P12_01 thanh toán ngày 20)
    assert d20["ThuDichVu"] == 52000
    assert d20["HoanDichVu"] == 0
    # Ngày 21: thời điểm thanh toán -> gồm 50.000 của DH_P12_02 + 15.000 của DH_TEST_DATES = 65.000
    assert d21["ThuDichVu"] == 65000
    assert d21["HoanDichVu"] == 0
    # Ngày 22: thời điểm hoàn tiền -> ThuDichVu=0, HoanDichVu=15000
    assert d22["ThuDichVu"] == 0
    assert d22["HoanDichVu"] == 15000
    cur.close()


def test_functions_p12_large_amounts(db_conn):
    """Kiểm tra fn_tong_tien_don không bị tràn số với số tiền lớn (10 tỷ VND)."""
    cur = db_conn.cursor(dictionary=True)
    cur.execute("""
        INSERT INTO DON_GOI_DICH_VU (
            MaDonHang, ThoiDiemDat, KenhDat, MaPhien, MaNhanVienXuLy,
            TongTien, TrangThaiPhucVu, TrangThaiThanhToan, HinhThucThanhToan
        ) VALUES (
            'DH_10TY', '2026-10-25 10:00:00', 'TaiQuay', NULL, 'TK03',
            0, 'MoiDat', 'ChuaThanhToan', NULL
        )
    """)
    # 2 món mỗi món 5 tỷ
    cur.execute("INSERT INTO CHI_TIET_GOI_DICH_VU (MaDonHang, MaDichVu, SoLuong, DonGiaBan) VALUES ('DH_10TY', 'DV01', 1, 5000000000)")
    cur.execute("INSERT INTO CHI_TIET_GOI_DICH_VU (MaDonHang, MaDichVu, SoLuong, DonGiaBan) VALUES ('DH_10TY', 'DV02', 1, 5000000000)")

    cur.execute("SELECT fn_tong_tien_don('DH_10TY') AS TongTien")
    res = cur.fetchone()["TongTien"]
    assert int(res) == 10000000000
    cur.close()


def test_sp_bao_cao_ton_dich_vu_long_name(db_conn):
    """Kiểm tra sp_bao_cao_ton_dich_vu với tên dịch vụ dài 90 ký tự không bị lỗi 1265."""
    cur = db_conn.cursor()
    long_name = "A" * 90
    cur.execute("""
        INSERT INTO DICH_VU (
            MaDichVu, TenDichVu, GiaBanHienHanh, SoLuongTon,
            TrangThaiKinhDoanh, MaNhomDV, MaDonVi
        ) VALUES (
            'DV_LONG90', %s, 20000, 5, 'DangKinhDoanh', 'NDV01', 'DVT01'
        )
    """, (long_name,))

    cur.callproc("sp_bao_cao_ton_dich_vu", ["NDV01", 10])
    raw = next(cur.stored_results()).fetchall()[0][0]
    items = json.loads(raw) if isinstance(raw, str) else raw
    item = next((d for d in items if d["MaDichVu"] == "DV_LONG90"), None)
    assert item is not None
    assert item["TenDichVu"] == long_name
    assert item["PhanLoaiTon"] == "SapHet"
    cur.close()


def test_sp_thanh_toan_don_active_session_holding(db_conn):
    """Kiểm tra thanh toán đơn phiên cũ bị từ chối khi phiên mới đang giữ chỗ ví."""
    cur = db_conn.cursor(dictionary=True)
    # TK02 có số dư ví 100.000đ
    cur.execute("UPDATE NGUOI_CHOI SET SoDuVi = 100000 WHERE MaTaiKhoan = 'TK02'")

    # Phiên cũ đã kết thúc của TK02 trên M01
    cur.execute("""
        INSERT INTO PHIEN_SU_DUNG (
            MaPhien, MaMay, MaNguoiChoi, HinhThucDangNhap, TienNapTruoc,
            ThoiDiemBatDau, ThoiDiemKetThuc, DonGiaGioApDung, TrangThaiPhien, TienGiuCho, TongTienTamTinh
        ) VALUES (
            'PH_OLD_CLOSED', 'M01', 'TK02', 'TraSau', 0,
            '2026-10-25 06:00:00', '2026-10-25 07:00:00', 10000, 'DaKetThuc', 0, 10000
        )
    """)

    # Phiên mới đang hoạt động của TK02 trên M02 từ 2 tiếng trước, đơn giá 45.000đ/h -> giữ chỗ 90.000đ
    cur.execute("""
        INSERT INTO PHIEN_SU_DUNG (
            MaPhien, MaMay, MaNguoiChoi, HinhThucDangNhap, TienNapTruoc,
            ThoiDiemBatDau, DonGiaGioApDung, TrangThaiPhien, TienGiuCho, TongTienTamTinh
        ) VALUES (
            'PH_NEW_ACTIVE', 'M02', 'TK02', 'TraTruoc', 0,
            '2026-10-25 08:00:00', 45000, 'DangHoatDong', 90000, 90000
        )
    """)
    # Đơn hàng cũ gắn với phiên cũ PH_OLD_CLOSED trị giá 15.000đ (khả dụng 100k - 90k = 10k < 15k)
    cur.execute("""
        INSERT INTO DON_GOI_DICH_VU (
            MaDonHang, ThoiDiemDat, KenhDat, MaPhien, MaNhanVienXuLy,
            TongTien, TrangThaiPhucVu, TrangThaiThanhToan, HinhThucThanhToan
        ) VALUES (
            'DH_OLD_SESSION', '2026-10-25 06:30:00', 'TaiMay', 'PH_OLD_CLOSED', 'TK03',
            15000, 'DaTiepNhan', 'ChuaThanhToan', NULL
        )
    """)

    # Gọi thanh toán đơn bằng TruVi tại thời điểm 2026-10-25 10:00:00 (sau 2 tiếng)
    # Mong đợi lỗi 60006 INSUFFICIENT_FUNDS
    threw_insufficient = False
    try:
        cur.execute("""
            CALL sp_thanh_toan_don(
                'DH_OLD_SESSION', 'GD_TEST_HOLD', 'TruVi', 'TK02', '2026-10-25 10:00:00'
            )
        """)
    except mysql.connector.Error as err:
        if err.errno == 60006 or "INSUFFICIENT_FUNDS" in str(err):
            threw_insufficient = True
        else:
            raise

    assert threw_insufficient, "Phải từ chối thanh toán với lỗi INSUFFICIENT_FUNDS khi số dư khả dụng sau giữ chỗ không đủ"
    # Số dư ví phải được giữ nguyên 100.000đ
    cur.execute("SELECT SoDuVi FROM NGUOI_CHOI WHERE MaTaiKhoan = 'TK02'")
    assert cur.fetchone()["SoDuVi"] == 100000
    cur.close()
