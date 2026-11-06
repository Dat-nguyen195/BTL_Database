INSERT INTO PHIEN_SU_DUNG(MaPhien,MaMay,MaNguoiChoi,HinhThucDangNhap,ThoiDiemBatDau,ThoiDiemKetThuc,DonGiaGioApDung,TienNapTruoc,TienGiuCho,TongTienTamTinh,TrangThaiPhien) VALUES('P_VALID','M04',NULL,'MienPhi','2026-10-23 10:00:00','2026-10-23 11:00:00',0,0,0,0,'DaKetThuc');
INSERT INTO BIEN_LAI_TIEN_MAY(MaBienLai,MaPhien,ThoiDiemLap,TongTienGio,TienNhan,TienHoan,HinhThucThanhToan,TrangThaiBienLai,MaNhanVienThu) VALUES('BL_REVIEW','P_VALID',NOW(),0,0,0,'MienPhi','ChuaThanhToan','TK03');
UPDATE BIEN_LAI_TIEN_MAY SET TienNhan=1,TienHoan=1 WHERE MaBienLai='BL_REVIEW';
SELECT MaBienLai,TrangThaiBienLai,TienNhan,TienHoan FROM BIEN_LAI_TIEN_MAY WHERE MaBienLai='BL_REVIEW';
DELETE FROM BIEN_LAI_TIEN_MAY WHERE MaBienLai='BL_REVIEW';
SELECT COUNT(*) AS ConLai FROM BIEN_LAI_TIEN_MAY WHERE MaBienLai='BL_REVIEW';
