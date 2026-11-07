CALL sp_khu_vuc_delete('KV01');
CALL sp_khu_vuc_delete('KV99');
SELECT COUNT(*) AS ConLai FROM KHU_VUC WHERE MaKhuVuc='KV99';
