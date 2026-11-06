CALL sp_khu_vuc_update('KV99','Khu Demo Mới','Tầng 3');
CALL sp_khu_vuc_update('KV_NONE','Không có','');
SELECT * FROM KHU_VUC WHERE MaKhuVuc='KV99';
