DELIMITER $$
CREATE PROCEDURE sp_nap_vi(IN pMaGiaoDich VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin,IN pMaYeuCau VARCHAR(100) CHARACTER SET ascii COLLATE ascii_bin,IN pMaNguoiChoi VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin,IN pSoTien DECIMAL(12,0),IN pPhuongThucGD VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin,IN pMaTacNhan VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin,IN pThoiDiem DATETIME)
SQL SECURITY DEFINER
proc: BEGIN
  DECLARE balance DECIMAL(12,0);
  IF NOT fn_co_quyen(pMaTacNhan,'ThuNgan,QuanLy') THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60003,MESSAGE_TEXT='FORBIDDEN'; END IF;
  IF pSoTien<=0 OR pPhuongThucGD NOT IN ('TienMat','ChuyenKhoan') THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60001,MESSAGE_TEXT='INVALID_INPUT'; END IF;
  IF NOT EXISTS(SELECT 1 FROM NGUOI_CHOI WHERE MaTaiKhoan=pMaNguoiChoi) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60002,MESSAGE_TEXT='NOT_FOUND'; END IF;
  SELECT SoDuVi INTO balance FROM NGUOI_CHOI WHERE MaTaiKhoan=pMaNguoiChoi FOR UPDATE;
  IF EXISTS(SELECT 1 FROM GIAO_DICH_VI WHERE MaYeuCau=pMaYeuCau) THEN
    IF NOT EXISTS(SELECT 1 FROM GIAO_DICH_VI WHERE MaYeuCau=pMaYeuCau AND MaGiaoDich=pMaGiaoDich AND MaNguoiChoi=pMaNguoiChoi AND SoTien=pSoTien AND PhuongThucGD=pPhuongThucGD AND MaNhanVienXuLy=pMaTacNhan AND LoaiGiaoDich='NapTien' AND TrangThaiGD='ThanhCong') THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60009,MESSAGE_TEXT='IDEMPOTENCY_CONFLICT'; END IF;
    SELECT pMaGiaoDich AS MaDoiTuong,1 AS DaThucHienTruoc; LEAVE proc;
  END IF;
  IF balance+pSoTien>999999999999 THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60001,MESSAGE_TEXT='INVALID_INPUT'; END IF;
  INSERT INTO GIAO_DICH_VI(MaGiaoDich,MaYeuCau,LoaiGiaoDich,SoTien,ThoiDiemGD,TrangThaiGD,PhuongThucGD,MaNguoiChoi,MaNhanVienXuLy) VALUES(pMaGiaoDich,pMaYeuCau,'NapTien',pSoTien,pThoiDiem,'ThanhCong',pPhuongThucGD,pMaNguoiChoi,pMaTacNhan);
  UPDATE NGUOI_CHOI SET SoDuVi=SoDuVi+pSoTien WHERE MaTaiKhoan=pMaNguoiChoi;
  SELECT pMaGiaoDich AS MaDoiTuong,0 AS DaThucHienTruoc;
END$$
CREATE PROCEDURE sp_tiep_nhan_don(IN pMaDonHang VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin,IN pMaTacNhan VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin,IN pThoiDiem DATETIME)
SQL SECURITY DEFINER
proc: BEGIN
  DECLARE sessionId VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE state VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE ownerId VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin; DECLARE kind VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE started DATETIME; DECLARE price DECIMAL(10,0); DECLARE budget DECIMAL(12,0); DECLARE total DECIMAL(12,0); DECLARE amount DECIMAL(30,0) DEFAULT 0; DECLARE done BOOLEAN DEFAULT FALSE; DECLARE serviceId VARCHAR(10) CHARACTER SET ascii COLLATE ascii_bin; DECLARE qty INT; DECLARE stock INT; DECLARE capturedPrice DECIMAL(10,0); DECLARE countLines INT DEFAULT 0;
  DECLARE items CURSOR FOR SELECT dv.MaDichVu,ct.SoLuong,dv.SoLuongTon,ct.DonGiaBan FROM CHI_TIET_GOI_DICH_VU ct JOIN DICH_VU dv ON dv.MaDichVu=ct.MaDichVu WHERE ct.MaDonHang=pMaDonHang ORDER BY dv.MaDichVu FOR UPDATE;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done=TRUE;
  IF NOT fn_co_quyen(pMaTacNhan,'ThuNgan,PhaChe,QuanLy') THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60003,MESSAGE_TEXT='FORBIDDEN'; END IF;
  IF NOT EXISTS(SELECT 1 FROM DON_GOI_DICH_VU WHERE MaDonHang=pMaDonHang) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60002,MESSAGE_TEXT='NOT_FOUND'; END IF;
  SELECT MaPhien INTO sessionId FROM DON_GOI_DICH_VU WHERE MaDonHang=pMaDonHang;
  IF sessionId IS NOT NULL THEN CALL sp_khoa_phien(sessionId); END IF;
  SELECT TrangThaiPhucVu,TongTien INTO state,total FROM DON_GOI_DICH_VU WHERE MaDonHang=pMaDonHang FOR UPDATE;
  IF state IN ('DaTiepNhan','DangCheBien','DaGiao') THEN SELECT pMaDonHang AS MaDoiTuong,1 AS DaThucHienTruoc; LEAVE proc; END IF;
  IF state<>'MoiDat' THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60008,MESSAGE_TEXT='INVALID_STATE'; END IF;
  IF sessionId IS NOT NULL THEN
    SELECT TrangThaiPhien,MaNguoiChoi,HinhThucDangNhap,ThoiDiemBatDau,DonGiaGioApDung,TienNapTruoc INTO state,ownerId,kind,started,price,budget FROM PHIEN_SU_DUNG WHERE MaPhien=sessionId;
    IF state<>'DangHoatDong' THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60008,MESSAGE_TEXT='INVALID_STATE'; END IF;
    IF ownerId IS NOT NULL THEN SELECT SoDuVi INTO budget FROM NGUOI_CHOI WHERE MaTaiKhoan=ownerId; END IF;
    IF kind='TraTruoc' AND price>0 AND pThoiDiem>=fn_han_phien(started,budget,price) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60014,MESSAGE_TEXT='PREPAID_EXPIRED'; END IF;
  END IF;
  OPEN items;
  item_loop: LOOP
    FETCH items INTO serviceId,qty,stock,capturedPrice;
    IF done THEN LEAVE item_loop; END IF;
    IF stock<qty THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60007,MESSAGE_TEXT='INSUFFICIENT_STOCK'; END IF;
    SET amount=amount+qty*capturedPrice; SET countLines=countLines+1;
    UPDATE DICH_VU SET SoLuongTon=SoLuongTon-qty WHERE MaDichVu=serviceId;
  END LOOP;
  CLOSE items;
  IF countLines=0 OR amount<>total THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60008,MESSAGE_TEXT='INVALID_STATE'; END IF;
  UPDATE DON_GOI_DICH_VU SET TrangThaiPhucVu='DaTiepNhan',MaNhanVienXuLy=pMaTacNhan WHERE MaDonHang=pMaDonHang;
  SELECT pMaDonHang AS MaDoiTuong,0 AS DaThucHienTruoc;
END$$
CREATE PROCEDURE sp_thanh_toan_don(IN pMaDonHang VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin,IN pMaGiaoDich VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin,IN pHinhThucThanhToan VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin,IN pMaTacNhan VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin,IN pThoiDiem DATETIME)
SQL SECURITY DEFINER
proc: BEGIN
  DECLARE sessionId VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE ownerId VARCHAR(15) CHARACTER SET ascii COLLATE ascii_bin; DECLARE state VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE serviceState VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE sessionState VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE oldMethod VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE kind VARCHAR(20) CHARACTER SET ascii COLLATE ascii_bin; DECLARE started DATETIME; DECLARE rate DECIMAL(10,0); DECLARE total DECIMAL(12,0); DECLARE balance DECIMAL(12,0); DECLARE holding DECIMAL(12,0) DEFAULT 0;
  IF pHinhThucThanhToan NOT IN ('TienMat','ChuyenKhoan','TruVi') THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60001,MESSAGE_TEXT='INVALID_INPUT'; END IF;
  IF NOT EXISTS(SELECT 1 FROM DON_GOI_DICH_VU WHERE MaDonHang=pMaDonHang) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60002,MESSAGE_TEXT='NOT_FOUND'; END IF;
  SELECT MaPhien INTO sessionId FROM DON_GOI_DICH_VU WHERE MaDonHang=pMaDonHang;
  IF sessionId IS NOT NULL THEN
    CALL sp_khoa_phien(sessionId);
    SELECT MaNguoiChoi,HinhThucDangNhap,ThoiDiemBatDau,DonGiaGioApDung,TrangThaiPhien INTO ownerId,kind,started,rate,sessionState FROM PHIEN_SU_DUNG WHERE MaPhien=sessionId;
  END IF;
  SELECT TrangThaiThanhToan,TrangThaiPhucVu,HinhThucThanhToan,TongTien INTO state,serviceState,oldMethod,total FROM DON_GOI_DICH_VU WHERE MaDonHang=pMaDonHang FOR UPDATE;
  IF NOT fn_co_quyen(pMaTacNhan,'ThuNgan,QuanLy') AND NOT (pMaTacNhan=ownerId AND pHinhThucThanhToan='TruVi' AND EXISTS(SELECT 1 FROM TAI_KHOAN WHERE MaTaiKhoan=pMaTacNhan AND TrangThai='HoatDong')) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60003,MESSAGE_TEXT='FORBIDDEN'; END IF;
  IF state='DaThanhToan' THEN
    IF oldMethod<>pHinhThucThanhToan THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60009,MESSAGE_TEXT='IDEMPOTENCY_CONFLICT'; END IF;
    SELECT pMaDonHang AS MaDoiTuong,1 AS DaThucHienTruoc; LEAVE proc;
  END IF;
  IF state<>'ChuaThanhToan' OR serviceState NOT IN ('DaTiepNhan','DangCheBien','DaGiao') THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60008,MESSAGE_TEXT='INVALID_STATE'; END IF;
  IF pHinhThucThanhToan='TruVi' THEN
    IF ownerId IS NULL THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60012,MESSAGE_TEXT='INVALID_WALLET_OWNER'; END IF;
    SELECT SoDuVi INTO balance FROM NGUOI_CHOI WHERE MaTaiKhoan=ownerId;
    IF kind='TraTruoc' AND sessionState='DangHoatDong' THEN
      IF rate>0 AND pThoiDiem>=fn_han_phien(started,balance,rate) THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60014,MESSAGE_TEXT='PREPAID_EXPIRED'; END IF;
      SET holding=fn_tien_gio(started,pThoiDiem,rate);
      UPDATE PHIEN_SU_DUNG SET TienGiuCho=holding,TongTienTamTinh=holding WHERE MaPhien=sessionId;
    END IF;
    IF balance-holding<total THEN SIGNAL SQLSTATE '45000' SET MYSQL_ERRNO=60006,MESSAGE_TEXT='INSUFFICIENT_FUNDS'; END IF;
    UPDATE NGUOI_CHOI SET SoDuVi=SoDuVi-total WHERE MaTaiKhoan=ownerId;
    IF total>0 THEN INSERT INTO GIAO_DICH_VI(MaGiaoDich,MaYeuCau,LoaiGiaoDich,SoTien,ThoiDiemGD,TrangThaiGD,PhuongThucGD,MaNguoiChoi,MaDonHang,MaPhien) VALUES(pMaGiaoDich,CONCAT('dv:',pMaDonHang),'TruTienDichVu',total,pThoiDiem,'ThanhCong','NoiBo',ownerId,pMaDonHang,sessionId); END IF;
  END IF;
  UPDATE DON_GOI_DICH_VU SET TrangThaiThanhToan='DaThanhToan',HinhThucThanhToan=pHinhThucThanhToan,ThoiDiemThanhToan=pThoiDiem WHERE MaDonHang=pMaDonHang;
  SELECT pMaDonHang AS MaDoiTuong,0 AS DaThucHienTruoc;
END$$
DELIMITER ;
