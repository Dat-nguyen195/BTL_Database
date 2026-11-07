INSERT INTO DON_GOI_DICH_VU(MaDonHang,ThoiDiemDat,KenhDat,TongTien,TrangThaiPhucVu,TrangThaiThanhToan,SoTienDaHoan) VALUES('DH_EVIDENCE',NOW(),'TaiQuay',0,'MoiDat','ChuaThanhToan',0);
SELECT MaDonHang,TongTien FROM DON_GOI_DICH_VU WHERE MaDonHang='DH_EVIDENCE';
